from hypothesis import settings as hypsettings
from hypothesis.stateful import run_state_machine_as_test
import pytest
import schemathesis


from solarperformanceinsight_api.main import app


pytestmark = pytest.mark.usefixtures("add_example_db_data")
schemathesis.fixups.install()


@pytest.fixture()
def new_settings():
    return {"stateful_step_count": 5, "max_examples": 150}


@pytest.fixture()
def auth_state_machine(auth_token, new_settings):
    schema = schemathesis.from_asgi("/openapi.json", app)

    class APIWorkflow(schema.as_state_machine()):
        headers: dict

        def setup(self):
            self.headers = {"Authorization": f"Bearer {auth_token}"}

        def get_call_kwargs(self, case):
            return {"headers": self.headers}

    APIWorkflow.TestCase.settings = hypsettings(
        APIWorkflow.TestCase.settings, **new_settings
    )

    return APIWorkflow


@pytest.fixture()
def noauth_state_machine(new_settings):
    schema = schemathesis.from_asgi("/openapi.json", app)
    out = schema.as_state_machine()
    out.TestCase.settings = hypsettings(out.TestCase.settings, **new_settings)
    return out


def test_statefully_with_auth(auth_state_machine):
    run_state_machine_as_test(auth_state_machine)


def test_statefully_without_auth(noauth_state_machine):
    run_state_machine_as_test(noauth_state_machine)
