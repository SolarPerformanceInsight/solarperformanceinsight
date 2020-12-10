import argparse
import json
from pathlib import Path
import sys


from pvlib.pvsystem import retrieve_sam
from solarperformanceinsight_api.main import app
from solarperformanceinsight_api.models import SandiaInverterParameters


dashdir = Path(__file__).parent / "dashboard"
OPENAPI_PATH = dashdir / "tests/unit/openapi.json"
INVERTERS_PATH = dashdir / "src/assets/inverters.json"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract API files for dashboard consumption"
    )
    parser.add_argument("--check", action="store_true", help="Check for file changes")
    args = parser.parse_args()

    new_openapi = app.openapi()
    inverter_df = retrieve_sam("CECInverter")
    inv_param_keys = SandiaInverterParameters.schema()["properties"].keys()
    inverter_json = inverter_df.loc[inv_param_keys].to_json()

    if args.check:
        ecode = 0
        if not OPENAPI_PATH.is_file() or new_openapi != json.loads(
            OPENAPI_PATH.read_text()
        ):
            print("OpenAPI spec out of date")
            ecode = 1
        if (
            not INVERTERS_PATH.is_file()
            or inverter_json != INVERTERS_PATH.read_text().rstrip("\n")
        ):
            print("Inverter specs out of date")
            ecode = 1
        sys.exit(ecode)
    else:
        with OPENAPI_PATH.open("w") as f:
            json.dump(new_openapi, f, separators=(",", ":"))
            f.write("\n")
        with INVERTERS_PATH.open("w") as f:
            f.write(inverter_json)
            f.write("\n")
