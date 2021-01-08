from io import BytesIO, StringIO
import uuid


from fastapi import HTTPException
import numpy as np
import pandas as pd
import pytest


from solarperformanceinsight_api import models
from solarperformanceinsight_api.routers import jobs


pytestmark = pytest.mark.usefixtures("add_example_db_data")


def test_list_jobs(client, stored_job):
    response = client.get("/jobs")
    jobs = [models.StoredJob(**j) for j in response.json()]
    assert response.status_code == 200
    assert len(jobs) == 1
    assert jobs[0] == stored_job


def test_get_job(client, stored_job, job_id):
    response = client.get(f"/jobs/{job_id}")
    assert response.status_code == 200
    assert models.StoredJob(**response.json()) == stored_job


@pytest.mark.parametrize(
    "fnc,endpoint",
    (
        ("GET", "/jobs/{other}"),
        ("GET", "/jobs/{other}/status"),
        ("GET", "/jobs/{other}/data/{data_id}"),
        ("GET", "/jobs/{jobid}/data/{baddataid}"),
        ("DELETE", "/jobs/{other}"),
        ("POST", "/jobs/{other}/compute"),
    ),
)
def test_job_404s(client, other_job_id, job_data_ids, fnc, endpoint, job_id):
    response = client.request(
        fnc,
        endpoint.format(
            other=other_job_id,
            data_id=job_data_ids[0],
            jobid=job_id,
            baddataid=str(uuid.uuid1()),
        ),
    )
    assert response.status_code == 404


def test_get_job_noauth(noauthclient, job_id):
    response = noauthclient.get(f"/jobs/{job_id}")
    assert response.status_code == 403


def test_get_job_status(client, job_id, job_status):
    response = client.get(f"/jobs/{job_id}/status")
    assert response.status_code == 200
    assert models.JobStatus(**response.json()) == job_status


def test_delete_job(nocommit_transaction, client, job_id):
    response = client.delete(f"/jobs/{job_id}")
    assert response.status_code == 204


def test_get_job_data(client, job_id, job_data_ids, job_data_meta):
    response = client.get(f"/jobs/{job_id}/data/{job_data_ids[1]}")
    assert response.status_code == 200
    assert response.content == (
        b"time,performance\n2020-01-01 00:00:00+00:00,0\n"
        b"2020-01-01 01:00:00+00:00,1\n"
    )


def test_get_job_data_not_there(client, job_id, job_data_ids, job_data_meta):
    response = client.get(f"/jobs/{job_id}/data/{job_data_ids[0]}")
    assert response.status_code == 204


def test_get_job_data_arrow(
    client, job_id, job_data_ids, job_data_meta, arrow_job_data
):
    response = client.get(
        f"/jobs/{job_id}/data/{job_data_ids[1]}",
        headers={"Accept": "application/vnd.apache.arrow.file"},
    )
    assert response.status_code == 200
    assert response.content == arrow_job_data


def test_get_job_data_bad_type(client, job_id, job_data_ids, job_data_meta):
    response = client.get(
        f"/jobs/{job_id}/data/{job_data_ids[1]}", headers={"Accept": "application/json"}
    )
    assert response.status_code == 406


def test_convert_job_data():
    out = jobs._convert_job_data(
        b"thisiswrong",
        "application/vnd.apache.arrow.file",
        "application/vnd.apache.arrow.file",
        lambda x: x,
    )
    assert out == b"thisiswrong"


def test_convert_job_data_invalid():
    with pytest.raises(HTTPException) as err:
        jobs._convert_job_data(
            b"thisiswrong", "application/vnd.apache.arrow.file", "text/csv", lambda x: x
        )
    assert err.value.status_code == 500


def test_convert_job_data_bad_type():
    with pytest.raises(HTTPException) as err:
        jobs._convert_job_data(
            b"thisiswrong",
            "application/vnd.apache.arrow.file",
            "text/html",
            lambda x: x,
        )
    assert err.value.status_code == 400


