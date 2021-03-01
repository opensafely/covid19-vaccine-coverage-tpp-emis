import json
import os
import re
from pathlib import Path

import requests


def run(spec_path):
    with open(spec_path) as f:
        spec = json.load(f)

    codelists = get_codelists(spec["extraction_criteria"])

    base_dir = Path(os.path.abspath(__file__)).parents[1]

    with open(base_dir / "analysis" / "codelists.py", "w") as f:
        write_codelists_py(codelists, f)

    with open(base_dir / "codelists" / "codelists.txt", "w") as f:
        write_codelists_txt(codelists, f)


def get_codelists(extraction_criteria):
    codelists = []
    seen = set()

    for r in extraction_criteria:
        if r["details"] == "dm+d code when available":
            continue

        name = r["name"].lower()
        comment = r["title"]

        if name.endswith("_cod"):
            name = name[:-4]

        if name.startswith("eth2001"):
            name = "eth2001"
            comment = "Ethnicity codes"

        if name.startswith("astrx"):
            name = "astrx"
            comment = "Asthma systemic steroid prescription codes"

        if name.startswith("covrx") or re.search("[12]rx", name):
            name = re.sub(r"\d", "", name)
            if name.startswith("covrx"):
                comment = "COVID vaccination medication codes"
            else:
                _, comment = comment.split(" ", 1)
                comment = comment.split(" - ")[0]

        if name in seen:
            continue

        codelists.append([name, comment])
        seen.add(name)

    return codelists


def write_codelists_py(codelists, f):
    f.write("from cohortextractor import codelist_from_csv\n\n\n")

    for name, comment in codelists:
        lines = [
            f"# {comment}",
            f"{name} = codelist_from_csv(",
            f'    "codelists/primis-covid19-vacc-uptake-{name}.csv",',
            f'    system="snomed",',
            '    column="code",',
            ")",
        ]
        if name == "eth2001":
            lines.insert(-1, '    category_column="grouping_16_id",')

        f.write("\n".join(lines))
        f.write("\n\n")


def write_codelists_txt(codelists, f):
    for name, _ in codelists:
        url = f"https://codelists.opensafely.org/codelist/primis-covid19-vacc-uptake/{name}/"
        rsp = requests.get(url)
        f.write("/".join(rsp.url.split("/")[4:7]) + "\n")

if __name__ == "__main__":
    import sys

    run(sys.argv[1])
