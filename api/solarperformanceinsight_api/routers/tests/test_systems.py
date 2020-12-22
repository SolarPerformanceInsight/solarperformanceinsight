"""Test some select system endpoint interaction. The majority of testing
is done via schemathesis in ../../tests/test_app.py
"""
import json
import string
from urllib.parse import quote
import uuid


import pytest


from solarperformanceinsight_api import models, storage


pytestmark = pytest.mark.usefixtures("add_example_db_data")


def test_list_systems(client, stored_system):
    response = client.get("/systems")
    systems = [models.StoredPVSystem(**j) for j in response.json()]
    assert len(systems) == 1
    assert systems[0] == stored_system


def test_get_system(client, system_id, stored_system):
    response = client.get(f"/systems/{system_id}")
    assert models.StoredPVSystem(**response.json()) == stored_system


def test_get_system_404(client):
    id_ = str(uuid.uuid1())
    response = client.get(f"/systems/{id_}")
    assert response.status_code == 404


def test_get_system_noauth(noauthclient):
    id_ = str(uuid.uuid1())
    response = noauthclient.get(f"/systems/{id_}")
    assert response.status_code == 403


def test_get_other_system(client, other_system_id):
    response = client.get(f"/systems/{other_system_id}")
    assert response.status_code == 404


def test_delete_other_system(client, other_system_id):
    response = client.delete(f"/systems/{other_system_id}")
    assert response.status_code == 404


@pytest.mark.parametrize("alter", [0, 1])
def test_update_system(client, system_def, system_id, mocker, alter):
    if alter:
        system_def.latitude = 33.99
    update = mocker.spy(storage.StorageInterface, "update_system")
    response = client.post(f"/systems/{system_id}", data=system_def.json())
    assert response.status_code == 201
    assert response.json()["object_id"] == system_id
    update.assert_called()


def test_update_other_system(client, other_system_id, system_def):
    system_def.longitude = -129.83
    system_def.name = "New Name"
    response = client.post(f"/systems/{other_system_id}", data=system_def.json())
    assert response.status_code == 404


@pytest.mark.parametrize(
    "change", [({}, 200), ({"latitude": "notanumber"}, 422), ({"name": "ok"}, 200)]
)
def test_check_system(system_def, client, change):
    cd, code = change
    data = system_def.dict()
    data.update(cd)
    resp = client.post("/systems/check", data=json.dumps(data))
    assert resp.status_code == code


def test_get_create_delete_system(client, system_def, nocommit_transaction, system_id):
    r1 = client.get("/systems/")
    assert len(r1.json()) == 1
    assert r1.json()[0]["object_id"] == system_id
    r2 = client.delete(f"/systems/{system_id}")
    assert r2.status_code == 204
    resp = client.post("/systems/", json=system_def.dict())
    assert resp.status_code == 201
    r3 = client.get(resp.headers["Location"])
    assert r3.status_code == 200
    assert r3.json()["definition"] == system_def


def test_create_same_name(client, system_def, nocommit_transaction):
    resp = client.post("/systems/", json=system_def.dict())
    assert resp.status_code == 409


@pytest.mark.parametrize("char", string.whitespace)
def test_get_system_whitespace(client, char):
    resp = client.get(f"/systems/{quote(char)}")
    if char == "\n":  # newline goes to the list systems endpoint
        assert resp.status_code == 200
    else:
        assert resp.status_code == 422