@pytest.fixture()
def new_job(system_id):
    return models.JobParameters(
        system_id=system_id,
        job_type=models.CalculatePerformanceJob(calculate="expected performance"),
        time_parameters=models.JobTimeindex(
            start="2020-01-01T00:00:00+00:00",
            end="2020-12-31T23:59:59+00:00",
            step="15:00",
            timezone="UTC",
        ),
        weather_granularity="system",
        irradiance_type="poa",
        temperature_type="module",
    )


def test_create_job(client, nocommit_transaction, new_job):
    response = client.post("/jobs/", data=new_job.json())
    assert response.status_code == 201
    response = client.get(response.headers["Location"])
    assert response.status_code == 200


def test_create_job_inaccessible(
    client, nocommit_transaction, other_system_id, new_job
):
    new_job.system_id = other_system_id
    response = client.post("/jobs/", data=new_job.json())
    assert response.status_code == 404


def test_check_job(client, new_job):
    response = client.post("/jobs/", data=new_job.json())
    assert response.status_code == 201


def test_check_job_bad(client):
    response = client.post("/jobs/", data="reasllybad")
    assert response.status_code == 422


@pytest.fixture()
def performance_df(job_params):
    return pd.DataFrame(
        {
            "time": job_params.time_parameters._time_range,
            "performance": np.random.randn(len(job_params.time_parameters._time_range)),
        }
    )


@pytest.fixture()
def weather_df(job_params):
    return pd.DataFrame(
        {
            "time": job_params.time_parameters._time_range,
            **{
                col: np.random.randn(len(job_params.time_parameters._time_range))
                for col in (
                    "poa_global",
                    "poa_direct",
                    "poa_diffuse",
                    "module_temperature",
                )
            },
        }
    )


@pytest.fixture(params=[0, 1])
def either_df(weather_df, performance_df, request):
    if request.param == 0:
        return weather_df, 0
    else:
        return performance_df, 1


def test_add_job_data_no_data(client, job_id, job_data_ids):
    response = client.post(f"/jobs/{job_id}/data/{job_data_ids[0]}")
    assert response.status_code == 422


def test_post_job_data_arrow(
    client, nocommit_transaction, job_data_ids, job_id, either_df
):
    df, ind = either_df
    iob = BytesIO()
    df.to_feather(iob)
    iob.seek(0)
    response = client.post(
        f"/jobs/{job_id}/data/{job_data_ids[ind]}",
        files={
            "file": (
                "job_data.arrow",
                iob,
                "application/vnd.apache.arrow.file",
            )
        },
    )
    assert response.status_code == 200
    rjson = response.json()
    assert rjson["number_of_missing_rows"] == 0
    assert rjson["missing_times"] == []
    assert rjson["number_of_extra_rows"] == 0
    assert rjson["extra_times"] == []
    assert rjson["number_of_expected_rows"] == len(df)
    assert rjson["number_of_missing_values"] == {
        c: 0 for c in df.columns if c != "time"
    }
    job_resp = client.get(f"/jobs/{job_id}")
    assert (
        job_resp.json()["data_objects"][ind]["definition"]["filename"]
        == "job_data.arrow"
    )
    assert (
        job_resp.json()["data_objects"][ind]["definition"]["data_format"]
        == "application/vnd.apache.arrow.file"
    )


def test_post_job_data_csv(
    client, nocommit_transaction, job_data_ids, job_id, either_df
):
    df, ind = either_df
    iob = StringIO()
    df.to_csv(iob, index=False)
    iob.seek(0)
    response = client.post(
        f"/jobs/{job_id}/data/{job_data_ids[ind]}",
        files={
            "file": (
                "job_data.csv",
                iob,
                "text/csv",
            )
        },
    )
    assert response.status_code == 200
    rjson = response.json()
    assert rjson["number_of_missing_rows"] == 0
    assert rjson["missing_times"] == []
    assert rjson["number_of_extra_rows"] == 0
    assert rjson["extra_times"] == []
    assert rjson["number_of_expected_rows"] == len(df)
    assert rjson["number_of_missing_values"] == {
        c: 0 for c in df.columns if c != "time"
    }

    job_resp = client.get(f"/jobs/{job_id}")
    assert (
        job_resp.json()["data_objects"][ind]["definition"]["filename"] == "job_data.csv"
    )
    assert (
        job_resp.json()["data_objects"][ind]["definition"]["data_format"]
        == "application/vnd.apache.arrow.file"
    )


