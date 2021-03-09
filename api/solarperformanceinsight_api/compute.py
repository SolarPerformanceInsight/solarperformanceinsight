import calendar
from copy import deepcopy
import datetime as dt
from functools import partial
import json
import logging
from typing import Callable, Generator, Union, List, Tuple, Optional
from uuid import UUID


from fastapi import HTTPException
import pandas as pd
from pvlib.modelchain import (  # type: ignore
    ModelChainResult,
    ModelChain,
    _irrad_for_celltemp,
)


from . import storage, models, utils
from .pvmodeling import construct_modelchains


logger = logging.getLogger(__name__)


def run_job(job_id: UUID, user: str):
    si = storage.StorageInterface(user=user)
    try:
        with si.start_transaction() as st:
            job = st.get_job(job_id)
    except HTTPException as err:
        if err.status_code == 404:
            # job doesn't exist or can't be fetched, so no point continuing
            return
        else:  # pragma: no cover
            raise

    job_func = lookup_job_compute_function(job)
    try:
        job_func(job, si)
    except Exception as err:
        logger.exception("Error for job %s", job_id)
        try:
            details = str(err.args[0])
        except IndexError:
            details = f"Raised {type(err)}"
        msg = json.dumps({"error": {"details": details}})
        with si.start_transaction() as st:
            st.add_job_result(job_id, "/", "error message", "application/json", msg)
            st.set_job_error(job_id)


def lookup_job_compute_function(
    job: models.StoredJob,
) -> Callable[[models.StoredJob, storage.StorageInterface], None]:
    if isinstance(job.definition.parameters, models.CalculatePerformanceJobParameters):
        return run_performance_job
    elif isinstance(
        job.definition.parameters, models.CompareExpectedActualJobParameters
    ):
        return compare_expected_and_actual
    elif isinstance(
        job.definition.parameters, models.ComparePredictedActualJobParameters
    ):
        return compare_predicted_and_actual
    return dummy_func


def dummy_func(job, storage):  # pragma: no cover
    raise NotImplementedError("Job computation not implemented")


def _get_data(
    job_id: UUID, data_id: UUID, si: storage.StorageInterface
) -> pd.DataFrame:
    """Get the data from the database."""
    with si.start_transaction() as st:
        meta, data = st.get_job_data(job_id, data_id)
    if meta.definition.data_format != "application/vnd.apache.arrow.file":
        raise TypeError(
            f"Data for /jobs/{job_id}/data/{data_id} not in Apache Arrow format"
        )
    return utils.read_arrow(data).set_index("time")  # type: ignore


def generate_job_weather_data(
    job: models.StoredJob,
    si: storage.StorageInterface,
    types=(
        models.JobDataTypeEnum.original_weather,
        models.JobDataTypeEnum.actual_weather,
    ),
    weather_granularity=None,
) -> Generator[List[pd.DataFrame], None, None]:
    """Generator to fetch job data at the inverter level to run a
    ModelChain.  Iterates over each inverter in the system and returns a
    list of weather dataframes for the arrays associated with that
    inverter.
    """
    data_id_by_schema_path = {
        do.definition.schema_path: do.object_id
        for do in job.data_objects
        if do.definition.type in types
    }
    job_id = job.object_id
    num_inverters = len(job.definition.system_definition.inverters)
    if weather_granularity is None:
        weather_granularity = getattr(job.definition.parameters, "weather_granularity")

    if weather_granularity == models.WeatherGranularityEnum.system:
        data_id = data_id_by_schema_path["/"]
        df = _get_data(job_id, data_id, si)
        for i in range(num_inverters):
            num_arrays = len(job.definition.system_definition.inverters[i].arrays)
            yield [df.copy()] * num_arrays
    elif weather_granularity == models.WeatherGranularityEnum.inverter:
        for i in range(num_inverters):
            num_arrays = len(job.definition.system_definition.inverters[i].arrays)
            data_id = data_id_by_schema_path[f"/inverters/{i}"]
            df = _get_data(job_id, data_id, si)
            yield [df] * num_arrays
    elif weather_granularity == models.WeatherGranularityEnum.array:
        for i in range(num_inverters):
            num_arrays = len(job.definition.system_definition.inverters[i].arrays)
            data_ids = [
                data_id_by_schema_path[f"/inverters/{i}/arrays/{j}"]
                for j in range(num_arrays)
            ]
            yield [_get_data(job_id, data_id, si) for data_id in data_ids]
    else:
        raise ValueError(f"Unknown weather granularity {weather_granularity}")


