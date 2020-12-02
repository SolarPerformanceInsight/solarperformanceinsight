"""Test some select system endpoint interaction. The majority of testing
is done via schemathesis in ../../tests/test_app.py
"""
import uuid


from fastapi.testclient import TestClient
import pytest


from solarperformanceinsight_api.main import app
from solarperformanceinsight_api import models


@pytest.fixture(scope="module")
def client(auth_token):
    out = TestClient(app)
    out.headers.update({"Authorization": f"Bearer {auth_token}"})
    return out


@pytest.fixture(scope="module")
def noauthclient():
    return TestClient(app)


def test_get_system(client, system_id, stored_system, add_example_db_data):
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


def test_get_other_system(client, add_example_db_data, other_system_id):
    response = client.get(f"/systems/{other_system_id}")
    assert response.status_code == 404


def test_delete_other_system(client, add_example_db_data, other_system_id):
    response = client.delete(f"/systems/{other_system_id}")
    assert response.status_code == 404


def test_update_other_system(client, add_example_db_data, other_system_id, system_def):
    system_def.albedo = 999
    system_def.name = "New Name"
    response = client.post(f"/systems/{other_system_id}", data=system_def.json())
    assert response.status_code == 404
