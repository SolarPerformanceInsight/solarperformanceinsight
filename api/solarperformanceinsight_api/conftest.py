import httpx
import pytest


@pytest.fixture(scope="session")
def valid_token():
    token_req = httpx.post(
        "https://solarperformanceinsight.us.auth0.com/oauth/token",
        headers={"content-type": "application/json"},
        data=(
            '{"grant_type": "password", '
            '"username": "testing@solarperformanceinsight.org",'
            '"password": "Thepassword123!", '
            '"audience": "https://app.solarperformanceinsight.org/api", '
            '"client_id": "G1YyfLdseYn10RQo11Lqee2ThXj5l5fh"}'
        ),
    )
    if token_req.status_code != 200:
        pytest.skip("Cannot retrieve valid Auth0 token")
    else:
        token = token_req.json()["access_token"]
        return token