def generate_job_performance_data(
    job: models.StoredJob,
    si: storage.StorageInterface,
    types: List[models.JobDataTypeEnum],
    performance_granularity: Optional[models.PerformanceGranularityEnum] = None,
) -> Generator[Union[pd.DataFrame, None], None, None]:
    """Generator to fetch job performance data at the inverter level."""
    data_id_by_schema_path = {
        do.definition.schema_path: do.object_id
        for do in job.data_objects
        if do.definition.type in types
    }
    job_id = job.object_id
    num_inverters = len(job.definition.system_definition.inverters)
    if performance_granularity is None:
        performance_granularity = getattr(
            job.definition.parameters, "performance_granularity"
        )

    if len(data_id_by_schema_path) == 0:
        for _ in range(num_inverters):
            yield None
    elif performance_granularity == models.PerformanceGranularityEnum.system:
        data_id = data_id_by_schema_path["/"]
        df = _get_data(job_id, data_id, si)
        for i in range(num_inverters):
            yield df.copy()
    elif performance_granularity == models.PerformanceGranularityEnum.inverter:
        for i in range(num_inverters):
            data_id = data_id_by_schema_path[f"/inverters/{i}"]
            df = _get_data(job_id, data_id, si)
            yield df
    else:
        raise ValueError(f"Unknown performance granularity {performance_granularity}")


class DBResult(models.JobResultMetadata):
    data_format: str = "application/vnd.apache.arrow.file"
    data: bytes  # feather format

    def __init__(self, **kwargs):
        kwargs["data"] = utils.dump_arrow_bytes(
            utils.convert_to_arrow(kwargs.pop("data").reset_index())
        )
        super().__init__(**kwargs)

    def __repr__(self):  # pragma: no cover
        return f"DBResult(schema_path='{self.schema_path}', type='{self.type}', data=<{len(self.data)} bytes>)"  # NOQA


def save_results_to_db(
    job_id: UUID, result_list: List[DBResult], si: storage.StorageInterface
):
    with si.start_transaction() as st:
        for result in result_list:
            st.add_job_result(
                job_id, result.schema_path, result.type, result.data_format, result.data
            )
        st.set_job_complete(job_id)


def _adjust_frame(
    inp: Union[pd.Series, pd.DataFrame],
    tshift: dt.timedelta,
    name: Optional[str] = None,
) -> Union[pd.Series, pd.DataFrame]:
    """Shift the object by -tshift and make sure index is named "time" """
    if not isinstance(inp, (pd.Series, pd.DataFrame)):
        raise TypeError(f"Expected pandas.Series or pandas.DataFrame not {type(inp)}")

    if not isinstance(inp.index, pd.DatetimeIndex):  # type: ignore
        raise TypeError("Expected input to have a DatetimeIndex")

    out = inp.shift(freq=-tshift)  # type: ignore
    out.index.name = "time"  # type: ignore
    if isinstance(out, pd.Series):
        out.name = name  # type: ignore
    return out


def _get_index(
    result: ModelChainResult, prop: str, index: int
) -> Union[pd.DataFrame, pd.Series]:
    # handle possible issues when only one array with results not being
    # a tuple until pvlib#1139 is resolved
    val = getattr(result, prop)
    if isinstance(val, (tuple, list)):
        out = val[index]
        if isinstance(out, (pd.DataFrame, pd.Series)):
            return out
        else:  # issue described in pvlib/pvlib-python#1139
            # nans for now
            return pd.Series(
                None, index=result.ac.index, dtype=float, name=prop
            )  # type: ignore
    elif isinstance(val, (pd.DataFrame, pd.Series)):
        return val
    else:
        raise TypeError(f"Unknown result format {type(val)}")


