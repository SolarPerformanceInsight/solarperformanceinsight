import calendar
from copy import deepcopy
import datetime as dt
from io import BytesIO
from uuid import uuid1


import numpy as np
import pandas as pd
from pvlib.location import Location
from pvlib.modelchain import ModelChain
import pytest


from solarperformanceinsight_api import compute, storage, models, pvmodeling


pytestmark = pytest.mark.usefixtures("add_example_db_data")


def test_run_job(job_id, auth0_id, mocker, nocommit_transaction):
    new = mocker.MagicMock()

    mocker.patch.object(compute, "lookup_job_compute_function", return_value=new)
    compute.run_job(job_id, auth0_id)
    assert new.call_count == 1


def test_run_job_no_job(other_job_id, auth0_id, mocker, nocommit_transaction):
    new = mocker.MagicMock()
    mocker.patch.object(compute, "lookup_job_compute_function", return_value=new)
    compute.run_job(other_job_id, auth0_id)
    assert new.call_count == 0


@pytest.mark.parametrize("msg", [0, 1])
def test_run_job_job_fail(job_id, auth0_id, mocker, msg, nocommit_transaction):
    if msg:
        new = mocker.MagicMock(side_effect=ValueError("message"))
    else:
        new = mocker.MagicMock(side_effect=ValueError)
    mocker.patch.object(compute, "lookup_job_compute_function", return_value=new)
    compute.run_job(job_id, auth0_id)
    assert new.call_count == 1
    with storage.StorageInterface(user=auth0_id).start_transaction() as st:
        results = st.list_job_results(job_id)
    assert len(results) == 1
    assert results[0].definition.type == "error message"


@pytest.mark.parametrize(
    "njp,exp,tp",
    [
        (
            dict(
                calculate="predicted performance",
                weather_granularity="system",
                irradiance_type="standard",
                temperature_type="air",
            ),
            compute.run_performance_job,
            True,
        ),
        (
            dict(
                calculate="expected performance",
                weather_granularity="system",
                irradiance_type="standard",
                temperature_type="air",
            ),
            compute.run_performance_job,
            True,
        ),
        (
            dict(
                compare="predicted and actual performance",
                predicted_data_parameters=dict(
                    data_available="weather only",
                    weather_granularity="system",
                    irradiance_type="standard",
                    temperature_type="air",
                ),
                actual_data_parameters=dict(
                    weather_granularity="system",
                    irradiance_type="standard",
                    temperature_type="air",
                    performance_granularity="system",
                ),
            ),
            compute.compare_predicted_and_actual,
            True,
        ),
        (
            dict(
                compare="expected and actual performance",
                performance_granularity="system",
                weather_granularity="system",
                irradiance_type="standard",
                temperature_type="air",
            ),
            compute.compare_expected_and_actual,
            True,
        ),
        (
            dict(compare="monthly predicted and actual performance"),
            compute.compare_monthly_predicted_and_actual,
            False,
        ),
    ],
)
def test_lookup_compute_function(njp, system_def, exp, system_id, stored_job, tp):
    njp["system_id"] = system_id
    if tp:
        njp["time_parameters"] = dict(
            start="2020-01-01T00:00:00+00:00",
            end="2020-12-31T23:59:59+00:00",
            step="15:00",
            timezone="UTC",
        )
    job = models.Job(parameters=njp, system_definition=system_def)
    stored_job.definition = job
    assert compute.lookup_job_compute_function(stored_job) == exp


def test_get_data(complete_job_id, complete_job_data_id, auth0_id):
    si = storage.StorageInterface(user=auth0_id)
    assert isinstance(
        compute._get_data(complete_job_id, complete_job_data_id, si),
        pd.DataFrame,
    )


def test_get_data_bad(job_id, job_data_ids, auth0_id):
    si = storage.StorageInterface(user=auth0_id)
    with pytest.raises(TypeError):
        compute._get_data(job_id, job_data_ids[0], si)


