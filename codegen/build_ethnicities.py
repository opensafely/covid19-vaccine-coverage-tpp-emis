import csv
import json
import os
from pathlib import Path


def run(spec_path):
    with open(spec_path) as f:
        spec = json.load(f)

    out_path = (
        Path(os.path.abspath(__file__)).parents[1] / "analysis" / "ethnicities.py"
    )

    ethnicities = {
        int(row[0]): row[2] for row in spec["bandings_and_groupings"][2]["rows"]
    }
    ethnicities[20] = "Ethnicity not recorded"

    high_level_ethnicities = {}

    with open("codelists/primis-covid19-vacc-uptake-eth2001.csv") as f:
        for record in csv.DictReader(f):
            category_6 = int(record["grouping_6_id"])
            label_6 = record["grouping_6_label"]
            if category_6 in high_level_ethnicities:
                assert high_level_ethnicities[category_6] == label_6
            else:
                high_level_ethnicities[category_6] = label_6

    high_level_ethnicities[6] = "Unknown"

    with open(out_path, "w") as f:
        f.write(f"ethnicities = {ethnicities}\n\n\n")
        f.write(f"high_level_ethnicities = {high_level_ethnicities}\n")

    os.system(f"black {out_path}")


if __name__ == "__main__":
    import sys

    run(sys.argv[1])
