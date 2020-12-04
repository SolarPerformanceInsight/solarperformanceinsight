import datetime as dt
import uuid


from fastapi import HTTPException
import pandas as pd
import pymysql
import pytest


from solarperformanceinsight_api import storage


@pytest.fixture(scope="module")
def storage_interface(auth0_id):
    out = storage.StorageInterface()
    out.commit = False
    out.user = auth0_id
    return out


def test_escape_timestamp():
    assert (
        storage.escape_timestamp(pd.Timestamp("2019-04-08T030423"))
        == "'2019-04-08 03:04:23'"
    )
    assert (
        storage.escape_timestamp(pd.Timestamp("2019-04-08T030423Z"))
        == "'2019-04-08 03:04:23'"
    )
    assert (
        storage.escape_timestamp(pd.Timestamp("2019-04-08T030423-0300"))
        == "'2019-04-08 06:04:23'"
    )


def test_escape_datetime():
    assert (
        storage.escape_datetime(dt.datetime(2019, 5, 1, 23, 33, 12))
        == "'2019-05-01 23:33:12'"
    )
    assert (
        storage.escape_datetime(
            dt.datetime(
                2019, 5, 1, 23, 33, 12, tzinfo=dt.timezone(dt.timedelta(hours=-5))
            )
        )
        == "'2019-05-02 04:33:12'"
    )


def test_convert_datetime_utc():
    assert storage.convert_datetime_utc("2019-05-01 23:01:32") == dt.datetime(
        2019, 5, 1, 23, 1, 32, tzinfo=dt.timezone(dt.timedelta(hours=0))
    )


def test_no_cursor(storage_interface):
    with pytest.raises(AttributeError):
        storage_interface.cursor


@pytest.mark.parametrize("err", [pymysql.err.OperationalError, HTTPException])
def test_start_transaction_rollback(mocker, err):
    si = storage.StorageInterface()
    conn = mocker.MagicMock()
    mocker.patch.object(storage.engine, "connect", return_value=conn)

    with pytest.raises(err):
        with si.start_transaction():
            raise err(400)
    conn.rollback.assert_called()
    conn.commit.assert_not_called()


def test_start_transaction_commit(mocker):
    si = storage.StorageInterface()
    conn = mocker.MagicMock()
    mocker.patch.object(storage.engine, "connect", return_value=conn)
    with si.start_transaction() as st:
        st.cursor.execute("select 1")
    conn.commit.assert_called()


def test_start_transaction_no_commit(mocker):
    si = storage.StorageInterface()
    si.commit = False
    conn = mocker.MagicMock()
    mocker.patch.object(storage.engine, "connect", return_value=conn)
    with si.start_transaction() as st:
        st.cursor.execute("select 1")
    conn.commit.assert_not_called()
    conn.rollback.assert_not_called()


@pytest.mark.parametrize(
    "errno,outerr,status_code",
    [
        (1142, HTTPException, 404),
        (1062, HTTPException, 409),
        (3140, HTTPException, 400),
        (1406, HTTPException, 400),
        (1048, HTTPException, 400),
        (1408, pymysql.err.OperationalError, None),
    ],
)
def test_try_query_raises(storage_interface, errno, outerr, status_code):
    with pytest.raises(outerr) as err:
        with storage_interface.start_transaction() as st:
            st.try_query(
                "signal sqlstate '45000' set message_text='',"
                f" mysql_errno = {errno}",
                None,
            )
    if status_code:
        err.value.status_code == status_code


def test_timezone(storage_interface):
    with storage_interface.start_transaction() as st:
        st.cursor.execute("SELECT @@session.time_zone as tz")
        res = st.cursor.fetchone()["tz"]
    assert res == "+00:00"


def test_call_procedure(storage_interface, mocker, auth0_id):
    tryq = mocker.patch.object(storage_interface, "try_query")
    with storage_interface.start_transaction() as st:
        st._cursor = mocker.MagicMock()
        st._call_procedure("the_procedure", 0, "a")
    tryq.assert_called_with("CALL the_procedure(%s,%s,%s)", (auth0_id, 0, "a"))


