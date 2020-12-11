import argparse
import difflib
import json
from pathlib import Path
from pprint import pformat
import sys


from solarperformanceinsight_api.main import app


dashdir = Path(__file__).parent / "dashboard"
OPENAPI_PATH = dashdir / "tests/unit/openapi.json"


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
    new_openapi["info"]["version"] = "1"

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
        sys.exit(ecode)
    else:
        with OPENAPI_PATH.open("w") as f:
            json.dump(new_openapi, f, separators=(",", ":"))
            f.write("\n")