@pytest.fixture()
def insert_monthly_data(
    monthlypa_job_id,
    auth0_id,
    nocommit_transaction,
    monthly_weather_actuals_id,
    monthly_weather_original_id,
    monthly_perf_actuals_id,
    monthly_perf_original_id,
):
    si = storage.StorageInterface(user=auth0_id)
    months = calendar.month_name[1:]
    monthadj = [np.cos((i - 6) / 24 * np.pi) for i in range(12)]
    energydf = pd.DataFrame(
        {"total_energy": [60000 * x for x in monthadj], "month": months}
    )
    weatherdf = pd.DataFrame(
        {
            "total_poa_insolation": [500 * 8 * 30 * x for x in monthadj],
            "average_daytime_cell_temperature": [25 * x for x in monthadj],
            "month": months,
        }
    )
    ref_energy = energydf.copy()
    ref_energy.loc[:, "total_energy"] *= 0.9
    ref_weather = weatherdf.copy()
    ref_weather.loc[:, "total_poa_insolation"] *= 0.96
    ref_weather.loc[:, "average_daytime_cell_temperature"] *= 1.2

    with si.start_transaction() as st:
        for did, df in [
            (monthly_weather_actuals_id, weatherdf),
            (monthly_perf_actuals_id, energydf),
            (monthly_weather_original_id, ref_weather),
            (monthly_perf_original_id, ref_energy),
        ]:
            iob = BytesIO()
            df.to_feather(iob)
            iob.seek(0)
            st.add_job_data(
                monthlypa_job_id,
                did,
                "test.arrow",
                "application/vnd.apache.arrow.file",
                iob.read(),
            )
    return energydf, weatherdf, ref_energy, ref_weather


def test_get_data_month(
    monthlypa_job_id,
    monthly_perf_actuals_id,
    auth0_id,
    nocommit_transaction,
    insert_monthly_data,
):
    si = storage.StorageInterface(user=auth0_id)
    exp, *_ = insert_monthly_data
    out = compute._get_data(monthlypa_job_id, monthly_perf_actuals_id, si)
    pd.testing.assert_frame_equal(exp.set_index("month"), out)


def test_DBResult_setting():
    df = pd.DataFrame(
        {"a": 0.0},
        index=pd.date_range("2020-01-01T00:00Z", freq="10min", periods=3, name="time"),
    )
    dbr = compute.DBResult(schema_path="/", type="performance data", data=df)
    new_df = pd.read_feather(BytesIO(dbr.data))
    pd.testing.assert_frame_equal(new_df, df.astype("float32").reset_index())


def test_save_results_to_db(job_id, nocommit_transaction, auth0_id):
    si = storage.StorageInterface(user=auth0_id)
    with si.start_transaction() as st:
        prev_results = st.list_job_results(job_id)
    assert len(prev_results) == 0
    df = pd.DataFrame(
        {"a": 0.0},
        index=pd.date_range("2020-01-01T00:00Z", freq="10min", periods=3, name="time"),
    )
    dbrs = [
        compute.DBResult(schema_path="/", type="performance data", data=df),
        compute.DBResult(schema_path="/", type="weather data", data=df),
    ]
    compute.save_results_to_db(job_id, dbrs, si)
    with si.start_transaction() as st:
        new_results = st.list_job_results(job_id)
        status = st.get_job_status(job_id)
    assert len(new_results) == 2
    assert status.status == "complete"


@pytest.mark.parametrize(
    "inp,name,shift,expected_index",
    [
        (
            pd.Series(
                0, index=pd.date_range("2021-01-01T00:10Z", freq="20min", periods=5)
            ),
            "myname",
            dt.timedelta(minutes=10),
            pd.date_range("2021-01-01T00:00Z", freq="20min", periods=5, name="time"),
        ),
        (
            pd.DataFrame(
                {"a": 0},
                index=pd.date_range("2021-01-01T00:10Z", freq="20min", periods=5),
            ),
            "myname",
            dt.timedelta(minutes=10),
            pd.date_range("2021-01-01T00:00Z", freq="20min", periods=5, name="time"),
        ),
        pytest.param(
            0,
            "name",
            dt.timedelta(minutes=1),
            None,
            marks=pytest.mark.xfail(raises=TypeError, strict=True),
        ),
        pytest.param(
            pd.Series(dtype=float),
            "name",
            dt.timedelta(minutes=1),
            None,
            marks=pytest.mark.xfail(raises=TypeError, strict=True),
        ),
        pytest.param(
            pd.DataFrame(dtype=float),
            "name",
            dt.timedelta(minutes=1),
            None,
            marks=pytest.mark.xfail(raises=TypeError, strict=True),
        ),
    ],
)
def test_adjust_frame(inp, name, shift, expected_index):
    out = compute._adjust_frame(inp, shift, name)
    pd.testing.assert_index_equal(out.index, expected_index)
    if isinstance(out, pd.Series):
        assert out.name == name