def test_post_job_data_wrong_id(client, job_id, performance_df):
    iob = BytesIO()
    performance_df.to_feather(iob)
    iob.seek(0)
    response = client.post(
        f"/jobs/{job_id}/data/{job_id}",
        files={
            "file": (
                "job_data.arrow",
                iob,
                "application/vnd.apache.arrow.file",
            )
        },
    )
    assert response.status_code == 404


def test_post_job_data_wrong_job_id(client, other_job_id, job_data_ids, performance_df):
    iob = BytesIO()
    performance_df.to_feather(iob)
    iob.seek(0)
    response = client.post(
        f"/jobs/{other_job_id}/data/{job_data_ids[1]}",
        files={
            "file": (
                "job_data.arrow",
                iob,
                "application/vnd.apache.arrow.file",
            )
        },
    )
    assert response.status_code == 404


def test_post_job_data_bad_data_type(client, job_id, job_data_ids, performance_df):
    iob = StringIO()
    performance_df.to_csv(iob)
    iob.seek(0)
    response = client.post(
        f"/jobs/{job_id}/data/{job_data_ids[1]}",
        files={"file": ("job_data.json", iob, "application/json")},
    )
    assert response.status_code == 415


def test_post_job_data_missing_col(client, job_id, job_data_ids, weather_df):
    iob = BytesIO()
    weather_df.drop(columns="poa_direct").to_feather(iob)
    iob.seek(0)
    response = client.post(
        f"/jobs/{job_id}/data/{job_data_ids[0]}",
        files={
            "file": (
                "job_data.arrow",
                iob,
                "application/vnd.apache.arrow.file",
            )
        },
    )
    assert response.status_code == 400


def test_post_job_data_not_enough(client, job_id, job_data_ids, weather_df):
    iob = BytesIO()
    weather_df.iloc[:10].reset_index().to_feather(iob)
    iob.seek(0)
    response = client.post(
        f"/jobs/{job_id}/data/{job_data_ids[0]}",
        files={
            "file": (
                "job_data.arrow",
                iob,
                "application/vnd.apache.arrow.file",
            )
        },
    )
    assert response.status_code == 400


def test_post_job_data_invalid_time_col(client, job_id, job_data_ids):
    iob = BytesIO()
    df = pd.DataFrame({"time": [0, -99.0, 88.0], "performance": [0, 1, 2.0]})
    df.to_feather(iob)
    iob.seek(0)
    response = client.post(
        f"/jobs/{job_id}/data/{job_data_ids[1]}",
        files={
            "file": (
                "job_data.arrow",
                iob,
                "application/vnd.apache.arrow.file",
            )
        },
    )
    assert response.status_code == 400
    assert "not be parsed as a timestamp" in response.json()["detail"]


def test_post_job_data_duplicate_points(client, job_id, job_data_ids, weather_df):
    iob = BytesIO()
    ndf = weather_df.copy()
    pd.concat([weather_df, ndf], ignore_index=True).reset_index().to_feather(iob)
    iob.seek(0)
    response = client.post(
        f"/jobs/{job_id}/data/{job_data_ids[0]}",
        files={
            "file": (
                "job_data.arrow",
                iob,
                "application/vnd.apache.arrow.file",
            )
        },
    )
    assert response.status_code == 400


