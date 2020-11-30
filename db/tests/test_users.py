import datetime as dt
from uuid import UUID


import pytest
from pymysql.err import OperationalError


def test_does_user_exist(cursor, auth0_id):
    cursor.execute(f'select does_user_exist("{auth0_id}")')
    assert cursor.fetchone()[0]


def test_does_user_exist_nope(cursor):
    cursor.execute('select does_user_exist("invalid")')
    assert not cursor.fetchone()[0]


def test_get_user_id(cursor, auth0_id, user_id):
    cursor.execute(f'select get_user_id("{auth0_id}")')
    assert cursor.fetchone()[0] == user_id


def test_get_user_id_nope(cursor):
    cursor.execute('select get_user_id("invalid")')
    assert cursor.fetchone()[0] is None


def test_get_user_binid(cursor, auth0_id, user_id):
    cursor.execute(f'select bin_to_uuid(get_user_binid("{auth0_id}"), 1)')
    assert cursor.fetchone()[0] == user_id


def test_get_user_binid_nope(cursor):
    cursor.execute('select get_user_binid("invalid")')
    assert cursor.fetchone()[0] is None


def test_create_user_if_not_exists(cursor, user_id):
    cursor.execute('call create_user_if_not_exists("newauth0")')
    assert str(UUID(cursor.fetchone()[0])) != user_id


def test_create_user_if_not_exists_already(cursor, user_id, auth0_id):
    cursor.execute(f'call create_user_if_not_exists("{auth0_id}")')
    assert str(UUID(cursor.fetchone()[0])) == user_id


def test_delete_user_by_auth0id(cursor, user_id, auth0_id):
    cursor.execute(f'call delete_user_by_auth0id("{auth0_id}")')
    cursor.execute(
        f'select exists(select 1 from users where id = uuid_to_bin("{user_id}", 1))'
    )
    assert not cursor.fetchone()[0]


def test_delete_user_by_auth0id_dne(cursor):
    with pytest.raises(OperationalError) as err:
        cursor.execute('call delete_user_by_auth0id("invalid")')
    assert err.value.args[0] == 1142


def test_get_user(cursor, auth0_id, user_id):
    cursor.execute(f'call get_user("{auth0_id}")')
    res = cursor.fetchone()
    assert len(res) == 3
    assert res[0] == user_id
    assert res[1] == auth0_id
    assert isinstance(res[2], dt.datetime)


def test_get_user_dne(cursor):
    with pytest.raises(OperationalError) as err:
        cursor.execute('call get_user("invalid")')
    assert err.value.args[0] == 1142