def test_generate_job_weather_data_system(stored_job, auth0_id, mocker):
    si = storage.StorageInterface(user=auth0_id)

    def mockgetdata(job_id, data_id, si):
        return pd.DataFrame({"jid": job_id, "did": data_id}, index=[0])

    mocker.patch("solarperformanceinsight_api.compute._get_data", new=mockgetdata)

    ndo = deepcopy(stored_job.data_objects[0])
    ndo.object_id = uuid1()
    ndo.definition.schema_path = "/"

    stored_job.definition.parameters.weather_granularity = "system"
    stored_job.data_objects = [ndo]
    gen = compute.generate_job_weather_data(stored_job, si)
    assert str(type(gen)) == "<class 'generator'>"
    genlist = list(gen)
    assert len(genlist) == 1
    # returns list of dataframes for each item
    pd.testing.assert_frame_equal(
        genlist[0][0],
        pd.DataFrame({"jid": stored_job.object_id, "did": ndo.object_id}, index=[0]),
    )


def test_generate_job_weather_data_system_multi_array(stored_job, auth0_id, mocker):
    si = storage.StorageInterface(user=auth0_id)
    arr = stored_job.definition.system_definition.inverters[0].arrays[0]
    stored_job.definition.system_definition.inverters[0].arrays = [arr, arr]

    def mockgetdata(job_id, data_id, si):
        return pd.DataFrame({"jid": job_id, "did": data_id}, index=[0])

    mocker.patch("solarperformanceinsight_api.compute._get_data", new=mockgetdata)

    ndo = deepcopy(stored_job.data_objects[0])
    ndo.object_id = uuid1()
    ndo.definition.schema_path = "/"

    stored_job.definition.parameters.weather_granularity = "system"
    stored_job.data_objects = [ndo]
    gen = compute.generate_job_weather_data(stored_job, si)
    assert str(type(gen)) == "<class 'generator'>"
    genlist = list(gen)
    assert len(genlist) == 1
    assert len(genlist[0]) == 2


def test_generate_job_weather_data_inverter(stored_job, auth0_id, mocker):
    si = storage.StorageInterface(user=auth0_id)

    def mockgetdata(job_id, data_id, si):
        return (job_id, data_id)

    mocker.patch("solarperformanceinsight_api.compute._get_data", new=mockgetdata)

    do = stored_job.data_objects[0]
    new_do = []
    ids = []
    for i in range(3):
        ndo = deepcopy(do)
        ndo.object_id = uuid1()
        ids.append((stored_job.object_id, ndo.object_id))
        ndo.definition.schema_path = f"/inverters/{i}"
        new_do.append(ndo)
    inv = deepcopy(stored_job.definition.system_definition.inverters[0])
    stored_job.definition.system_definition.inverters = [inv, inv, inv]
    stored_job.definition.parameters.weather_granularity = "inverter"
    stored_job.data_objects = new_do
    gen = compute.generate_job_weather_data(stored_job, si)
    assert str(type(gen)) == "<class 'generator'>"
    genlist = list(gen)
    # returns list of dataframes for each item
    assert genlist == [[i] for i in ids]


def test_generate_job_weather_data_inverter_multi_array(stored_job, auth0_id, mocker):
    si = storage.StorageInterface(user=auth0_id)

    def mockgetdata(job_id, data_id, si):
        return (job_id, data_id)

    mocker.patch("solarperformanceinsight_api.compute._get_data", new=mockgetdata)

    do = stored_job.data_objects[0]
    new_do = []
    ids = []
    for i in range(3):
        ndo = deepcopy(do)
        ndo.object_id = uuid1()
        ids.append((stored_job.object_id, ndo.object_id))
        ndo.definition.schema_path = f"/inverters/{i}"
        new_do.append(ndo)
    inv = deepcopy(stored_job.definition.system_definition.inverters[0])
    inv.arrays = [inv.arrays[0], inv.arrays[0]]
    stored_job.definition.system_definition.inverters = [inv, inv, inv]
    stored_job.definition.parameters.weather_granularity = "inverter"
    stored_job.data_objects = new_do
    gen = compute.generate_job_weather_data(stored_job, si)
    assert str(type(gen)) == "<class 'generator'>"
    genlist = list(gen)
    # returns list of dataframes for each item
    assert genlist == [[i, i] for i in ids]


