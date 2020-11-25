"""Test systems endpoints"""
import uuid


from fastapi.testclient import TestClient
import pytest


from solarperformanceinsight_api.main import app


@pytest.fixture(scope="module")
def client(auth_token):
    out = TestClient(app)
    out.headers.update({"Authorization": f"Bearer {auth_token}"})
    return out


@pytest.fixture(scope="module")
def noauthclient():
    return TestClient(app)


def test_get_system_404(client):
    id_ = str(uuid.uuid1())
    response = client.get(f"/systems/{id_}")
    assert response.status_code == 404


def test_get_system_noauth(noauthclient):
    id_ = str(uuid.uuid1())
    response = noauthclient.get(f"/systems/{id_}")
    assert response.status_code == 403
