import datetime as dt
from functools import partial
import json
import logging
from typing import Callable, Generator, Union, List, Tuple
from uuid import UUID


from fastapi import HTTPException
import pandas as pd
from pvlib.modelchain import ModelChainResult, ModelChain  # type: ignore


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
    if isinstance(job.definition.parameters.job_type, models.CalculatePerformanceJob):
        return run_performance_job
    return dummy_func


def dummy_func(job, storage):  # pragma: no cover
    raise NotImplementedError("Job computation not implemented")


def _get_data(
    job_id: UUID, data_id: UUID, si: storage.StorageInterface, shift: dt.timedelta
) -> pd.DataFrame:
    with si.start_transaction() as st:
        meta, data = st.get_job_data(job_id, data_id)
    if meta.definition.data_format != "application/vnd.apache.arrow.file":
        raise TypeError(
            f"Data for /jobs/{job_id}/data/{data_id} not in Apache Arrow format"
        )
    return utils.read_arrow(data).set_index("time").shift(freq=shift)  # type: ignore


def generate_job_weather_data(
    job: models.StoredJob, si: storage.StorageInterface, shift: dt.timedelta
) -> Generator[List[pd.DataFrame], None, None]:
    """Generator to fetch job data at the inverter level to run a ModelChain"""
    data_id_by_schema_path = {
        do.definition.schema_path: do.object_id
        for do in job.data_objects
        if do.definition.type
        in (
            models.JobDataTypeEnum.original_weather,
            models.JobDataTypeEnum.actual_weather,
        )
    }
    job_id = job.object_id
    num_inverters = len(job.definition.system_definition.inverters)
    if (
        job.definition.parameters.weather_granularity
        == models.WeatherGranularityEnum.system
    ):
        data_id = data_id_by_schema_path["/"]
        df = _get_data(job_id, data_id, si, shift)
        for _ in range(num_inverters):
            yield [df.copy()]
    elif (
        job.definition.parameters.weather_granularity
        == models.WeatherGranularityEnum.inverter
    ):
        for i in range(num_inverters):
            data_id = data_id_by_schema_path[f"/inverters/{i}"]
            df = _get_data(job_id, data_id, si, shift)
            yield [df]
    else:
        for i in range(num_inverters):
            num_arrays = len(job.definition.system_definition.inverters[i].arrays)
            data_ids = [
                data_id_by_schema_path[f"/inverters/{i}/arrays/{j}"]
                for j in range(num_arrays)
            ]
            yield [_get_data(job_id, data_id, si, shift) for data_id in data_ids]


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
    inp: Union[pd.Series, pd.DataFrame], name: str, tshift: dt.timedelta
) -> Union[pd.Series, pd.DataFrame]:
    if not isinstance(inp, (pd.Series, pd.DataFrame)):
        raise TypeError(f"Expected pandas.Series or pandas.DataFrame not {type(inp)}")

    if not isinstance(inp.index, pd.DatetimeIndex):  # type: ignore
        raise TypeError("Expected input to have a DatetimeIndex")

    out = inp.shift(freq=-tshift)  # type: ignore
    if isinstance(out, pd.DataFrame):
        out.index.name = "time"  # type: ignore
        return out
    else:
        out.name = name  # type: ignore
        out.index.name = "time"  # type: ignore
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
    chain : pvlib.ModelChain
        The chain to run
    weather_data : List[pandas.DataFrame]
        The data that will be passed to chain.run_model
    run_model_method : str
        The method of chain to used calculate results, i.e. run_model or run_from_poa
    tshift : dt.timedelta
        Weather data should already be shifted forward by this amount, so final results
        will be shifted by -1 * tshift.
    inverter_num : int
        Which inverter in the full system this chain is for

    Returns
    -------
    inverter_results : List[DBResult]
        List of DBResult objects that can be inserted into the database
    summary_frame : pd.DataFrame
        A frame with the AC performance result, zenith angle, and average of
        poa_global, effective_irradiance, and cell_temperature over all arrays
    """
    # run chain
    mc = getattr(chain, run_model_method)(weather_data)
    results = mc.results
    adjust = partial(_adjust_frame, tshift=tshift)
    performance = adjust(results.ac, "performance")
    summary_frame = pd.DataFrame(
        {
            "poa_global": 0,  # type: ignore
            "effective_irradiance": 0,  # type: ignore
            "cell_temperature": 0,  # type: ignore
        },
        index=performance.index,
    )
    summary_frame.index.name = "time"  # type: ignore
    # make nice result output
    num_arrays = len(mc.system.arrays)
    out = []
    for i in range(num_arrays):
        weather: pd.DataFrame = adjust(  # type: ignore
            _get_index(results, "total_irrad", i)[["poa_global"]], "poa_global"
        )
        weather.loc[:, "effective_irradiance"] = adjust(  # type: ignore
            _get_index(results, "effective_irradiance", i), "effective_irradiance"
        )
        weather.loc[:, "cell_temperature"] = adjust(  # type: ignore
            _get_index(results, "cell_temperature", i), "cell_temperature"
        )
        summary_frame += weather  # type: ignore
        out.append(
            DBResult(
                schema_path=f"/inverters/{inverter_num}/arrays/{i}",
                type="weather data",
                data=weather,
            )
        )
    out.append(
        DBResult(
            schema_path=f"/inverters/{inverter_num}",
            type="performance data",
            data=performance,
        )
    )
    # mean
    summary_frame /= num_arrays  # type: ignore
    summary_frame.insert(0, "performance", performance)  # type: ignore
    summary_frame.insert(
        len(summary_frame.columns),
        "zenith",
        adjust(results.solar_position["zenith"], "zenith"),  # type: ignore
    )  # type: ignore
    return out, summary_frame


def run_performance_job(job: models.StoredJob, si: storage.StorageInterface):
    summary = pd.DataFrame(
        {
            "performance": 0,  # type: ignore
            "poa_global": 0,  # type: ignore
            "effective_irradiance": 0,  # type: ignore
            "cell_temperature": 0,  # type: ignore
            "zenith": 0,  # type: ignore
        },
        index=job.definition.parameters.time_parameters._time_range,
    )
    summary.index.name = "time"  # type: ignore
    run_model_method = job.definition._model_chain_method
    tshift = job.definition.parameters.time_parameters.step / 2
    chains = construct_modelchains(job.definition.system_definition)

    weather_count = 0.0
    # result from each inverter...
    result_list = []
    for i, weather_data in enumerate(generate_job_weather_data(job, si, tshift)):
        db_results, array_summary = process_single_modelchain(
            chains[i], weather_data, run_model_method, tshift, i
        )
        result_list += db_results
        summary += array_summary  # type: ignore
        weather_count += 1
    # keep performance as sum, but make everything else average over inverters
    summary = summary.div(  # type: ignore
        pd.Series(
            {
                "performance": 1.0,
                **{
                    col: weather_count
                    for col in summary.columns
                    if col != "performance"
                },
            }
        )
    )
    daytime = summary.pop("zenith") < 87.0  # type: ignore
    daytime.name = "daytime_flag"  # type: ignore
    # will dump any nans and summary for a month may only have a single point and
    # still be not NaN
    daytime_summary = summary.loc[daytime]
    months = daytime.groupby(daytime.index.month).mean().index
    month_summary = (
        daytime_summary.groupby(daytime_summary.index.month).mean().reindex(months)
    )
    month_summary.index.name = "month"  # type: ignore

    result_list.extend(
        [
            DBResult(
                schema_path="/", type="monthly daytime summary", data=month_summary
            ),
            DBResult(
                schema_path="/",
                type="daytime flag",
                data=daytime.to_frame(),
            ),
            DBResult(
                schema_path="/", type="performance data", data=summary[["performance"]]
            ),
        ]
    )
    save_results_to_db(job.object_id, result_list, si)