def test_generate_job_weather_data_array(stored_job, auth0_id, mocker):
    si = storage.StorageInterface(user=auth0_id)

    def mockgetdata(job_id, data_id, si):
        return (job_id, data_id)

    mocker.patch("solarperformanceinsight_api.compute._get_data", new=mockgetdata)

    do = stored_job.data_objects[0]
    new_do = []
    ids = []
    for i in range(3):
        arid = []
        for j in range(2):
            ndo = deepcopy(do)
            ndo.object_id = f"{i}_{j}"
            arid.append((stored_job.object_id, ndo.object_id))
            ndo.definition.schema_path = f"/inverters/{i}/arrays/{j}"
            new_do.append(ndo)
        ids.append(arid)
    inv = deepcopy(stored_job.definition.system_definition.inverters[0])
    arr = deepcopy(inv.arrays[0])
    inv.arrays = [arr, arr]
    stored_job.definition.system_definition.inverters = [inv, inv, inv]
    stored_job.definition.parameters.weather_granularity = "array"
    stored_job.data_objects = new_do
    gen = compute.generate_job_weather_data(stored_job, si)
    assert str(type(gen)) == "<class 'generator'>"
    genlist = list(gen)
    assert len(genlist[0]) == 2
    assert genlist[0][0][1] == "0_0"
    assert genlist[0][1][1] == "0_1"
    assert genlist[1][1][1] == "1_1"
    # returns list of dataframes for each inverter
    assert genlist == ids


def test_generate_job_weather_data_fail(stored_job, auth0_id, mocker):
    si = storage.StorageInterface(user=auth0_id)

    stored_job.definition.parameters.weather_granularity = "unknown"
    with pytest.raises(ValueError):
        list(compute.generate_job_weather_data(stored_job, si))


@pytest.mark.parametrize("numarr", [1, 2])
def test_generate_job_performance_data_system(stored_job, auth0_id, mocker, numarr):
    si = storage.StorageInterface(user=auth0_id)
    arr = stored_job.definition.system_definition.inverters[0].arrays[0]
    stored_job.definition.system_definition.inverters[0].arrays = [arr] * numarr

    def mockgetdata(job_id, data_id, si):
        return pd.DataFrame({"jid": job_id, "did": data_id}, index=[0])

    mocker.patch("solarperformanceinsight_api.compute._get_data", new=mockgetdata)

    ndo = deepcopy(stored_job.data_objects[0])
    ndo.object_id = uuid1()
    ndo.definition.schema_path = "/"
    ndo.definition.type = "actual performance data"

    stored_job.data_objects = [ndo]
    gen = compute.generate_job_performance_data(
        stored_job, si, [models.JobDataTypeEnum.actual_performance], "system"
    )
    assert str(type(gen)) == "<class 'generator'>"
    genlist = list(gen)
    assert len(genlist) == 1
    # returns list of dataframes for each item
    pd.testing.assert_frame_equal(
        genlist[0],
        pd.DataFrame({"jid": stored_job.object_id, "did": ndo.object_id}, index=[0]),
    )


def test_generate_job_performance_data_inverter(stored_job, auth0_id, mocker):
    si = storage.StorageInterface(user=auth0_id)

    def mockgetdata(job_id, data_id, si):
        return (job_id, data_id)

    mocker.patch("solarperformanceinsight_api.compute._get_data", new=mockgetdata)

    do = stored_job.data_objects[0]
    new_do = []
    ids = []
    for i in range(3):
        ndo = deepcopy(do)
        ndo.object_id = uuid1()
        ids.append((stored_job.object_id, ndo.object_id))
        ndo.definition.schema_path = f"/inverters/{i}"
        if i == 1:
            ndo.definition.type = "actual performance data"
        else:
            ndo.definition.type = "predicted performance data"
        new_do.append(ndo)
    inv = deepcopy(stored_job.definition.system_definition.inverters[0])
    stored_job.definition.system_definition.inverters = [inv, inv, inv]
    stored_job.data_objects = new_do
    gen = compute.generate_job_performance_data(
        stored_job,
        si,
        [
            models.JobDataTypeEnum.actual_performance,
            models.JobDataTypeEnum.predicted_performance,
        ],
        "inverter",
    )
    assert str(type(gen)) == "<class 'generator'>"
    genlist = list(gen)
    # returns list of dataframes for each item
    assert genlist == ids


