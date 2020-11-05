from setuptools import setup, find_packages

if __name__ == "__main__":
    setup(
        name="solarperformanceinsight-api",
        packages=find_packages(),
        install_requires=[],
        use_scm_version={"write_to": "solarperformanceinsight_api/version.py"},
        setup_requires=["setuptools_scm"],
    )
