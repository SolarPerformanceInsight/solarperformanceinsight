import datetime as dt
from io import BytesIO


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
            compute.run_modelchain,
        ),
        (
            models.CalculatePerformanceJob(calculate="expected performance"),
            compute.run_modelchain,
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
            pd.Series(),
            "name",
            dt.timedelta(minutes=1),
            None,
            marks=pytest.mark.xfail(raises=TypeError, strict=True),
        ),
        pytest.param(
            pd.DataFrame(),
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


def test_generate_job_weather_data():
    pass


def test_get_index():
    pass


def test_process_single_modelchain():
    pass


def test_run_modelchain():
    pass


def test_save_results_to_db():
    pass