def test_generate_job_performance_data_fail(stored_job, auth0_id, mocker):
    si = storage.StorageInterface(user=auth0_id)

    with pytest.raises(ValueError):
        list(
            compute.generate_job_performance_data(
                stored_job, si, [models.JobDataTypeEnum.actual_performance], "unknown"
            )
        )


def test_generate_job_performance_data_empty(stored_job, auth0_id, mocker):
    si = storage.StorageInterface(user=auth0_id)
    assert not list(
        compute.generate_job_performance_data(
            stored_job,
            si,
            [models.JobDataTypeEnum.predicted_performance_dc],
            "inverter",
        )
    )
    assert not list(
        compute.generate_job_performance_data(
            stored_job,
            si,
            [models.JobDataTypeEnum.actual_performance],
            None,
        )
    )


def test_get_index():
    class Res:
        cell_temperature = (43,)
        ac = pd.Series(0, dtype=float, index=[0, 1])
        total_irrad = (pd.DataFrame({"a": [0]}, dtype=float, index=[0]),)
        what = "str"

    res = Res()

    with pytest.raises(TypeError):
        compute._get_index(res, "what", 0)
    with pytest.raises(IndexError):
        compute._get_index(res, "total_irrad", 1)
    pd.testing.assert_series_equal(res.ac, compute._get_index(res, "ac", 0))
    pd.testing.assert_frame_equal(
        res.total_irrad[0], compute._get_index(res, "total_irrad", 0)
    )
    nans = compute._get_index(res, "cell_temperature", 0)
    assert pd.isna(nans).all()


# pytest param ids are helpful finding combos that fail
@pytest.mark.parametrize(
    "tempcols",
    (
        # pytest parm ids are
        pytest.param(["temp_air", "wind_speed"], id="standard_temp"),
        pytest.param(["temp_air"], id="air_temp_only"),
        pytest.param(["module_temperature"], id="module_temp"),
        pytest.param(["cell_temperature"], id="cell_temp"),
        pytest.param(["module_temperature", "wind_speed"], id="module_temp+ws"),
        pytest.param(["cell_temperature", "wind_speed"], id="cell_temp+ws"),
    ),
)
@pytest.mark.parametrize(
    "method,colmap",
    (
        pytest.param("run_model", {}, id="run_model"),
        pytest.param(
            "run_model_from_poa",
            {"ghi": "poa_global", "dni": "poa_direct", "dhi": "poa_diffuse"},
            id="run_model_poa",
        ),
        pytest.param(
            "run_model_from_effective_irradiance",
            {"ghi": "effective_irradiance", "dni": "noped", "dhi": "nah"},
            id="run_model_eff",
        ),
    ),
)
def test_process_single_modelchain(
    system_def, either_tracker, method, colmap, tempcols
):
    # full run through a modelchain with a fixed tilt single array,
    # fixed tilt two array, and single axis tracker single array
    tshift = dt.timedelta(minutes=5)
    index = pd.DatetimeIndex([pd.Timestamp("2020-01-01T12:00:00-07:00")], name="time")
    tempdf = pd.DataFrame(
        {
            "temp_air": [25.0],
            "wind_speed": [10.0],
            "module_temperature": [30.0],
            "cell_temperature": [32.0],
            "poa_global": [1100.0],
        },
        index=index,
    )[tempcols]
    irrad = pd.DataFrame(
        {
            "ghi": [1100.0],
            "dni": [1000.0],
            "dhi": [100.0],
        },
        index=index,
    ).rename(columns=colmap)
    df = pd.concat([irrad, tempdf], axis=1)
    inv, _, multi = either_tracker
    location = Location(latitude=32.1, longitude=-110.8, altitude=2000, name="test")
    pvsys = pvmodeling.construct_pvsystem(inv)
    mc = ModelChain(system=pvsys, location=location, **dict(inv._modelchain_models))
    weather = [df]
    if multi:
        weather.append(df)

    # shifted (df - 5min) goes in, and shifted right (df) goes to be processed
    dblist, summary = compute.process_single_modelchain(mc, weather, method, tshift, 0)
    assert summary.performance.iloc[0] == 250.0
    assert set(summary.columns) == {
        "performance",
        "poa_global",
        "effective_irradiance",
        "cell_temperature",
        "zenith",
    }
    pd.testing.assert_index_equal(summary.index, df.index)

    # performance for the inverter, and weather for each array
    if multi:
        assert {d.schema_path for d in dblist} == {
            "/inverters/0",
            "/inverters/0/arrays/0",
            "/inverters/0/arrays/1",
        }
    else:
        assert {d.schema_path for d in dblist} == {
            "/inverters/0",
            "/inverters/0/arrays/0",
        }

    inv_perf = list(
        filter(
            lambda x: x.type == "performance data" and x.schema_path == "/inverters/0",
            dblist,
        )
    )[0]
    pd.testing.assert_frame_equal(
        pd.read_feather(BytesIO(inv_perf.data)),
        pd.DataFrame(
            {"performance": [250.0]}, dtype="float32", index=df.index
        ).reset_index(),
    )
    arr0_weather_df = pd.read_feather(
        BytesIO(
            list(
                filter(
                    lambda x: x.type == "weather data"
                    and x.schema_path == "/inverters/0/arrays/0",
                    dblist,
                )
            )[0].data
        )
    )
    assert set(arr0_weather_df.columns) == {
        "poa_global",
        "effective_irradiance",
        "cell_temperature",
        "time",
    }
    # pvlib>0.9.0a2
    assert not pd.isna(arr0_weather_df.cell_temperature).any()


