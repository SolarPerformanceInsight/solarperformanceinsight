from base64 import b64decode
from contextlib import contextmanager
import datetime as dt
from uuid import UUID, uuid1


from fakeredis import FakeRedis  # type: ignore
from fastapi.testclient import TestClient
import httpx
import pymysql
import pytest
from rq import Queue  # type: ignore


from solarperformanceinsight_api.main import app
from solarperformanceinsight_api import settings, models, storage, queuing


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
def client(auth_token):
    out = TestClient(app)
    out.headers.update({"Authorization": f"Bearer {auth_token}"})
    return out


@pytest.fixture(scope="module")
def noauthclient():
    return TestClient(app)


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
            data_columns=[
                "time",
                "poa_global",
                "poa_direct",
                "poa_diffuse",
                "module_temperature",
            ],
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


@pytest.fixture()
def arrow_job_data():
    return b64decode(
        """
QVJST1cxAAD/////gAIAABAAAAAAAAoADgAGAAUACAAKAAAAAAEEABAAAAAAAAoADAAAAAQACAAK
AAAAvAEAAAQAAAABAAAADAAAAAgADAAEAAgACAAAAAgAAAAQAAAABgAAAHBhbmRhcwAAhwEAAHsi
aW5kZXhfY29sdW1ucyI6IFtdLCAiY29sdW1uX2luZGV4ZXMiOiBbXSwgImNvbHVtbnMiOiBbeyJu
YW1lIjogInRpbWUiLCAiZmllbGRfbmFtZSI6ICJ0aW1lIiwgInBhbmRhc190eXBlIjogImRhdGV0
aW1ldHoiLCAibnVtcHlfdHlwZSI6ICJkYXRldGltZTY0W25zXSIsICJtZXRhZGF0YSI6IHsidGlt
ZXpvbmUiOiAiVVRDIn19LCB7Im5hbWUiOiAicGVyZm9ybWFuY2UiLCAiZmllbGRfbmFtZSI6ICJw
ZXJmb3JtYW5jZSIsICJwYW5kYXNfdHlwZSI6ICJpbnQ2NCIsICJudW1weV90eXBlIjogImludDY0
IiwgIm1ldGFkYXRhIjogbnVsbH1dLCAiY3JlYXRvciI6IHsibGlicmFyeSI6ICJweWFycm93Iiwg
InZlcnNpb24iOiAiMi4wLjAifSwgInBhbmRhc192ZXJzaW9uIjogIjEuMS40In0AAgAAAFQAAAAE
AAAAxP///wAAAQIQAAAAJAAAAAQAAAAAAAAACwAAAHBlcmZvcm1hbmNlAAgADAAIAAcACAAAAAAA
AAFAAAAAEAAUAAgABgAHAAwAAAAQABAAAAAAAAEKEAAAACAAAAAEAAAAAAAAAAQAAAB0aW1lAAAA
AAgADAAGAAgACAAAAAAAAwAEAAAAAwAAAFVUQwD/////yAAAABQAAAAAAAAADAAYAAYABQAIAAwA
DAAAAAADBAAcAAAAUAAAAAAAAAAAAAAADAAcABAABAAIAAwADAAAAGgAAAAcAAAAFAAAAAIAAAAA
AAAAAAAAAAQABAAEAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACcAAAAAAAAAKAAAAAAA
AAAAAAAAAAAAACgAAAAAAAAAJAAAAAAAAAAAAAAAAgAAAAIAAAAAAAAAAAAAAAAAAAACAAAAAAAA
AAAAAAAAAAAAEAAAAAAAAAAEIk0YYECCEAAAgAAAirk1muUVAKBC6nud5RUAAAAAABAAAAAAAAAA
BCJNGGBAgg0AAAATAAEAgAEAAAAAAAAAAAAAAAAAAAD/////AAAAABAAAAAMABQABgAIAAwAEAAM
AAAAAAAEAEAAAAAoAAAABAAAAAEAAACQAgAAAAAAANAAAAAAAAAAUAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAoADAAAAAQACAAKAAAAvAEAAAQAAAABAAAADAAAAAgADAAEAAgACAAAAAgAAAAQAAAABgAA
AHBhbmRhcwAAhwEAAHsiaW5kZXhfY29sdW1ucyI6IFtdLCAiY29sdW1uX2luZGV4ZXMiOiBbXSwg
ImNvbHVtbnMiOiBbeyJuYW1lIjogInRpbWUiLCAiZmllbGRfbmFtZSI6ICJ0aW1lIiwgInBhbmRh
c190eXBlIjogImRhdGV0aW1ldHoiLCAibnVtcHlfdHlwZSI6ICJkYXRldGltZTY0W25zXSIsICJt
ZXRhZGF0YSI6IHsidGltZXpvbmUiOiAiVVRDIn19LCB7Im5hbWUiOiAicGVyZm9ybWFuY2UiLCAi
ZmllbGRfbmFtZSI6ICJwZXJmb3JtYW5jZSIsICJwYW5kYXNfdHlwZSI6ICJpbnQ2NCIsICJudW1w
eV90eXBlIjogImludDY0IiwgIm1ldGFkYXRhIjogbnVsbH1dLCAiY3JlYXRvciI6IHsibGlicmFy
eSI6ICJweWFycm93IiwgInZlcnNpb24iOiAiMi4wLjAifSwgInBhbmRhc192ZXJzaW9uIjogIjEu
MS40In0AAgAAAFQAAAAEAAAAxP///wAAAQIQAAAAJAAAAAQAAAAAAAAACwAAAHBlcmZvcm1hbmNl
AAgADAAIAAcACAAAAAAAAAFAAAAAEAAUAAgABgAHAAwAAAAQABAAAAAAAAEKEAAAACAAAAAEAAAA
AAAAAAQAAAB0aW1lAAAAAAgADAAGAAgACAAAAAAAAwAEAAAAAwAAAFVUQwCwAgAAQVJST1cx
"""
    )


