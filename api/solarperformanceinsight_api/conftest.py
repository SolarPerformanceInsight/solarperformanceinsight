from contextlib import contextmanager
import datetime as dt
from uuid import UUID


import httpx
import pymysql
import pytest


from solarperformanceinsight_api import settings, models, storage


@pytest.fixture(scope="session")
def auth_token():
    token_req = httpx.post(
        settings.auth_token_url,
        headers={"content-type": "application/json"},
        data=(
            '{"grant_type": "password", '
            '"username": "testing@solarperformanceinsight.org",'
            '"password": "Thepassword123!", '
            f'"audience": "{settings.auth_audience}", '
            f'"client_id": "{settings.auth_client_id}"'
            "}"
        ),
    )
    if token_req.status_code != 200:  # pragma: no cover
        pytest.skip("Cannot retrieve valid Auth0 token")
    else:
        token = token_req.json()["access_token"]
        return token


@pytest.fixture(scope="module")
def root_conn():
    conn = storage._make_sql_connection_partial(user="root", password="testpassword")()
    yield conn
    conn.close()


@pytest.fixture(scope="module")
def add_example_db_data(root_conn):
    curs = root_conn.cursor()
    curs.callproc("add_example_data")
    root_conn.commit()
    yield curs
    curs.callproc("remove_example_data")
    root_conn.commit()


@pytest.fixture()
def nocommit_transaction(mocker):
    conn = storage.engine.connect()

    @contextmanager
    def start_transaction(cls):
        cls._cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        yield cls
        cls._cursor = None

    mocker.patch.object(
        storage.StorageInterface, "start_transaction", new=start_transaction
    )
    yield
    conn.rollback()


@pytest.fixture(scope="module")
def auth0_id():
    return "auth0|5fa9596ccf64f9006e841a3a"


@pytest.fixture(scope="module")
def user_id():
    return UUID("17fbf1c6-34bd-11eb-af43-f4939feddd82")


@pytest.fixture(scope="module")
def system_id():
    return models.SYSTEM_ID


@pytest.fixture(scope="module")
def other_system_id():
    return "6513485a-34cd-11eb-8f13-f4939feddd82"


@pytest.fixture()
def system_def():
    return models.PVSystem(**models.SYSTEM_EXAMPLE)


@pytest.fixture()
def stored_system(system_def, system_id):
    extime = dt.datetime(2020, 12, 1, 1, 23, tzinfo=dt.timezone.utc)
    return models.StoredPVSystem(
        object_id=system_id,
        object_type="system",
        created_at=extime,
        modified_at=extime,
        definition=system_def,
    )


@pytest.fixture(scope="module")
def job_id():
    return "e1772e64-43ac-11eb-92c2-f4939feddd82"


@pytest.fixture(scope="module")
def other_job_id():
    return "7f13ab34-43ad-11eb-80a2-f4939feddd82"


@pytest.fixture(scope="module")
def job_data_ids():
    return (
        "ecaa5a40-43ac-11eb-a75d-f4939feddd82",
        "f9ef0c00-43ac-11eb-8931-f4939feddd82",
    )


@pytest.fixture()
def job_params():
    return models.JobParameters(**models.JOB_PARAMS_EXAMPLE)


@pytest.fixture()
def job_def(system_def, job_params):
    return models.Job(system_definition=system_def, parameters=job_params)


@pytest.fixture()
def job_status():
    return models.JobStatus(
        status="incomplete",
        last_change=dt.datetime(2020, 12, 11, 20, tzinfo=dt.timezone.utc),
    )


@pytest.fixture()
def job_data_meta(job_data_ids):
    return models.StoredJobDataMetadata(
        definition=models.JobDataMetadata(**models.JOB_DATA_META_EXAMPLE),
        object_id=job_data_ids[1],
        object_type="job_data",
        created_at=dt.datetime(2020, 12, 11, 19, 52, tzinfo=dt.timezone.utc),
        modified_at=dt.datetime(2020, 12, 11, 20, tzinfo=dt.timezone.utc),
    )


@pytest.fixture()
def stored_job(job_id, job_def, job_status, job_data_ids, job_data_meta):
    ctime = dt.datetime(2020, 12, 11, 19, 52, tzinfo=dt.timezone.utc)
    job_data_meta_0 = models.StoredJobDataMetadata(
        object_id=job_data_ids[0],
        object_type="job_data",
        created_at=ctime,
        modified_at=ctime,
        definition=models.JobDataMetadata(
            schema_path="/inverters/0/arrays/0",
            type="original weather data",
            filename="",
            data_type="",
        ),
    )
    job_data_meta_1 = job_data_meta
    return models.StoredJob(
        definition=job_def,
        status=job_status,
        data_objects=[job_data_meta_0, job_data_meta_1],
        object_id=job_id,
        object_type="job",
        created_at=ctime,
        modified_at=ctime,
    )
