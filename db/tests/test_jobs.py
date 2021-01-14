import datetime as dt
import json
from uuid import uuid1


from pymysql.err import OperationalError, IntegrityError, DataError
import pytest


def test_jobs_foreign_key(cursor, job_id):
    cursor.execute(
        "select count(job_id) from job_data where job_id = uuid_to_bin(%s, 1)", job_id
    )
    assert cursor.fetchone()[0] == 4
    cursor.execute(
        "select count(id) from jobs where id = uuid_to_bin(%s, 1)",
        job_id,
    )
    assert cursor.fetchone()[0] == 1

    cursor.execute("delete from jobs where id = uuid_to_bin(%s, 1)", job_id)

    cursor.execute(
        "select count(job_id) from job_data where job_id = uuid_to_bin(%s, 1)", job_id
    )
    assert cursor.fetchone()[0] == 0
    cursor.execute(
        "select count(id) from jobs where id = uuid_to_bin(%s, 1)",
        job_id,
    )
    assert cursor.fetchone()[0] == 0


@pytest.fixture(params=["func", "proc"])
def job_status_func_or_proc(request, job_id, auth0_id):
    if request.param == "func":
        return f"select job_status_func(uuid_to_bin('{job_id}', 1))"
    else:
        return f"call get_job_status('{auth0_id}', '{job_id}')"


def test_job_status_incomplete(cursor, job_status_func_or_proc):
    cursor.execute(job_status_func_or_proc)
    out = cursor.fetchone()[0]
    assert out == "incomplete"


def test_job_status_prepared(cursor, job_status_func_or_proc):
    cursor.execute("update job_data set present = 1")
    cursor.execute(job_status_func_or_proc)
    out = cursor.fetchone()[0]
    assert out == "prepared"


@pytest.mark.parametrize("stat", ["complete", "error"])
def test_job_status_com_err(cursor, stat, job_status_func_or_proc):
    cursor.execute("update jobs set status = %s", stat)
    cursor.execute(job_status_func_or_proc)
    out = cursor.fetchone()[0]
    assert out == stat


def test_get_job_status_denied(cursor, bad_user, job_id):
    with pytest.raises(OperationalError) as err:
        cursor.execute("call get_job_status(%s, %s)", (bad_user, job_id))
    assert err.value.args[0] == 1142


def test_get_job_status_transition(cursor, auth0_id, job_id):
    cursor.execute("call get_job_status(%s, %s)", (auth0_id, job_id))
    res = cursor.fetchone()
    assert res[0] == "incomplete"
    assert res[1] <= dt.datetime.utcnow()
    first_time = res[1]

    cursor.execute("delete from job_data")
    cursor.execute("call get_job_status(%s, %s)", (auth0_id, job_id))
    res = cursor.fetchone()
    assert res[0] == "incomplete"
    assert res[1] == first_time

    cursor.execute(
        "insert into job_data (job_id, schema_path,type, filename, present, modified_at)"
        " values (uuid_to_bin(%s, 1), %s, %s, %s, 1, %s)",
        (job_id, "schema_path", "type", "fnmae", "2030-10-10T00:00"),
    )
    cursor.execute("call get_job_status(%s, %s)", (auth0_id, job_id))
    res = cursor.fetchone()
    assert res[0] == "prepared"
    assert res[1] == dt.datetime(2030, 10, 10)
    cursor.execute("delete from job_data")

    cursor.execute("update jobs set status = 'complete'")
    cursor.execute("call get_job_status(%s, %s)", (auth0_id, job_id))
    res = cursor.fetchone()
    assert res[0] == "complete"
    assert res[1] >= first_time


def test_get_datametadata(cursor, job_id, job_data_ids, mocker):
    cursor.executemany(
        "update job_data set filename = 'newname', present=true, format='text'"
        " where id = uuid_to_bin(%s, 1)",
        (job_data_ids[0], job_data_ids[2]),
    )
    cursor.execute("select job_dataobj_func(uuid_to_bin(%s, 1))", job_id)
    res = cursor.fetchall()
    assert len(res) == 1
    assert json.loads(res[0][0]) == [
        {
            "id": job_data_ids[0],
            "schema_path": "data0",
            "type": "weather",
            "filename": "newname",
            "modified_at": mocker.ANY,
            "created_at": mocker.ANY,
            "present": 1,
            "data_format": "text",
        },
        {
            "id": job_data_ids[1],
            "schema_path": "data1",
            "type": "weather",
            "filename": None,
            "modified_at": mocker.ANY,
            "created_at": mocker.ANY,
            "present": 0,
            "data_format": None,
        },
        {
            "id": job_data_ids[2],
            "schema_path": "data2",
            "type": "weather",
            "filename": "newname",
            "modified_at": mocker.ANY,
            "created_at": mocker.ANY,
            "present": 1,
            "data_format": "text",
        },
        {
            "id": job_data_ids[3],
            "schema_path": "data3",
            "type": "performance",
            "filename": None,
            "modified_at": mocker.ANY,
            "created_at": mocker.ANY,
            "present": 0,
            "data_format": None,
        },
    ]


