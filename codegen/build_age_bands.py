import json
import os
import re
from pathlib import Path


def run(spec_path):
    with open(spec_path) as f:
        spec = json.load(f)

    out_path = Path(os.path.abspath(__file__)).parents[1] / "analysis" / "age_bands.py"

    age_bands = get_age_bands(spec)

    with open(out_path, "w") as f:
        f.write(
            f"""
import numpy as np


# Mapping from age band to (lower, upper).  The lower limit is inclusive, the upper
# limit is exclusive.
age_bands = {age_bands}

def add_age_bands(df, bands):
    df["age_band"] = np.nan

    for band in bands:
        lower, upper = age_bands[band]
        mask = df["age_band"].isna()
        if lower is not None:
            mask &= lower <= df["age"]
        if upper is not None:
            mask &= df["age"] < upper
        df["age_band"].where(~mask, band, inplace=True)

    assert df["age_band"].all()
    df["age_band"] = df["age_band"].astype(int)
"""
        )

    os.system(f"black {out_path}")


def get_age_bands(spec):
    age_bands = {}

    for ix, row in enumerate(spec["bandings_and_groupings"][0]["row"]):
        if not row[0]:
            continue

        assert row[0].startswith("Band ")
        band = int(row[0][4:])

        criteria = row[1]
        if ix == 0:
            criteria = re.sub(r"defined as.*", "", criteria)
        criteria = criteria.replace(" ", "")

        if m := re.search(r">=(\d+)", criteria):
            lower = int(m.groups()[0])
        else:
            lower = None

        if m := re.search(r"<(\d+)", criteria):
            upper = int(m.groups()[0])
        else:
            upper = None

        if lower and upper:
            assert lower < upper

        age_bands[band] = (lower, upper)

    return age_bands


if __name__ == "__main__":
    import sys

    run(sys.argv[1])
