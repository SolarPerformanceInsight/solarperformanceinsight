import uuid


import pytest


from solarperformanceinsight_api import models


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
    assert response.content == b"binary data blob"


def test_add_job_data_no_data(client, job_id, job_data_ids):
    response = client.post(f"/jobs/{job_id}/data/{job_data_ids[0]}")
    assert response.status_code == 422


def test_upload_compute(client, job_id, job_data_ids, nocommit_transaction):
    response = client.post(
        f"/jobs/{job_id}/data/{job_data_ids[0]}",
        files={"file": ("test.arrow", b"data", "application/vnd.apache.arrow.file")},
    )
    assert response.status_code == 204
    response = client.get(f"/jobs/{job_id}/status")
    assert response.json()["status"] == "prepared"
    response = client.post(f"/jobs/{job_id}/compute")
    assert response.status_code == 202
    response = client.get(f"/jobs/{job_id}/status")
    assert response.json()["status"] == "queued"


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


def test_create_upload_compute_delete(client, nocommit_transaction, new_job):
    cr = client.post("/jobs/", data=new_job.json())
    assert cr.status_code == 201
    new_id = cr.json()["object_id"]
    response = client.get(f"/jobs/{new_id}")
    assert response.status_code == 200
    stored_job = response.json()
    assert len(stored_job["data_objects"]) == 1
    data_id = stored_job["data_objects"][0]["object_id"]
    response = client.post(
        f"/jobs/{new_id}/data/{data_id}",
        files={"file": ("test.arrow", b"data", "application/vnd.apache.arrow.file")},
    )
    assert response.status_code == 204
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


def test_check_job(client, new_job):
    response = client.post("/jobs/", data=new_job.json())
    assert response.status_code == 201


def test_check_job_bad(client):
    response = client.post("/jobs/", data="reasllybad")
    assert response.status_code == 422
