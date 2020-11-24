import logging


from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
import sentry_sdk
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware


from . import auth, __version__, settings
from .routers import plants


app = FastAPI(title="Solar Performance Insight")
app.add_middleware(CORSMiddleware, allow_origins=[])

sentry_sdk.init(traces_sample_rate=settings.traces_sample_rate)
app.add_middleware(SentryAsgiMiddleware)


@app.get("/ping", include_in_schema=False)
async def ping() -> str:
    return "pong"


class PingFilter(logging.Filter):
    def filter(record):
        if hasattr(record, "scope"):
            if record.scope.get("path") == "/ping":
                return 0
        return 1


@app.on_event("startup")
async def startup_event():
    await auth.get_auth_key()
    for handler in logging.getLogger("uvicorn.access").handlers:
        handler.addFilter(PingFilter)


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


app.openapi = custom_openapi
app.include_router(
    plants.router,
    prefix="/powerplants",
    tags=["Power Plant"],
    dependencies=[Depends(auth.get_user_id)],
)