def process_single_modelchain(
    chain: ModelChain,
    weather_data: List[pd.DataFrame],
    run_model_method: str,
    tshift: dt.timedelta,
    inverter_num: int,
) -> Tuple[List[DBResult], pd.DataFrame]:
    """Run and process a single ModelChain

    Parameters
    ----------
    chain : pvlib.modelchain.ModelChain
        The chain to run
    weather_data : List[pandas.DataFrame]
        The data that will be passed to chain.run_model
    run_model_method : str
        The method of chain to used calculate results, i.e. run_model,
        run_model_from_poa, run_model_from_effective_irradiance
    tshift : dt.timedelta
        Amount by which to shift weather data before running the chain.
        Typically half the interval length.
    inverter_num : int
        Which inverter in the full system this chain is for

    Returns
    -------
    inverter_results : List[DBResult]
        List of DBResult objects that can be inserted into the database
        including AC performance for each inverter and weather (poa_global,
        effective_irradiance, cell_temperature) for each array
    summary_frame : pd.DataFrame
        A frame with the AC performance result, zenith angle, and average of
        poa_global, effective_irradiance, and cell_temperature over all arrays
    """
    # run chain
    mc = getattr(chain, run_model_method)(
        [d.shift(freq=tshift) for d in weather_data]  # type: ignore
    )
    results = mc.results
    adjust = partial(_adjust_frame, tshift=tshift)
    performance: pd.DataFrame = adjust(
        results.ac, name="performance"
    ).to_frame()  # type: ignore
    weather_sum = pd.DataFrame(
        {
            "effective_irradiance": 0,  # type: ignore
            "poa_global": 0,  # type: ignore
            "cell_temperature": 0,  # type: ignore
        },
        index=performance.index,
    )

    # make nice result output
    num_arrays = len(mc.system.arrays)
    out = []
    for i in range(num_arrays):
        array_weather: pd.DataFrame = _get_index(
            results, "effective_irradiance", i
        ).to_frame(
            "effective_irradiance"
        )  # type: ignore
        # total irrad empty if effective irradiance supplied initially
        array_weather.loc[:, "poa_global"] = _get_index(
            results, "total_irrad", i
        ).get(  # type: ignore
            "poa_global", float("NaN")
        )
        array_weather.loc[:, "cell_temperature"] = _get_index(
            results, "cell_temperature", i
        )  # type: ignore
        array_weather = adjust(array_weather)  # type: ignore
        weather_sum += array_weather  # type: ignore
        out.append(
            DBResult(
                schema_path=f"/inverters/{inverter_num}/arrays/{i}",
                type="weather data",
                data=array_weather,
            )
        )
    # mean
    weather_avg: pd.DataFrame = weather_sum / num_arrays  # type: ignore
    adjusted_zenith: pd.DataFrame
    # not calculated if effective irradiance is provided
    if results.solar_position is not None:
        adjusted_zenith = adjust(results.solar_position[["zenith"]])  # type: ignore
    else:
        # calculate solar position making sure to shift times and shift back
        # modelchain passes through air temperature and pressure, but that only
        # affects apparent_zenith
        adjusted_zenith = adjust(
            mc.location.get_solarposition(
                weather_avg.index.shift(freq=tshift)  # type: ignore
            )[["zenith"]]
        )  # type: ignore
    summary_frame = pd.concat(
        [
            performance,
            weather_avg,
            adjusted_zenith,
        ],
        axis=1,
    )
    summary_frame.index.name = "time"  # type: ignore
    out.append(
        DBResult(
            schema_path=f"/inverters/{inverter_num}",
            type="performance data",
            data=performance,
        )
    )
    return out, summary_frame


