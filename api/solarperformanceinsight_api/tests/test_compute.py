from copy import deepcopy
import datetime as dt
from io import BytesIO
from uuid import uuid1


import pandas as pd
import pytest


from solarperformanceinsight_api import compute, storage, models


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
    "job_type,exp",
    [
        (
            models.CalculatePerformanceJob(calculate="predicted performance"),
            compute.run_performance_job,
        ),
        (
            models.CalculatePerformanceJob(calculate="expected performance"),
            compute.run_performance_job,
        ),
        (
            models.ComparePerformanceJob(
                compare="predicted and actual performance",
                performance_granularity="system",
            ),
            compute.dummy_func,
        ),
        (
            models.ComparePerformanceJob(
                compare="predicted and expected performance",
                performance_granularity="system",
            ),
            compute.dummy_func,
        ),
        (
            models.ComparePerformanceJob(
                compare="expected and actual performance",
                performance_granularity="system",
            ),
            compute.dummy_func,
        ),
    ],
)
def test_lookup_compute_function(stored_job, job_type, exp):
    stored_job.definition.parameters.job_type = job_type
    assert compute.lookup_job_compute_function(stored_job) == exp


def test_get_data(complete_job_id, complete_job_data_id, auth0_id):
    si = storage.StorageInterface(user=auth0_id)
    shift = dt.timedelta(minutes=30) / 2
    assert isinstance(
        compute._get_data(complete_job_id, complete_job_data_id, si, shift),
        pd.DataFrame,
    )


def test_get_data_bad(job_id, job_data_ids, auth0_id):
    si = storage.StorageInterface(user=auth0_id)
    shift = dt.timedelta(minutes=30) / 2
    with pytest.raises(TypeError):
        compute._get_data(job_id, job_data_ids[0], si, shift)


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
    out = compute._adjust_frame(inp, name, shift)
    pd.testing.assert_index_equal(out.index, expected_index)
    if isinstance(out, pd.Series):
        assert out.name == name


def test_generate_job_weather_data_system(stored_job, auth0_id, mocker):
    tshift = dt.timedelta(minutes=5)
    si = storage.StorageInterface(user=auth0_id)

    def mockgetdata(job_id, data_id, si, shift):
        assert shift == tshift
        return pd.DataFrame({"jid": job_id, "did": data_id}, index=[0])

    mocker.patch("solarperformanceinsight_api.compute._get_data", new=mockgetdata)

    ndo = deepcopy(stored_job.data_objects[0])
    ndo.object_id = uuid1()
    ndo.definition.schema_path = "/"

    stored_job.definition.parameters.weather_granularity = "system"
    stored_job.data_objects = [ndo]
    gen = compute.generate_job_weather_data(stored_job, si, tshift)
    assert str(type(gen)) == "<class 'generator'>"
    genlist = list(gen)
    assert len(genlist) == 1
    # returns list of dataframes for each item
    pd.testing.assert_frame_equal(
        genlist[0][0],
        pd.DataFrame({"jid": stored_job.object_id, "did": ndo.object_id}, index=[0]),
    )


def test_generate_job_weather_data_system_multi_array(stored_job, auth0_id, mocker):
    tshift = dt.timedelta(minutes=5)
    si = storage.StorageInterface(user=auth0_id)
    arr = stored_job.definition.system_definition.inverters[0].arrays[0]
    stored_job.definition.system_definition.inverters[0].arrays = [arr, arr]

    def mockgetdata(job_id, data_id, si, shift):
        assert shift == tshift
        return pd.DataFrame({"jid": job_id, "did": data_id}, index=[0])

    mocker.patch("solarperformanceinsight_api.compute._get_data", new=mockgetdata)

    ndo = deepcopy(stored_job.data_objects[0])
    ndo.object_id = uuid1()
    ndo.definition.schema_path = "/"

    stored_job.definition.parameters.weather_granularity = "system"
    stored_job.data_objects = [ndo]
    gen = compute.generate_job_weather_data(stored_job, si, tshift)
    assert str(type(gen)) == "<class 'generator'>"
    genlist = list(gen)
    assert len(genlist) == 1
    assert len(genlist[0]) == 2