@pytest.fixture()
def arrow_weather_job_result():
    return b64decode(
        """
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
"""
    )


@pytest.fixture()
def arrow_performance_job_result():
    return b64decode(
        """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
"""
    )


@pytest.fixture(scope="module")
def job_result_ids():
    return (
        "d84bdf30-55f2-11eb-a03d-f4939feddd82",
        "e525466a-55f2-11eb-a03d-f4939feddd82",
        "e566a59c-55f2-11eb-a03d-f4939feddd82",
    )


@pytest.fixture(scope="module")
def complete_job_id():
    return "4910c750-55f1-11eb-a03d-f4939feddd82"


@pytest.fixture()
def job_result_list():
    return [
        models.StoredJobResultMetadata(**ex) for ex in models.STORED_JOB_RESULT_EXAMPLES
    ]


@pytest.fixture()
def error_job_result(root_conn, job_id):
    curs = root_conn.cursor()
    newid = str(uuid1())
    curs.execute(
        "insert into job_results (id, job_id, schema_path, type, format, data) "
        "values (uuid_to_bin(%s, 1), uuid_to_bin(%s, 1), %s, %s, %s, %s)",
        (
            newid,
            job_id,
            "/",
            "error message",
            "application/json",
            '{"details": "Error in job"}',
        ),
    )
    root_conn.commit()
    yield newid, {"details": "Error in job"}
    curs.execute("delete from job_results where id = uuid_to_bin(%s, 1)", newid)
    root_conn.commit()


@pytest.fixture()
def mock_redis(mocker):
    faker = FakeRedis()
    mocker.patch.object(queuing, "_get_redis_conn", return_value=faker)
    return faker


@pytest.fixture()
def async_queue(mock_redis, mocker):
    q = Queue("jobs", connection=mock_redis)
    mocker.patch.object(queuing, "_get_queue", return_value=q)
    return q


@pytest.fixture()
def sync_queue(mock_redis, mocker):
    q = Queue("jobs", connection=mock_redis, is_async=False)
    mocker.patch.object(queuing, "_get_queue", return_value=q)
    return q
