from hypothesis.stateful import run_state_machine_as_test
import pytest
import schemathesis


from solarperformanceinsight_api.main import app


schemathesis.fixups.install()


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
