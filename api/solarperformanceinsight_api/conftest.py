import httpx
import pytest


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
    if token_req.status_code != 200:  # pragma: no cover
        pytest.skip("Cannot retrieve valid Auth0 token")
    else:
        token = token_req.json()["access_token"]
        return token