def test_call_procedure_without_user(storage_interface, mocker):
    tryq = mocker.patch.object(storage_interface, "try_query")
    with storage_interface.start_transaction() as st:
        st._cursor = mocker.MagicMock()
        st._call_procedure("the_procedure", 0, "a", with_current_user=False)
    tryq.assert_called_with("CALL the_procedure(%s,%s)", (0, "a"))


def test_call_procedure_for_single(storage_interface, mocker):
    callp = mocker.patch.object(storage_interface, "_call_procedure", return_value=[0])
    with storage_interface.start_transaction() as st:
        out = st._call_procedure_for_single("the_procedure", 0, "a")
    callp.assert_called()
    assert out == 0


def test_call_procedure_for_single_nothing(storage_interface, mocker):
    mocker.patch.object(storage_interface, "_call_procedure", return_value=[])
    with pytest.raises(HTTPException):
        with storage_interface.start_transaction() as st:
            st._call_procedure_for_single("the_procedure", 0, "a")


def test_delete_system(storage_interface, add_example_db_data, system_id):
    with storage_interface.start_transaction() as st:
        st.delete_system(system_id)
        assert len(st.list_systems()) == 0


def test_delete_system_dne(storage_interface, add_example_db_data):
    with pytest.raises(HTTPException) as err:
        with storage_interface.start_transaction() as st:
            st.delete_system(uuid.uuid1())
    assert err.value.status_code == 404


def test_delete_system_wrong_owner(
    storage_interface, add_example_db_data, other_system_id
):
    with pytest.raises(HTTPException) as err:
        with storage_interface.start_transaction() as st:
            st.delete_system(other_system_id)
    assert err.value.status_code == 404


def test_create_system(storage_interface, add_example_db_data, system_def):
    system_def.name = "New System"
    with storage_interface.start_transaction() as st:
        sysid = st.create_system(system_def)
        out = st.get_system(sysid.object_id)
    assert out.definition == system_def


def test_create_system_duplicate(storage_interface, add_example_db_data, system_def):
    with pytest.raises(HTTPException) as err:
        with storage_interface.start_transaction() as st:
            st.create_system(system_def)
    assert err.value.status_code == 409


def test_list_system(storage_interface, add_example_db_data, stored_system):
    with storage_interface.start_transaction() as st:
        out = st.list_systems()
    assert out == [stored_system]


def test_get_system(storage_interface, add_example_db_data, stored_system, system_id):
    with storage_interface.start_transaction() as st:
        out = st.get_system(system_id)
    assert out == stored_system


def test_get_system_dne(storage_interface, add_example_db_data):
    with pytest.raises(HTTPException) as err:
        with storage_interface.start_transaction() as st:
            st.get_system(uuid.uuid1())
    assert err.value.status_code == 404


def test_get_system_wrong_owner(
    storage_interface, add_example_db_data, other_system_id
):
    with pytest.raises(HTTPException) as err:
        with storage_interface.start_transaction() as st:
            st.get_system(other_system_id)
    assert err.value.status_code == 404


@pytest.mark.parametrize("alter", [0, 1])
def test_update_system(
    storage_interface, add_example_db_data, stored_system, system_id, system_def, alter
):
    now = dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc, microsecond=0)
    if alter:
        system_def.albedo = 999
        system_def.inverters = []
    with storage_interface.start_transaction() as st:
        st.update_system(system_id, system_def)
        out = st.get_system(system_id)
    assert out.definition == system_def
    assert out.created_at == stored_system.created_at
    assert out.modified_at >= now


def test_update_system_dne(storage_interface, add_example_db_data, system_def):
    with pytest.raises(HTTPException) as err:
        with storage_interface.start_transaction() as st:
            st.update_system(uuid.uuid1(), system_def)
    assert err.value.status_code == 404


def test_update_system_wrong_owner(
    storage_interface, add_example_db_data, other_system_id, system_def
):
    with pytest.raises(HTTPException) as err:
        with storage_interface.start_transaction() as st:
            st.update_system(other_system_id, system_def)
    assert err.value.status_code == 404