@pytest.fixture()
def mockup_modelchain(mocker, stored_job):
    save = mocker.patch("solarperformanceinsight_api.compute.save_results_to_db")
    inv = stored_job.definition.system_definition.inverters[0]
    stored_job.definition.system_definition.inverters = [inv, inv]
    mocker.patch(
        "solarperformanceinsight_api.compute.generate_job_weather_data",
        return_value=[0, 1],
    )
    df = pd.DataFrame(
        {
            "performance": [1.0],
            "poa_global": [1.0],
            "effective_irradiance": [1.0],
            "cell_temperature": [1.0],
            "zenith": [1.0],
        },
        index=pd.DatetimeIndex([pd.Timestamp("2020-01-01T12:00Z")], name="time"),
    )
    mocker.patch(
        "solarperformanceinsight_api.compute.process_single_modelchain",
        return_value=([], df),
    )
    return stored_job, save, df


def test_run_performance_job(auth0_id, nocommit_transaction, mockup_modelchain):
    si = storage.StorageInterface(user=auth0_id)
    stored_job, save, df = mockup_modelchain

    compute.run_performance_job(stored_job, si)
    assert save.call_count == 1
    reslist = save.call_args[0][1]
    assert len(reslist) == 3

    perf = reslist[-1]
    assert perf.type == "performance data"
    iob = BytesIO(perf.data)
    iob.seek(0)
    perf_df = pd.read_feather(iob).set_index("time")
    assert perf_df.loc[df.index[0], "performance"] == 2.0  # sum of 2 inverters
    pd.testing.assert_index_equal(
        perf_df.index, stored_job.definition.parameters.time_parameters._time_range
    )

    month_avg = reslist[0]
    assert month_avg.type == "monthly summary"
    iob = BytesIO(month_avg.data)
    iob.seek(0)
    month_df = pd.read_feather(iob)
    assert len(month_df.index) == 12
    ser = month_df.iloc[0]
    assert len(ser) == 5
    assert ser.loc["month"] == "January"
    assert abs(ser.loc["total_energy"] - 2.0) < 1e-8
    assert abs(ser.loc["plane_of_array_insolation"] - 1.0) < 1e-8


def test_compare_expected_and_actual(mockup_modelchain, auth0_id, nocommit_transaction):
    si = storage.StorageInterface(user=auth0_id)
    stored_job, save, df = mockup_modelchain

    compute.compare_expected_and_actual(stored_job, si)
    assert save.call_count == 1
    reslist = save.call_args[0][1]
    assert len(reslist) == 4

    summary = reslist[-1]
    assert summary.type == "actual vs expected energy"
    iob = BytesIO(summary.data)
    iob.seek(0)
    summary_df = pd.read_feather(iob)
    assert len(summary_df.index) == 12
    ser = summary_df.iloc[0]
    assert len(ser) == 5
    assert ser.loc["month"] == "January"
    assert (ser.loc["expected_energy"] - 2.0) < 1e-7
    assert ser.loc["actual_energy"] == 1.0
    assert (ser.loc["difference"] - -1.0) < 1e-7
    assert (ser.loc["ratio"] - 1.0 / 2.0) < 1e-7