def test_get_datametadata_none(cursor):
    cursor.execute("select job_dataobj_func(uuid_to_bin(%s, 1))", str(uuid1()))
    assert cursor.fetchone()[0] is None


def test_get_job(
    dictcursor, job_id, mocker, auth0_id, system_id, user_id, job_def, job_data_ids
):
    dictcursor.execute("call get_job(%s, %s)", (auth0_id, job_id))
    res = dictcursor.fetchone()
    assert set(res.keys()) == {
        "job_id",
        "system_id",
        "user_id",
        "definition",
        "created_at",
        "modified_at",
        "status",
        "data_objects",
    }
    assert res["job_id"] == job_id
    assert res["system_id"] == system_id
    assert res["user_id"] == user_id
    assert res["definition"] == job_def
    assert json.loads(res["status"]) == {
        "status": "incomplete",
        "last_change": mocker.ANY,
    }
    data_links = json.loads(res["data_objects"])
    assert len(data_links) == 4
    assert {d["id"] for d in data_links} == set(job_data_ids)


def test_get_job_bad_user(cursor, bad_user, job_id):
    with pytest.raises(OperationalError) as err:
        cursor.execute("call get_job(%s, %s)", (bad_user, job_id))
    assert err.value.args[0] == 1142


def test_get_job_bad_id(cursor, auth0_id, system_id):
    with pytest.raises(OperationalError) as err:
        cursor.execute("call get_job(%s, %s)", (auth0_id, system_id))
    assert err.value.args[0] == 1142


def test_list_jobs(dictcursor, auth0_id, user_id, system_id, otherid, job_id, mocker):
    dictcursor.executemany(
        "insert into jobs (user_id, system_id, definition) values "
        "(uuid_to_bin(%s, 1), uuid_to_bin(%s, 1), %s)",
        (
            (user_id, system_id, '{"system": "stuff"}'),
            (otherid, system_id, '{"bad":"def"}'),
        ),
    )
    dictcursor.execute("call list_jobs(%s)", auth0_id)
    res = dictcursor.fetchall()
    assert len(res) == 3
    keys = {
        "job_id",
        "system_id",
        "user_id",
        "definition",
        "created_at",
        "modified_at",
        "status",
        "data_objects",
    }
    assert set(res[0].keys()) == keys
    assert set(res[1].keys()) == keys
    assert res[0]["job_id"] == job_id
    assert res[0]["user_id"] == user_id
    assert res[1]["user_id"] == user_id
    assert json.loads(res[1]["status"]) == {
        "status": "incomplete",
        "last_change": mocker.ANY,
    }


def test_list_jobs_bad(cursor, bad_user):
    cursor.execute("call list_jobs(%s)", bad_user)
    assert not len(cursor.fetchall())


def test_create_job(dictcursor, auth0_id, system_id, user_id):
    dataobjs = json.dumps(
        [
            {"schema_path": "inverter 0", "type": "weather"},
            {"schema_path": "inverter 0", "type": "performance"},
        ]
    )
    defn = json.dumps({"version": 1, "system_spec": "is here"})
    dictcursor.execute(
        "call create_job(%s, %s, %s, %s)", (auth0_id, system_id, defn, dataobjs)
    )
    newid = dictcursor.fetchone()["job_id"]
    dictcursor.execute(
        "select *, bin_to_uuid(system_id, 1) as sysid, "
        "bin_to_uuid(user_id, 1) as uid from jobs "
        "where id = uuid_to_bin(%s, 1)",
        newid,
    )
    res = dictcursor.fetchone()
    assert res["sysid"] == system_id
    assert res["uid"] == user_id
    assert res["definition"] == defn
    assert res["status"] == "created"
    dictcursor.execute(
        "select schema_path from job_data where job_id = uuid_to_bin(%s, 1)", newid
    )
    res = dictcursor.fetchall()
    assert len(res) == 2
    assert {r["schema_path"] for r in res} == {"inverter 0"}