def test_generate_job_weather_data_inverter(stored_job, auth0_id, mocker):
    tshift = dt.timedelta(minutes=5)
    si = storage.StorageInterface(user=auth0_id)

    def mockgetdata(job_id, data_id, si, shift):
        assert shift == tshift
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
    gen = compute.generate_job_weather_data(stored_job, si, tshift)
    assert str(type(gen)) == "<class 'generator'>"
    genlist = list(gen)
    # returns list of dataframes for each item
    assert genlist == [[i] for i in ids]


def test_generate_job_weather_data_inverter_multi_array(stored_job, auth0_id, mocker):
    tshift = dt.timedelta(minutes=5)
    si = storage.StorageInterface(user=auth0_id)

    def mockgetdata(job_id, data_id, si, shift):
        assert shift == tshift
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
    gen = compute.generate_job_weather_data(stored_job, si, tshift)
    assert str(type(gen)) == "<class 'generator'>"
    genlist = list(gen)
    # returns list of dataframes for each item
    assert genlist == [[i, i] for i in ids]


def test_generate_job_weather_data_array(stored_job, auth0_id, mocker):
    tshift = dt.timedelta(minutes=5)
    si = storage.StorageInterface(user=auth0_id)

    def mockgetdata(job_id, data_id, si, shift):
        assert shift == tshift
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
    gen = compute.generate_job_weather_data(stored_job, si, tshift)
    assert str(type(gen)) == "<class 'generator'>"
    genlist = list(gen)
    assert len(genlist[0]) == 2
    assert genlist[0][0][1] == "0_0"
    assert genlist[0][1][1] == "0_1"
    assert genlist[1][1][1] == "1_1"
    # returns list of dataframes for each inverter
    assert genlist == ids


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


def test_process_single_modelchain(mocker):
    tshift = dt.timedelta(minutes=5)
    df = pd.DataFrame({"poa_global": [1.0]}, index=[pd.Timestamp("2020-01-01T12:00")])
    shifted = df.shift(freq=-tshift)
    shifted.index.name = "time"

    class Res:
        ac = df["poa_global"]
        total_irrad = (df, df)
        effective_irradiance = (df, df)
        cell_temperature = (df, df)
        solar_position = {"zenith": df}

    class Sys:
        arrays = [0, 1]

    class MC:
        results = Res()
        system = Sys()

        def run_model(self, data):
            pd.testing.assert_frame_equal(df, data[0])
            return self

    with pytest.raises(AttributeError):
        compute.process_single_modelchain(MC(), [df], "run_from_poa", tshift, 0)

    dblist, summary = compute.process_single_modelchain(
        MC(), [df], "run_model", tshift, 0
    )
    pd.testing.assert_frame_equal(
        summary,
        pd.DataFrame(
            {
                "performance": [1.0],
                "poa_global": [1.0],
                "effective_irradiance": [1.0],
                "cell_temperature": [1.0],
                "zenith": [1.0],
            },
            index=shifted.index,
        ),
    )

    # performance for the inverter, and weather for each array
    assert {d.schema_path for d in dblist} == {
        "/inverters/0",
        "/inverters/0/arrays/0",
        "/inverters/0/arrays/1",
    }


def test_run_performance_job(stored_job, auth0_id, nocommit_transaction, mocker):
    si = storage.StorageInterface(user=auth0_id)
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
    assert month_avg.type == "monthly daytime summary"
    iob = BytesIO(month_avg.data)
    iob.seek(0)
    month_df = pd.read_feather(iob)
    assert len(month_df.index) == 12
    ser = month_df.iloc[0]
    assert len(ser) == 5
    assert ser.loc["month"] == 1.0
    assert ser.loc["performance"] == 2.0
    assert ser.loc["poa_global"] == 1.0
