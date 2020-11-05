from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi


from . import auth
from .version import version
from .routers import plants


app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=[])


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
        version=version,
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


@app.on_event("startup")
async def startup_event():
    await auth.set_auth_key()