def _calculate_performance(
    job: models.StoredJob, si: storage.StorageInterface
) -> Tuple[pd.Series, List[DBResult]]:
    """Compute the performance, and other modeling variables, for the Job and
    store the inverter level performance, total system performance, array level weather,
    and a monthly summary to the database for retrieval
    """
    time_params: models.JobTimeindex = (
        job.definition.parameters.time_parameters  # type: ignore
    )
    job_time_range = time_params._time_range
    summary = pd.DataFrame(
        {
            "performance": 0,  # type: ignore
            "poa_global": 0,  # type: ignore
            "effective_irradiance": 0,  # type: ignore
            "cell_temperature": 0,  # type: ignore
            "zenith": 0,  # type: ignore
        },
        index=job_time_range,
    )
    summary.index.name = "time"  # type: ignore
    run_model_method: str = job.definition._model_chain_method  # type: ignore
    # compute solar position at the middle of the interval
    # positive value assumes left (beginning) label convention
    tshift = time_params.step / 2
    chains = construct_modelchains(job.definition.system_definition)

    weather_count = 0
    # result from each inverter...
    result_list = []
    # get weather data for each inverter as List[pd.DataFrame] to pass
    # directly to the appropriate ModelChain run function for multiple arrays
    # Weather data is shifted right by half the interval length and
    # process_single_modelchain shifts the results back to original labels
    # so that solar position used for modeling is midpoint of interval
    for i, weather_data in enumerate(generate_job_weather_data(job, si)):
        db_results, array_summary = process_single_modelchain(
            chains[i], weather_data, run_model_method, tshift, i
        )
        result_list += db_results
        summary += array_summary  # type: ignore
        weather_count += 1
    # keep performance as sum, but make everything else average over inverters
    total_performance = summary.pop("performance")  # type: ignore
    # summary up to now is sum of array-averaged weather for each inverter
    summary /= weather_count  # type: ignore
    # summary is now average over inverters
    # average zenith
    daytime = summary.pop("zenith") < 87.0  # type: ignore
    daytime.name = "daytime_flag"  # type: ignore
    # index of data actually uploaded
    input_data_range = daytime.dropna().index
    # months in output according to job time range
    months = job_time_range.month.unique().sort_values()  # type: ignore

    # cell temp will be averaged over a month
    daytime_cell_temp = summary.pop("cell_temperature").loc[daytime]  # type: ignore
    avg_cell_temp = (
        daytime_cell_temp.groupby(daytime_cell_temp.index.month).mean().reindex(months)
    )
    # resample rest of summary for insolation
    # only use data from input range
    insolation = summary.loc[input_data_range].resample("1h").mean()
    month_summary = (
        insolation.groupby(insolation.index.month)
        .sum()
        .reindex(months)
        .rename(
            columns={
                "poa_global": "plane_of_array_insolation",
                "effective_irradiance": "effective_insolation",
            }
        )
    )  # Wh/m^2
    ac_energy = total_performance.loc[input_data_range].resample("1h").mean()
    monthly_energy = (
        ac_energy.groupby(ac_energy.index.month).sum().reindex(months)
    )  # Wh
    month_summary.insert(0, "total_energy", monthly_energy)
    month_summary.insert(
        len(month_summary.columns), "average_daytime_cell_temperature", avg_cell_temp
    )
    month_name_index = pd.Index([calendar.month_name[i] for i in months], name="month")
    month_summary.index = month_name_index

    result_list.extend(
        [
            DBResult(schema_path="/", type="monthly summary", data=month_summary),
            DBResult(
                schema_path="/",
                type="daytime flag",
                data=daytime.to_frame(),
            ),
            DBResult(
                schema_path="/",
                type="performance data",
                data=total_performance.to_frame(),
            ),
        ]
    )
    return monthly_energy, result_list


def run_performance_job(job: models.StoredJob, si: storage.StorageInterface):
    montlhy_energy, result_list = _calculate_performance(job, si)
    save_results_to_db(job.object_id, result_list, si)


