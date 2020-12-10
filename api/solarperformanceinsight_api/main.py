import logging


from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from prometheus_fastapi_instrumentator import Instrumentator  # type: ignore
import sentry_sdk
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware


from . import auth, __version__, settings, storage
from .routers import systems, user


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
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Solar Performance Insight API",
        description="""
The backend RESTful API for Solar Performance Insight.

# Introduction

# Authentication

""",
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
            "name": "Power Plant",
            "description": "Power Plant description",
        }
    ]
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
