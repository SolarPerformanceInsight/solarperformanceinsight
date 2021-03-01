from urllib.parse import unquote


from hypothesis import settings as hypsettings
from hypothesis import HealthCheck
import pytest
import schemathesis


from solarperformanceinsight_api.main import app


pytestmark = pytest.mark.usefixtures("add_example_db_data")
schemathesis.fixups.install()
schema = schemathesis.from_asgi("/openapi.json", app)


@pytest.fixture(params=[True, False])
def with_auth(request):
    return request.param


def before_generate_path_parameters(context, strategy):
    return strategy.filter(
        lambda x: not unquote(x.get("system_id", "a")).startswith("\n")
        and not unquote(x.get("job_id", "a")).startswith("\n")
    )


@pytest.mark.usefixtures("nocommit_transaction")
@schema.hooks.apply(before_generate_path_parameters)
@schema.parametrize(method=["GET", "DELETE"])
def test_api(case, with_auth, auth_token):
    if with_auth:
        upd = {"Authorization": f"Bearer {auth_token}"}
        if case.headers is None:
            case.headers = upd
        else:
            case.headers.update(upd)
    response = case.call_asgi()
    case.validate_response(response)


@pytest.mark.usefixtures("nocommit_transaction")
@schema.parametrize(method=["POST"], operation_id="^(?!.*update.*system.*).*")
@hypsettings(max_examples=5, suppress_health_check=HealthCheck.all())
def test_api_post(case, with_auth, auth_token):
    if with_auth:
        upd = {"Authorization": f"Bearer {auth_token}"}
        if case.headers is None:
            case.headers = upd
        else:
            case.headers.update(upd)
    response = case.call_asgi()
    case.validate_response(response)
