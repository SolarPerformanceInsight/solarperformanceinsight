from setuptools import setup, find_packages  # type: ignore


if __name__ == "__main__":
    setup(
        name="solarperformanceinsight-api",
        packages=find_packages(),
        install_requires=[
            "cryptography",
            "fastapi",
            "httpx",
            "pandas",
            "prometheus_fastapi_instrumentator",
            "pvlib",
            "pydantic",
            "pymysql",
            "python-jose",
            "sentry_sdk",
            "sqlalchemy",
            "requests",
            "pyarrow",
            "redis",
            "rq",
        ],
        use_scm_version={
            "write_to": "api/solarperformanceinsight_api/_version.py",
            "root": "api/../..",
        },
        setup_requires=["setuptools_scm"],
        entry_points={
            "console_scripts": [
                "spi-sync-jobs=solarperformanceinsight_api.queuing:sync_jobs"
            ]
        },
    )
