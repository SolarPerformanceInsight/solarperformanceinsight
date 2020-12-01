import datetime as dt
import json
from uuid import UUID, uuid1


from pymysql.err import OperationalError, IntegrityError, DataError
import pytest


def test_user_foreign_key(cursor, system_id, user_id):
    cursor.execute("select 1 from systems where id = uuid_to_bin(%s, 1)", system_id)
    assert cursor.fetchone()[0]
    cursor.execute("delete from users where id = uuid_to_bin(%s, 1)", user_id)
    cursor.execute("select 1 from systems where id = uuid_to_bin(%s, 1)", system_id)
    assert len(cursor.fetchall()) == 0


def test_get_system(cursor, auth0_id, system_id, system_def, user_id):
    cursor.execute(f'call get_system("{auth0_id}", "{system_id}")')
    res = cursor.fetchone()
    assert res[0] == system_id
    assert res[1] == user_id
    assert res[2:4] == system_def
    assert res[4] <= dt.datetime.utcnow()
    assert res[5] <= dt.datetime.utcnow()


def test_get_system_dne(cursor, auth0_id):
    system_id = uuid1()
    with pytest.raises(OperationalError) as err:
        cursor.execute(f'call get_system("{auth0_id}", "{system_id}")')
    assert err.value.args[0] == 1142


def test_get_system_bad_user(cursor, system_id, bad_user):
    auth0_id = bad_user
    with pytest.raises(OperationalError) as err:
        cursor.execute(f'call get_system("{auth0_id}", "{system_id}")')
    assert err.value.args[0] == 1142


def test_list_systems(cursor, auth0_id, system_id, system_def, user_id):
    cursor.execute(f'call list_systems("{auth0_id}")')
    res = cursor.fetchall()
    assert len(res) == 1
    assert res[0][0] == system_id
    assert res[0][1] == user_id
    assert res[0][2:4] == system_def


def test_list_systems_none(cursor, bad_user):
    cursor.execute(f'call list_systems("{bad_user}")')
    assert len(cursor.fetchall()) == 0


def test_create_system(cursor, auth0_id, user_id):
    jdef = '{"version": "1", "stuf": []}'
    num = cursor.execute(
        "call create_system(%s, %s, %s)", (auth0_id, "another sys", jdef)
    )
    assert num == 1
    id_ = cursor.fetchone()[0]
    UUID(id_)
    cursor.execute(
        "select bin_to_uuid(user_id, 1), name, definition from systems where "
        "id = uuid_to_bin(%s, 1)",
        id_,
    )
    res = cursor.fetchone()
    assert res[0] == user_id
    assert res[1] == "another sys"
    assert json.loads(res[2]) == json.loads(jdef)


def test_create_system_bad_user(cursor):
    jdef = '{"version": "1", "stuf": []}'
    with pytest.raises(IntegrityError) as err:
        cursor.execute(
            "call create_system(%s, %s, %s)", ("invalid", "another sys", jdef)
        )
    assert err.value.args[0] == 1048


def test_create_system_duplicate_name(cursor, system_def, auth0_id):
    name, jdef = system_def
    with pytest.raises(IntegrityError) as err:
        cursor.execute("call create_system(%s, %s, %s)", (auth0_id, name, jdef))
    assert err.value.args[0] == 1062


def test_create_system_bad_json(cursor, auth0_id):
    name = "a sys"
    jdef = "{somehow bad json"
    with pytest.raises(OperationalError) as err:
        cursor.execute("call create_system(%s, %s, %s)", (auth0_id, name, jdef))
    assert err.value.args[0] == 3140


def test_create_system_long_name(cursor, auth0_id):
    name = "a sys" * 50
    jdef = "{}"
    with pytest.raises(DataError) as err:
        cursor.execute("call create_system(%s, %s, %s)", (auth0_id, name, jdef))
    assert err.value.args[0] == 1406


def test_update_system(cursor, auth0_id, system_id):
    ndef = '{"version": 2}'
    cursor.execute(
        "select modified_at from systems where id = uuid_to_bin(%s, 1)", system_id
    )
    prevtime = cursor.fetchone()[0]
    cursor.execute("call update_system(%s, %s, %s)", (auth0_id, system_id, ndef))
    num = cursor.execute(
        "select definition, modified_at from systems where id = uuid_to_bin(%s, 1)",
        system_id,
    )
    assert num == 1
    res = cursor.fetchone()
    assert res[0] == ndef
    assert res[1] >= prevtime


def test_update_system_bad_user(cursor, system_id, bad_user):
    with pytest.raises(OperationalError) as err:
        cursor.execute("call update_system(%s, %s, %s)", (bad_user, system_id, "{}"))
    assert err.value.args[0] == 1142


def test_update_system_bad_json(cursor, system_id, auth0_id):
    with pytest.raises(OperationalError) as err:
        cursor.execute("call update_system(%s, %s, %s)", (auth0_id, system_id, "{"))
    assert err.value.args[0] == 3140


def test_delete_system(cursor, system_id, auth0_id):
    assert (
        cursor.execute("select 1 from systems where id = uuid_to_bin(%s, 1)", system_id)
        == 1
    )
    cursor.execute("call delete_system(%s, %s)", (auth0_id, system_id))
    assert (
        cursor.execute("select 1 from systems where id = uuid_to_bin(%s, 1)", system_id)
        == 0
    )


def test_delete_system_bad_user(cursor, system_id, bad_user):
    assert (
        cursor.execute("select 1 from systems where id = uuid_to_bin(%s, 1)", system_id)
        == 1
    )
    with pytest.raises(OperationalError) as err:
        cursor.execute("call delete_system(%s, %s)", (bad_user, system_id))
    assert err.value.args[0] == 1142
    assert (
        cursor.execute("select 1 from systems where id = uuid_to_bin(%s, 1)", system_id)
        == 1
    )


def test_delete_system_bad_id(cursor, auth0_id):
    with pytest.raises(OperationalError) as err:
        cursor.execute("call delete_system(%s, %s)", (auth0_id, str(uuid1())))
    assert err.value.args[0] == 1142