def _get_actual_monthly_energy(job: models.StoredJob, si: storage.StorageInterface):
    # performance granularity validation means there won't be system level
    # perfromance and inverter level that you wouldn't want to sum
    performance_data_ids = [
        do.object_id
        for do in job.data_objects
        if do.definition.type == models.JobDataTypeEnum.actual_performance
    ]
    months = (
        (job.definition.parameters.time_parameters._time_range)  # type: ignore
        .month.unique()  # type: ignore
        .sort_values()
    )
    actual_performance = sum(
        _get_data(job.object_id, did, si) for did in performance_data_ids
    )[
        "performance"
    ]  # type: ignore
    actual_energy = actual_performance.resample("1h").mean()  # type: ignore
    actual_monthly_energy = (
        actual_energy.groupby(actual_energy.index.month).sum().reindex(months)
    )
    return actual_monthly_energy, months


def compare_expected_and_actual(job: models.StoredJob, si: storage.StorageInterface):
    expected, result_list = _calculate_performance(job, si)
    actual_monthly_energy, months = _get_actual_monthly_energy(job, si)
    diff = actual_monthly_energy - expected
    ratio = actual_monthly_energy / expected
    comparison_summary = pd.DataFrame(
        {
            "actual_energy": actual_monthly_energy,
            "expected_energy": expected,
            "difference": diff,
            "ratio": ratio,
        }
    )
    month_name_index = pd.Index([calendar.month_name[i] for i in months], name="month")
    comparison_summary.index = month_name_index
    result_list.append(
        DBResult(
            schema_path="/", type="actual vs expected energy", data=comparison_summary
        )
    )
    save_results_to_db(job.object_id, result_list, si)


def _temp_factor(gamma, t_ref, t_actual):
    t0 = 25.0
    return (1 - gamma * (t_actual - t0)) / (1 - gamma * (t_ref - t0))


def _get_mc_dc(mcresult: ModelChainResult, num_arrays: int) -> pd.DataFrame:
    test = _get_index(mcresult, "dc", 0)
    if isinstance(test, pd.DataFrame):
        out = sum([_get_index(mcresult, "dc", i)["p_mp"] for i in range(num_arrays)])
    else:
        out = sum([_get_index(mcresult, "dc", i) for i in range(num_arrays)])
    return pd.DataFrame({"performance": out})  # type: ignore