def test_create_job_baduser(cursor, bad_user, system_id):
    with pytest.raises(OperationalError) as err:
        cursor.execute(
            "call create_job(%s, %s, %s, %s)",
            (bad_user, system_id, "{}", '[{"schema_path": "a", "type": "b"}]'),
        )
    assert err.value.args[0] == 1142


def test_create_job_badsys(cursor, auth0_id):
    with pytest.raises(OperationalError) as err:
        cursor.execute(
            "call create_job(%s, %s, %s, %s)",
            (auth0_id, str(uuid1()), "{}", '[{"schema_path": "a", "type": "b"}]'),
        )
    assert err.value.args[0] == 1142


def test_delete_job(cursor, auth0_id, job_id):
    cursor.execute("call delete_job(%s, %s)", (auth0_id, job_id))
    cursor.execute(
        "select exists(select 1 from jobs where id = uuid_to_bin(%s, 1))", job_id
    )
    assert not cursor.fetchone()[0]


def test_delete_job_baduser(cursor, bad_user, job_id):
    with pytest.raises(OperationalError) as err:
        cursor.execute("call delete_job(%s, %s)", (bad_user, job_id))
    assert err.value.args[0] == 1142


def test_delete_job_not_owned(cursor, auth0_id, user_id):
    with pytest.raises(OperationalError) as err:
        cursor.execute("call delete_job(%s, %s)", (auth0_id, user_id))
    assert err.value.args[0] == 1142


def test_get_job_data(dictcursor, auth0_id, job_data_ids, job_id):
    dictcursor.execute(
        "update job_data set filename='newname', data='data' where id = uuid_to_bin(%s, 1)",
        job_data_ids[0],
    )
    dictcursor.execute(
        "call get_job_data(%s, %s, %s)", (auth0_id, job_id, job_data_ids[0])
    )
    res = dictcursor.fetchone()
    assert res["id"] == job_data_ids[0]
    assert res["job_id"] == job_id
    assert res["schema_path"] == "data0"
    assert res["type"] == "weather"
    assert res["filename"] == "newname"
    assert res["data"] == b"data"


def test_get_job_data_baduser(cursor, bad_user, job_data_ids, job_id):
    with pytest.raises(OperationalError) as err:
        cursor.execute(
            "call get_job_data(%s, %s, %s)", (bad_user, job_id, job_data_ids[1])
        )
    assert err.value.args[0] == 1142


def test_get_job_data_not_owned(cursor, auth0_id, job_id):
    with pytest.raises(OperationalError) as err:
        cursor.execute("call get_job_data(%s, %s, %s)", (auth0_id, job_id, job_id))
    assert err.value.args[0] == 1142


def test_get_job_data_id_mismatch(cursor, auth0_id, job_id, other_job_data_id):
    with pytest.raises(OperationalError) as err:
        cursor.execute(
            "call get_job_data(%s, %s, %s)", (auth0_id, job_id, other_job_data_id)
        )
    assert err.value.args[0] == 1142


def test_add_job_data(dictcursor, auth0_id, job_data_ids, job_id):
    dictcursor.execute(
        "call add_job_data(%s, %s, %s, %s, %s, %s)",
        (
            auth0_id,
            job_id,
            job_data_ids[0],
            "newfilename",
            "application/vnd.apache.arrow.file",
            b"\x00nonsense",
        ),
    )
    dictcursor.execute(
        "select schema_path, type, filename, data, created_at,"
        " modified_at, present, format from job_data where id = uuid_to_bin(%s, 1)",
        job_data_ids[0],
    )
    res = dictcursor.fetchone()
    assert res["schema_path"] == "data0"
    assert res["type"] == "weather"
    assert res["filename"] == "newfilename"
    assert res["data"] == b"\x00nonsense"
    assert res["present"]
    assert res["format"] == "application/vnd.apache.arrow.file"


def test_add_job_data_queued_up(cursor, auth0_id, job_id, job_data_ids):
    cursor.execute(
        "update jobs set status = 'queued' where id = uuid_to_bin(%s, 1)", job_id
    )
    with pytest.raises(OperationalError) as err:
        cursor.execute(
            "call add_job_data(%s, %s, %s, %s, %s, %s)",
            (auth0_id, job_id, job_data_ids[1], "asd", "format", b"sdfsdssd"),
        )
    assert err.value.args[0] == 1348


