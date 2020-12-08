"""Simple development app that mounts the app at /api and
servers static JS files from STATIC_DIRECTORY
"""
import os
from pathlib import Path


from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse
import uvicorn  # type: ignore


from solarperformanceinsight_api.main import app


dev_app = FastAPI()


@dev_app.get("/")
def index():
    return RedirectResponse(url="/index.html")


dev_app.mount("/api", app)


if __name__ == "__main__":
    dev_app.mount(
        "/",
        StaticFiles(
            directory=os.getenv(
                "STATIC_DIRECTORY",
                str(
                    (
                        Path(__file__).parent / ".." / ".." / "dashboard" / "dist"
                    ).absolute()
                ),
            )
        ),
        name="static",
    )
    uvicorn.run(dev_app, port=8000, log_level="info")
