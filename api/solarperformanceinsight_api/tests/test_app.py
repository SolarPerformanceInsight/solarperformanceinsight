from hypothesis import HealthCheck
from hypothesis import settings as hypsettings
from hypothesis import strategies as st
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
