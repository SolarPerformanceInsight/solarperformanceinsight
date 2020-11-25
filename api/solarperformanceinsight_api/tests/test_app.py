from hypothesis import HealthCheck
from hypothesis import settings as hypsettings
from hypothesis import strategies as st
from hypothesis.stateful import run_state_machine_as_test
import pytest
import schemathesis


from solarperformanceinsight_api.main import app


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


@pytest.fixture()
def auth_state_machine(auth_token):
    schema = schemathesis.from_asgi("/openapi.json", app)

    class APIWorkflow(schema.as_state_machine()):
        headers: dict

        def setup(self):
            self.headers = {"Authorization": f"Bearer {auth_token}"}

        def get_call_kwargs(self, case):
            return {"headers": self.headers}

    return APIWorkflow


@pytest.fixture()
def noauth_state_machine():
    schema = schemathesis.from_asgi("/openapi.json", app)
    return schema.as_state_machine()


def test_statefully_with_auth(auth_state_machine):
    run_state_machine_as_test(auth_state_machine)


def test_statefully_without_auth(noauth_state_machine):
    run_state_machine_as_test(noauth_state_machine)