def _calculate_weather_adjusted_predicted_performance(
    job: models.StoredJob, si: storage.StorageInterface
) -> Tuple[List[DBResult], pd.Series]:
    job_params: models.ComparePredictedActualJobParameters = (
        job.definition.parameters  # type: ignore
    )
    time_params: models.JobTimeindex = job_params.time_parameters  # type: ignore
    job_time_range = time_params._time_range
    total_ref_pac = pd.Series(  # type: ignore
        0,
        index=job_time_range,  # type: ignore
        name="performance",
    )
    total_ref_pac.index.name = "time"  # type: ignore
    data_available = job_params.predicted_data_parameters.data_available
    tshift = time_params.step / 2
    adjust = partial(_adjust_frame, tshift=tshift)
    ref_model_method = job_params.predicted_data_parameters._model_chain_method
    actual_model_method = job_params.actual_data_parameters._model_chain_method

    chains = construct_modelchains(job.definition.system_definition)
    ref_weather_gen = generate_job_weather_data(
        job,
        si,
        types=(models.JobDataTypeEnum.original_weather,),
        weather_granularity=job_params.predicted_data_parameters.weather_granularity,
    )
    actual_weather_gen = generate_job_weather_data(
        job,
        si,
        types=(models.JobDataTypeEnum.actual_weather,),
        weather_granularity=job_params.actual_data_parameters.weather_granularity,
    )
    ref_pac_gen = generate_job_performance_data(
        job,
        si,
        types=[models.JobDataTypeEnum.predicted_performance],
        performance_granularity=(
            job_params.predicted_data_parameters.performance_granularity
        ),
    )
    ref_pdc_gen = generate_job_performance_data(
        job,
        si,
        types=[models.JobDataTypeEnum.predicted_performance_dc],
        performance_granularity=(
            job_params.predicted_data_parameters.performance_granularity
        ),
    )
    # fail if pvsyst modules
    results_list = []
    for i, (chain, ref_weather, actual_weather, ref_pac, ref_pdc,) in enumerate(
        zip(
            chains,
            ref_weather_gen,
            actual_weather_gen,
            ref_pac_gen,
            ref_pdc_gen,
        )
    ):
        # use the ModelChain for temperature etc and since it sets class
        # properties, copy for the actuals calculations
        chain_actual = deepcopy(chain)
        pac0 = job.definition.system_definition.inverters[i].inverter_parameters._pac0
        num_arrays = len(chain.system.arrays)
        gammas = [
            arr._gamma for arr in job.definition.system_definition.inverters[i].arrays
        ]
        if data_available == models.PredictedDataEnum.weather_only:
            db_results, _ = process_single_modelchain(
                chain, ref_weather, ref_model_method, tshift, i
            )
            results_list += db_results
            ref_pdc = adjust(_get_mc_dc(chain.results, num_arrays))  # type: ignore
        else:
            # run chain on ref weather
            getattr(chain, ref_model_method)(
                [d.shift(freq=tshift) for d in ref_weather]  # type: ignore
            )

        # run chain on actual weather
        getattr(chain_actual, actual_model_method)(
            [d.shift(freq=tshift) for d in actual_weather]  # type: ignore
        )
        poa_ref = _irrad_for_celltemp(
            chain.results.total_irrad, chain.results.effective_irradiance
        )
        poa_actual = _irrad_for_celltemp(
            chain_actual.results.total_irrad, chain_actual.results.effective_irradiance
        )
        t_ref = chain.results.cell_temperature
        t_actual = chain_actual.results.cell_temperature
        # mean of array POArat * TempFactor for this inverter
        # could make more sense to use weighted mean with weights set
        # by array power percentage

        poa_rat = [pa / pr for pa, pr in zip(poa_actual, poa_ref)]
        tempfactor = list(map(_temp_factor, gammas, t_ref, t_actual))
        poa_rat_x_temp_factor = adjust(
            sum([p * t for p, t in zip(poa_rat, tempfactor)]) / num_arrays
        )

        if ref_pdc is not None:
            pdc_ref_adj = ref_pdc.mul(poa_rat_x_temp_factor, axis=0)  # type: ignore
            pac_ref_adj = pdc_ref_adj * 0.985
        else:
            pac_ref_adj = ref_pac.mul(poa_rat_x_temp_factor, axis=0)  # type: ignore
        pac_adj = pac_ref_adj.clip(upper=pac0)  # type: ignore
        pac_adj.index.name = "time"
        total_ref_pac += pac_adj["performance"]
        results_list.append(
            DBResult(
                schema_path=f"/inverters/{i}",
                type="weather adjusted performance",
                data=pac_adj,
            )
        )
    return results_list, total_ref_pac


def compare_predicted_and_actual(job: models.StoredJob, si: storage.StorageInterface):
    results_list, total_ref_pac = _calculate_weather_adjusted_predicted_performance(
        job, si
    )
    actual_monthly_energy, months = _get_actual_monthly_energy(job, si)
    ref_energy = total_ref_pac.resample("1h").mean()  # type: ignore
    ref_monthly_energy = (
        ref_energy.groupby(ref_energy.index.month).sum().reindex(months)
    )
    diff = actual_monthly_energy - ref_monthly_energy
    ratio = actual_monthly_energy / ref_monthly_energy
    comparison_summary = pd.DataFrame(
        {
            "actual_energy": actual_monthly_energy,
            "weather_adjusted_energy": ref_monthly_energy,
            "difference": diff,
            "ratio": ratio,
        }
    )
    month_name_index = pd.Index([calendar.month_name[i] for i in months], name="month")
    comparison_summary.index = month_name_index
    results_list.append(
        DBResult(
            schema_path="/",
            type="actual vs weather adjusted reference",
            data=comparison_summary,
        )
    )
    save_results_to_db(job.object_id, results_list, si)