def test_compare_monthly_predicted_and_actual_pvsyst(
    mocker, auth0_id, nocommit_transaction, insert_monthly_data, monthlypa_job_id
):
    si = storage.StorageInterface(user=auth0_id)
    with si.start_transaction() as st:
        job = st.get_job(monthlypa_job_id)
    assert isinstance(
        job.definition.system_definition.inverters[0].arrays[0].module_parameters,
        models.PVsystModuleParameters,
    )
    with pytest.raises(TypeError):
        compute.compare_monthly_predicted_and_actual(job, si)


@pytest.fixture()
def pvwatts_system():
    sysdict = deepcopy(models.SYSTEM_EXAMPLE)
    arr = dict(
        name="array",
        make_model="custom",
        albedo=0.2,
        modules_per_string=10,
        strings=5,
        tracking=dict(tilt=20.0, azimuth=180.0),
        temperature_model_parameters=dict(
            a=-3.47,
            b=-0.0594,
            deltaT=3,
        ),
        module_parameters=dict(pdc0=240.0, gamma_pdc=-0.5),
    )
    inv = dict(
        name="Inverter 1",
        make_model="custom",
        losses={},
        airmass_model="kastenyoung1989",
        aoi_model="physical",
        clearsky_model="ineichen",
        spectral_model="no_loss",
        transposition_model="haydavies",
        inverter_parameters=dict(pdc0=7500),
        arrays=[arr],
    )
    inv1 = deepcopy(inv)
    inv1["name"] = "inverter 2"
    inv1["arrays"] = [arr, arr]
    sysdict["inverters"] = [inv, inv1]
    return models.PVSystem(**sysdict)


def test_compare_monthly_predicted_and_actual(
    mocker,
    auth0_id,
    nocommit_transaction,
    insert_monthly_data,
    monthlypa_job_id,
    pvwatts_system,
):
    si = storage.StorageInterface(user=auth0_id)
    save = mocker.patch("solarperformanceinsight_api.compute.save_results_to_db")

    with si.start_transaction() as st:
        job = st.get_job(monthlypa_job_id)
    job.definition.system_definition = pvwatts_system
    compute.compare_monthly_predicted_and_actual(job, si)
    assert save.call_count == 1
    reslist = save.call_args[0][1]
    assert len(reslist) == 1

    summary = reslist[0]
    assert summary.type == "actual vs weather adjusted reference"
    iob = BytesIO(summary.data)
    iob.seek(0)
    summary_df = pd.read_feather(iob)
    assert len(summary_df.index) == 12
    ser = summary_df.iloc[6]
    assert len(ser) == 5
    assert ser.loc["month"] == "July"
    assert ser.loc["actual_energy"] == 60000
    assert ser.loc["weather_adjusted_energy"] == 56212.5
    assert ser.loc["difference"] == 3787.5
    assert (ser.loc["ratio"] - 1.0673783) < 1e-7


# list(models.TemperatureTypeEnum))  pvlib#1192 for module_temperature
@pytest.fixture(params=("air", "cell"))
def temp_type(request):
    return request.param


@pytest.fixture(params=list(models.IrradianceTypeEnum))
def irr_type(request):
    return request.param


@pytest.fixture(params=list(models.WeatherGranularityEnum))
def weather_gran(request):
    return request.param


@pytest.fixture(params=list(models.PerformanceGranularityEnum))
def perf_gran(request):
    return request.param


@pytest.fixture(
    params=(
        ("weather only", None),
        ("weather and AC performance", "system"),
        ("weather and AC performance", "inverter"),
        ("weather, AC, and DC performance", "system"),
        ("weather, AC, and DC performance", "inverter"),
    )
)
def pred_params(irr_type, temp_type, weather_gran, request):
    if request.param[0] == "weather only":
        return dict(
            irradiance_type=irr_type,
            temperature_type=temp_type,
            weather_granularity=weather_gran,
            data_available=request.param[0],
        )
    else:
        return dict(
            irradiance_type=irr_type,
            temperature_type=temp_type,
            weather_granularity=weather_gran,
            data_available=request.param[0],
            performance_granularity=request.param[1],
        )


@pytest.fixture()
def actual_params(irr_type, temp_type, weather_gran, perf_gran):
    return dict(
        irradiance_type=irr_type,
        temperature_type=temp_type,
        weather_granularity=weather_gran,
        performance_granularity=perf_gran,
    )