def test_add_job_data_complete(cursor, auth0_id, job_id, job_data_ids):
    cursor.execute(
        "update jobs set status = 'complete' where id = uuid_to_bin(%s, 1)", job_id
    )
    with pytest.raises(OperationalError) as err:
        cursor.execute(
            "call add_job_data(%s, %s, %s, %s, %s, %s)",
            (auth0_id, job_id, job_data_ids[1], "asd", "format", b"sdfsdssd"),
        )
    assert err.value.args[0] == 1348


def test_add_job_data_baduser(cursor, bad_user, job_data_ids, job_id):
    with pytest.raises(OperationalError) as err:
        cursor.execute(
            "call add_job_data(%s, %s, %s, %s, %s, %s)",
            (bad_user, job_id, job_data_ids[1], "asd", "format", b"sdfsdssd"),
        )
    assert err.value.args[0] == 1142


def test_add_job_data_not_owned(cursor, auth0_id, job_id, other_job_data_id):
    with pytest.raises(OperationalError) as err:
        cursor.execute(
            "call add_job_data(%s, %s, %s, %s, %s, %s)",
            (auth0_id, job_id, other_job_data_id, "b", "a", "c"),
        )
    assert err.value.args[0] == 1142


def test_queue_job(cursor, auth0_id, job_id):
    cursor.execute("update job_data set present = 1")
    cursor.execute("select job_status_func(uuid_to_bin(%s, 1))", job_id)
    assert cursor.fetchone()[0] == "prepared"
    cursor.execute("call queue_job(%s, %s)", (auth0_id, job_id))
    cursor.execute("select status from jobs where id = uuid_to_bin(%s, 1)", job_id)
    assert cursor.fetchone()[0] == "queued"
    # calling twice no effect
    cursor.execute("call queue_job(%s, %s)", (auth0_id, job_id))


def test_queue_job_incomplete(cursor, auth0_id, job_id):
    cursor.execute("select job_status_func(uuid_to_bin(%s, 1))", job_id)
    assert cursor.fetchone()[0] == "incomplete"
    with pytest.raises(OperationalError) as err:
        cursor.execute("call queue_job(%s, %s)", (auth0_id, job_id))
    assert err.value.args[0] == 1054


@pytest.mark.parametrize("stat", ["complete", "error"])
def test_queue_job_done(cursor, auth0_id, job_id, stat):
    cursor.execute(
        "update jobs set status = %s where id = uuid_to_bin(%s, 1)", (stat, job_id)
    )
    with pytest.raises(IntegrityError) as err:
        cursor.execute("call queue_job(%s, %s)", (auth0_id, job_id))
    assert err.value.args[0] == 1062


def test_queue_job_baduser(cursor, bad_user, job_id):
    with pytest.raises(OperationalError) as err:
        cursor.execute("call queue_job(%s, %s)", (bad_user, job_id))
    assert err.value.args[0] == 1142


def test_queue_job_badid(cursor, auth0_id, job_data_ids):
    with pytest.raises(OperationalError) as err:
        cursor.execute("call queue_job(%s, %s)", (auth0_id, job_data_ids[0]))
    assert err.value.args[0] == 1142


def test_get_job_result_metadata(dictcursor, auth0_id, job_id, job_result_ids):
    dictcursor.execute("call get_job_result_metadata(%s, %s)", (auth0_id, job_id))
    res = dictcursor.fetchall()
    assert len(res) == 2
    res0 = res[0]
    assert res0["id"] == job_result_ids[0]
    assert res0["schema_path"] == "/"
    assert res0["type"] == "ghi"
    assert res0["data_format"] == "application/vnd.apache.arrow.file"
    assert res0["created_at"] == res0["modified_at"]

    res1 = res[1]
    assert res1["id"] == job_result_ids[1]
    assert res1["schema_path"] == "/array"
    assert res1["type"] == "poa"
    assert res1["data_format"] == "application/json"


def test_get_job_result_metadata_baduser(cursor, bad_user, job_id):
    with pytest.raises(OperationalError) as err:
        cursor.execute("call get_job_result_metadata(%s, %s)", (bad_user, job_id))
    assert err.value.args[0] == 1142


