import json
import os
import re
from pathlib import Path


def run(spec_path):
    with open(spec_path) as f:
        spec = json.load(f)

    groups = {
        g["banding_key"].lower().rstrip("*"): g["banding_name"]
        for g in spec["bandings_and_groupings"][3:]
    }

    at_risk_groups = {}

    for g in spec["bandings_and_groupings"][3:]:
        if g["banding_key"] != "ATRISK_GROUP":
            continue
        for row in g["rows"]:
            condition = row[0].replace(" ", "")
            col_name = re.match("IF(\w+)<>NULL", condition).groups()[0]
            # eg s/IMMUNOGROUP/IMMUNO_GROUP/
            col_name = re.sub("([^_])GROUP", r"\1_GROUP", col_name)
            col_name = col_name.lower()
            group = col_name.replace("_dat", "_group")
            if group in groups:
                name =  groups[group]
            else:
                name = ""
                for criteria in spec["extraction_criteria"]:
                    if criteria["name"].lower().replace("_cod", "_group") == group:
                        name = "Patients with " + criteria["title"]
                        if name.endswith(" codes"):
                            name = name[:-6]
            at_risk_groups[group] = name

    out_path = Path(os.path.abspath(__file__)).parents[1] / "analysis" / "groups.py"

    with open(out_path, "w") as f:
        f.write(f"groups = {groups}\n\n\n")
        f.write(f"at_risk_groups = {at_risk_groups}\n")

    os.system(f"black {out_path}")


if __name__ == "__main__":
    import sys

    run(sys.argv[1])