@pytest.fixture()
def mockup_predicted_actual(
    mocker, pvwatts_system, system_id, pred_params, actual_params
):
    save = mocker.patch("solarperformanceinsight_api.compute.save_results_to_db")
    cat = pd.Timestamp.utcnow()
    job_params = models.ComparePredictedActualJobParameters(
        system_id=system_id,
        time_parameters=dict(
            start="2021-02-01T00:00:00-07:00",
            end="2021-04-01T00:00:00-07:00",
            step="30:00",
            timezone="Etc/GMT+7",
        ),
        compare="predicted and actual performance",
        predicted_data_parameters=pred_params,
        actual_data_parameters=actual_params,
    )
    index = job_params.time_parameters._time_range
    job = models.Job(
        parameters=job_params,
        system_definition=pvwatts_system,  # TODO: add cec and pvsyst tests
    )
    ids = [uuid1() for _ in range(len(job._data_items))]
    data_objects = [
        models.StoredJobDataMetadata(
            object_id=ids[i],
            object_type="job_data",
            created_at=cat,
            modified_at=cat,
            definition=dict(
                present=True,
                filename="data",
                data_format="application/vnd.apache.arrow.file",
                type=di.type,
                data_columns=di._data_cols,
                schema_path=di.schema_path,
            ),
        )
        for i, di in enumerate(job._data_items.values())
    ]
    stored_job = models.StoredJob(
        object_id=uuid1(),
        definition=job,
        status=dict(
            status="queued",
            last_change=cat,
        ),
        created_at=cat,
        modified_at=cat,
        data_objects=data_objects,
    )
    day = (index.hour > 8) & (index.hour < 17)
    perf = pd.DataFrame({"performance": 4000 * day}, index=index)
    perf.index.name = "time"
    weather = pd.DataFrame(
        {
            "temp_air": 25.0,
            "wind_speed": 10.0,
            "module_temperature": 35.0,
            "cell_temperature": 40.0,
            "effective_irradiance": 1000 * day,
            "poa_global": 1100 * day,
            "poa_direct": 1000 * day,
            "poa_diffuse": 100 * day,
            "ghi": 1100 * day,
            "dni": 1000 * day,
            "dhi": 100 * day,
        },
        index=index,
    )
    weather.index.name = "time"

    data = {}
    for i, ((sp, type_), di) in enumerate(job._data_items.items()):
        cols = set(di._data_cols) - {"time"}
        if type_ == models.JobDataTypeEnum.actual_performance:
            data[ids[i]] = perf.copy()
            if sp == "/":
                data[ids[i]] *= 3
        elif type_ == models.JobDataTypeEnum.predicted_performance:
            data[ids[i]] = perf.copy() * 0.9
            if sp == "/":
                data[ids[i]] *= 3
        elif type_ == models.JobDataTypeEnum.predicted_performance_dc:
            data[ids[i]] = perf.copy() * 0.98
            if sp == "/":
                data[ids[i]] *= 3
        elif type_ == models.JobDataTypeEnum.actual_weather:
            data[ids[i]] = weather[cols].copy()
        elif type_ == models.JobDataTypeEnum.original_weather:
            data[ids[i]] = weather[cols].copy() * 0.94

    def _get_data(job_id, data_id, si):
        return data[data_id]

    mocker.patch("solarperformanceinsight_api.compute._get_data", new=_get_data)
    return stored_job, save


def test_compare_predicted_and_actual(
    mockup_predicted_actual, auth0_id, nocommit_transaction
):
    si = storage.StorageInterface(user=auth0_id)
    job, save = mockup_predicted_actual
    compute.compare_predicted_and_actual(job, si)
    assert save.call_count == 1
    reslist = save.call_args[0][1]
    if (
        job.definition.parameters.predicted_data_parameters.data_available
        == "weather only"
    ):
        # 2 weather adj, 1 summary, 3 inv, 2 array
        assert len(reslist) == 8
    else:
        assert len(reslist) == 3

    assert (
        len([1 for res in reslist if res.type == "weather adjusted performance"]) == 2
    )

    summary = reslist[-1]
    assert summary.type == "actual vs weather adjusted reference"
    iob = BytesIO(summary.data)
    iob.seek(0)
    summary_df = pd.read_feather(iob)
    assert len(summary_df.index) == 2
    ser = summary_df.iloc[0]
    assert len(ser) == 5
    assert ser.loc["month"] == "February"
    assert "actual_energy" in ser
    assert "weather_adjusted_energy" in ser
    assert "difference" in ser
    assert "ratio" in ser