def test_get_job_result(dictcursor, auth0_id, job_result_ids, job_id):
    dictcursor.execute(
        "call get_job_result(%s, %s, %s)", (auth0_id, job_id, job_result_ids[0])
    )
    res = dictcursor.fetchone()
    assert res["id"] == job_result_ids[0]
    assert res["schema_path"] == "/"
    assert res["type"] == "ghi"
    assert res["data_format"] == "application/vnd.apache.arrow.file"
    assert res["data"] == b"dataz"


def test_get_job_result_baduser(cursor, bad_user, job_result_ids, job_id):
    with pytest.raises(OperationalError) as err:
        cursor.execute(
            "call get_job_result(%s, %s, %s)", (bad_user, job_id, job_result_ids[1])
        )
    assert err.value.args[0] == 1142


def test_get_job_result_not_owned(cursor, auth0_id, job_id):
    with pytest.raises(OperationalError) as err:
        cursor.execute("call get_job_result(%s, %s, %s)", (auth0_id, job_id, job_id))
    assert err.value.args[0] == 1142


def test_get_job_result_id_mismatch(cursor, auth0_id, job_id, other_job_result_id):
    with pytest.raises(OperationalError) as err:
        cursor.execute(
            "call get_job_result(%s, %s, %s)", (auth0_id, job_id, other_job_result_id)
        )
    assert err.value.args[0] == 1142


def test_add_job_results(dictcursor, auth0_id, job_id):
    dictcursor.execute("call get_job_result_metadata(%s, %s)", (auth0_id, job_id))
    assert len(dictcursor.fetchall()) == 2

    dictcursor.execute(
        "call add_job_result(%s, %s, %s, %s, %s, %s)",
        (
            auth0_id,
            job_id,
            "/new",
            "module_temperature",
            "text/csv",
            b"time,module_temperature\n0,1\n",
        ),
    )
    newid = dictcursor.fetchone()["job_result_id"]
    dictcursor.execute("call get_job_result_metadata(%s, %s)", (auth0_id, job_id))
    assert len(dictcursor.fetchall()) == 3

    dictcursor.execute("call get_job_result(%s, %s, %s)", (auth0_id, job_id, newid))
    res = dictcursor.fetchone()
    assert res["schema_path"] == "/new"
    assert res["data"] == b"time,module_temperature\n0,1\n"


def test_add_job_results_baduser(dictcursor, bad_user, job_id):
    with pytest.raises(OperationalError) as err:
        dictcursor.execute(
            "call add_job_result(%s, %s, %s, %s, %s, %s)",
            (
                bad_user,
                job_id,
                "/new",
                "module_temperature",
                "text/csv",
                b"time,module_temperature\n0,1\n",
            ),
        )
    assert err.value.args[0] == 1142


@pytest.mark.parametrize("status", ("complete", "error"))
def test_add_job_results_badstatus(cursor, auth0_id, other_job_id, status):
    cursor.execute(
        "update jobs set status = %s where id = uuid_to_bin(%s, 1)",
        (status, other_job_id),
    )
    with pytest.raises(IntegrityError) as err:
        cursor.execute(
            "call add_job_result(%s, %s, %s, %s, %s, %s)",
            (
                auth0_id,
                other_job_id,
                "/new",
                "module_temperature",
                "text/csv",
                b"time,module_temperature\n0,1\n",
            ),
        )
    assert err.value.args[0] == 1062


@pytest.mark.parametrize("status", ("complete", "error"))
def test_set_job_completion(dictcursor, auth0_id, job_id, status):
    dictcursor.execute(
        "call set_job_completion(%s, %s, %s)", (auth0_id, job_id, status)
    )
    dictcursor.execute("call get_job_status(%s, %s)", (auth0_id, job_id))
    res = dictcursor.fetchone()
    assert res["status"] == status


def test_set_job_completion_baduser(dictcursor, bad_user, job_id):
    with pytest.raises(OperationalError) as err:
        dictcursor.execute(
            "call set_job_completion(%s, %s, %s)", (bad_user, job_id, "error")
        )
    assert err.value.args[0] == 1142


@pytest.mark.parametrize("status", ("created", "queued", "notstat"))
def test_set_job_completion_bad_status(dictcursor, auth0_id, job_id, status):
    with pytest.raises(DataError) as err:
        dictcursor.execute(
            "call set_job_completion(%s, %s, %s)", (auth0_id, job_id, status)
        )
    assert err.value.args[0] == 1265
