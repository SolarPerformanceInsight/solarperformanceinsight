import logging


from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from prometheus_fastapi_instrumentator import Instrumentator  # type: ignore
import sentry_sdk
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware


from . import auth, __version__, settings, storage
from .routers import systems, user, parameters


app = FastAPI(title="Solar Performance Insight")
app.add_middleware(CORSMiddleware, allow_origins=[])

sentry_sdk.init(traces_sample_rate=settings.traces_sample_rate)
app.add_middleware(SentryAsgiMiddleware)

Instrumentator(
    should_respect_env_var=True,
    env_var_name="ENABLE_METRICS",
    excluded_handlers=["/metrics", "/ping"],
).instrument(app).expose(app, include_in_schema=False, should_gzip=True)


@app.get("/ping", include_in_schema=False)
async def ping() -> str:  # pragma: no cover
    return "pong"


class LogFilter(logging.Filter):
    def filter(record):  # pragma: no cover
        if hasattr(record, "scope"):
            if record.scope.get("path") in ("/ping", "/metrics"):
                return 0
        return 1


@app.on_event("startup")
async def startup_event():  # pragma: no cover
    storage.engine.connect()
    await auth.get_auth_key()
    for handler in logging.getLogger("uvicorn.access").handlers:
        handler.addFilter(LogFilter)


def custom_openapi():
    if app.openapi_schema:  # pragma: no cover
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Solar Performance Insight API",
        description="""
The backend RESTful API for Solar Performance Insight.

# Introduction

On this page, you'll find documentation for the Solar Performance
Insight API.  The API primarily serves the Solar Performance Insight
dashboard, but power users may interact with it directly. An OpenAPI
generator such as
[https://github.com/OpenAPITools/openapi-generator](https://github.com/OpenAPITools/openapi-generator)
may be used to generate client libraries for a number of languages to
interact with the API. A download link for the OpenAPI spec can be
found above.

# Authentication

The API is secured via OAuth 2.0 and OpenID Connect with
[Auth0](https://auth0.com) as the identity provider. We require valid
JSON Web Token (JWT) from Auth0 to be included as a Bearer token in
the Authorization header for API access. When [requesting a
token](https://auth0.com/docs/api/authentication#authorization-code-flow-with-pkce46),
the audience must be set to `{audience}`, the Client ID must be set to
`{client_id}`, and the token endpoint is `{token_endpoint}`.  Most tokens
are set to expire in 3 hours, and Auth0 rate limits requests, so users
are advised to reuse a token for as long as it is valid. One Python
library that can automatically refresh the tokens is
[Authlib](https://docs.authlib.org/en/latest/client/oauth2.html#oauth2session-for-password).

""".format(
            audience=settings.auth_audience,
            client_id=settings.auth_client_id,
            token_endpoint=settings.auth_issuer,
        ),
        version=__version__,
        routes=app.routes,
    )

    openapi_schema["info"]["contact"] = {
        "name": "Solar Performance Insight Team",
        "email": "info@solarperformanceinsight.org",
        "url": "https://github.com/solarperformanceinsight/solarperformanceinsight-api",
    }
    openapi_schema["info"]["license"] = {
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    }
    openapi_schema["tags"] = [
        {
            "name": "PV Systems",
            "description": "Interact with PV System metadata",
        },
        {"name": "User", "description": "Interact with User metadata"},
        {"name": "Parameters", "description": "Retrieve parameters for select schemas"},
    ]
    openapi_schema["servers"] = [{"url": "/api"}]  # for the docs 'try it out' to work
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi  # type: ignore
app.include_router(
    systems.router,
    prefix="/systems",
    tags=["PV Systems"],
    dependencies=[Depends(auth.get_user_id)],
)
app.include_router(
    user.router, prefix="/user", tags=["User"], dependencies=[Depends(auth.get_user_id)]
)
app.include_router(parameters.router, prefix="/parameters", tags=["Parameters"])