def test_post_job_data_too_many_datapoints(client, job_id, job_data_ids, weather_df):
    iob = BytesIO()
    ndf = weather_df.copy()
    ndf.loc[:, "time"] += pd.Timedelta("500d")
    ndf.index = weather_df.index + 10000
    o = pd.concat(
        [weather_df, ndf.loc[weather_df.index[-1] :]], ignore_index=True
    ).reset_index(drop=True)
    o.to_feather(iob)
    iob.seek(0)
    response = client.post(
        f"/jobs/{job_id}/data/{job_data_ids[0]}",
        files={
            "file": (
                "job_data.arrow",
                iob,
                "application/vnd.apache.arrow.file",
            )
        },
    )
    assert response.status_code == 400
    assert "additional rows" in response.json()["detail"]


def test_post_job_data_not_full_index(
    client, job_id, job_data_ids, nocommit_transaction, weather_df
):
    iob = BytesIO()
    extra_times = [pd.Timestamp("19700501T0000Z"), pd.Timestamp("20190101T0000Z")]
    ndf = weather_df.iloc[1:].reset_index()
    ndf = pd.concat([ndf, pd.DataFrame({"time": extra_times})]).reset_index()
    ndf.loc[100, "poa_global"] = None
    ndf.loc[1000:1009, "poa_diffuse"] = None
    ndf.to_feather(iob)
    iob.seek(0)
    response = client.post(
        f"/jobs/{job_id}/data/{job_data_ids[0]}",
        files={
            "file": (
                "job_data.arrow",
                iob,
                "application/vnd.apache.arrow.file",
            )
        },
    )
    assert response.status_code == 200
    rjson = response.json()
    assert rjson["number_of_missing_rows"] == 1
    assert rjson["missing_times"] == [weather_df["time"][0].isoformat()]
    assert rjson["number_of_extra_rows"] == 2
    assert rjson["extra_times"] == [e.isoformat() for e in extra_times]
    assert rjson["number_of_expected_rows"] == len(weather_df)
    assert rjson["number_of_missing_values"] == {
        "poa_global": 1,
        "poa_diffuse": 10,
        "poa_direct": 0,
        "module_temperature": 0,
    }


def test_upload_compute(client, job_id, job_data_ids, nocommit_transaction, weather_df):
    iob = BytesIO()
    weather_df.to_feather(iob)
    iob.seek(0)
    response = client.post(
        f"/jobs/{job_id}/data/{job_data_ids[0]}",
        files={"file": ("test.arrow", iob, "application/vnd.apache.arrow.file")},
    )
    assert response.status_code == 200
    response = client.get(f"/jobs/{job_id}/status")
    assert response.json()["status"] == "prepared"
    response = client.post(f"/jobs/{job_id}/compute")
    assert response.status_code == 202
    response = client.get(f"/jobs/{job_id}/status")
    assert response.json()["status"] == "queued"


def test_create_upload_compute_delete(
    client, nocommit_transaction, new_job, weather_df
):
    cr = client.post("/jobs/", data=new_job.json())
    assert cr.status_code == 201
    new_id = cr.json()["object_id"]
    response = client.get(f"/jobs/{new_id}")
    assert response.status_code == 200
    stored_job = response.json()
    assert len(stored_job["data_objects"]) == 1
    data_id = stored_job["data_objects"][0]["object_id"]
    iob = BytesIO()
    weather_df.to_feather(iob)
    iob.seek(0)
    response = client.post(
        f"/jobs/{new_id}/data/{data_id}",
        files={"file": ("test.arrow", iob, "application/vnd.apache.arrow.file")},
    )
    assert response.status_code == 200
    response = client.get(f"/jobs/{new_id}/status")
    assert response.json()["status"] == "prepared"
    response = client.post(f"/jobs/{new_id}/compute")
    assert response.status_code == 202
    response = client.get(f"/jobs/{new_id}/status")
    assert response.json()["status"] == "queued"
    resp = client.delete(f"/jobs/{new_id}")
    assert resp.status_code == 204
    response = client.get(f"/jobs/{new_id}")
    assert response.status_code == 404
