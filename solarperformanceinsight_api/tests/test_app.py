import httpx
from hypothesis import HealthCheck
from hypothesis import settings as hypsettings
from hypothesis import strategies as st
import pytest
import schemathesis


from solarperformanceinsight_api.main import app
from solarperformanceinsight_api import settings


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
    if token_req.status_code != 200:
        pytest.skip("Cannot retrieve valid Auth0 token")
    else:
        token = token_req.json()["access_token"]
        return token


schemathesis.fixups.install()
schema = schemathesis.from_asgi("/openapi.json", app)


@schema.parametrize()
@schema.given(data=st.data())
@hypsettings(max_examples=30, suppress_health_check=HealthCheck.all())
def test_api(data, case, auth_token):
    """Tests all endpoints in the OpenAPI Schema"""
    if data.draw(st.booleans()):
        case.headers["Authorization"] = f"Bearer {auth_token}"
    else:
        if "Authorization" in case.headers:
            del case.headers["Authorization"]
    response = case.call_asgi()
    case.validate_response(response)
