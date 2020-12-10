import argparse
import difflib
import json
from pathlib import Path
from pprint import pformat
import sys


import pandas as pd
from pvlib.pvsystem import retrieve_sam
from solarperformanceinsight_api.main import app
from solarperformanceinsight_api.models import SandiaInverterParameters


dashdir = Path(__file__).parent / "dashboard"
OPENAPI_PATH = dashdir / "tests/unit/openapi.json"
INVERTERS_PATH = dashdir / "src/assets/inverters.json"


def printdiff(old, new):
    print(
        "\n".join(
            list(
                difflib.context_diff(
                    pformat(old, sort_dicts=False).split("\n"),
                    pformat(new, sort_dicts=False).split("\n"),
                    lineterm="",
                    fromfile="current",
                    tofile="latest",
                )
            )
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract API files for dashboard consumption"
    )
    parser.add_argument("--check", action="store_true", help="Check for file changes")
    args = parser.parse_args()

    new_openapi = app.openapi()
    inverter_df = retrieve_sam("CECInverter")
    inv_param_keys = SandiaInverterParameters.schema()["properties"].keys()
    inverters = inverter_df.loc[inv_param_keys].astype(float)

    if args.check:
        ecode = 0
        if not OPENAPI_PATH.is_file():
            print("OpenAPI spec does not exist")
            ecode = 1
        else:
            old_openapi = json.loads(OPENAPI_PATH.read_text())
            if old_openapi != new_openapi:
                print("OpenAPI spec out of date")
                printdiff(old_openapi, new_openapi)
                ecode = 1
        if not INVERTERS_PATH.is_file():
            print("Inverter spec does not exist")
            ecode = 1
        else:
            old_inv = pd.read_json(INVERTERS_PATH.read_text())
            try:
                pd.testing.assert_frame_equal(
                    inverters, old_inv, check_exact=False, check_like=True
                )
            except AssertionError as e:
                print("Inverter spec out of date")
                print(e)
                ecode = 1
        sys.exit(ecode)
    else:
        with OPENAPI_PATH.open("w") as f:
            json.dump(new_openapi, f, separators=(",", ":"))
            f.write("\n")
        with INVERTERS_PATH.open("w") as f:
            f.write(inverters.to_json(double_precision=8))
            f.write("\n")
