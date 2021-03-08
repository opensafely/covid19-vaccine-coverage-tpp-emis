import json
import os
from pathlib import Path


def run(spec_path):
    with open(spec_path) as f:
        spec = json.load(f)

    groups = {
        g["banding_key"].lower().rstrip("*"): g["banding_name"]
        for g in spec["bandings_and_groupings"][3:]
    }

    out_path = Path(os.path.abspath(__file__)).parents[1] / "analysis" / "groups.py"

    with open(out_path, "w") as f:
        f.write(f"groups = {groups}")

    os.system(f"black {out_path}")


if __name__ == "__main__":
    import sys

    run(sys.argv[1])
