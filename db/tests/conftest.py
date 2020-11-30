import os
from uuid import uuid1


import pymysql
import pytest


@pytest.fixture(scope='session')
def connection():
    connection = pymysql.connect(
        host=os.getenv('MYSQL_HOST', '127.0.0.1'),
        port=int(os.getenv('MYSQL_PORT', 3306)),
        user='root',
        password='testpassword',
        database='spi_data',
        binary_prefix=True)
    return connection


@pytest.fixture(scope='session')
def auth0_id():
    return 'auth0|testuserid'


@pytest.fixture(scope='session')
def user_id():
    return str(uuid1())


@pytest.fixture(scope='session')
def standard_test_data(auth0_id, user_id, connection):
    curs = connection.cursor()
    curs.execute(
        'insert into users (id, auth0_id) values (uuid_to_bin(%s, 1), %s)',
        (user_id, auth0_id)
    )
    connection.commit()
    yield
    curs.execute(
        'delete from users where id = uuid_to_bin(%s, 1)',
        user_id
    )
    connection.commit()


@pytest.fixture()
def cursor(connection, standard_test_data):
    yield connection.cursor()
    connection.rollback()
