import csv
from tempfile import NamedTemporaryFile

import pandas as pd

from age_bands import age_bands
from add_groupings_2 import add_groupings_2
from transform import extra_at_risk_cols, extra_vacc_cols, necessary_cols


def run(input_path="output/input.csv", output_path="output/cohort.pickle"):
    with open(input_path) as f:
        reader = csv.DictReader(f)
        cohort = transform_2(reader)
    cohort.to_pickle(output_path)


def transform_2(reader):
    with NamedTemporaryFile("w+") as f:
        writer = csv.DictWriter(f, necessary_cols)
        writer.writeheader()
        for row in transform_rows(reader):
            writer.writerow(row)

        f.seek(0)

        # We set parse_dates and dtype to ensure that the returned dataframe is
        # identical to that returned by the original transform.
        date_fieldnames = [
            fn
            for fn in necessary_cols
            if fn.endswith("_dat") and fn not in extra_vacc_cols
        ]
        dtypes = {
            "ethnicity": "int8",
            "high_level_ethnicity": "int8",
        }
        cohort = pd.read_csv(f.name, parse_dates=date_fieldnames, dtype=dtypes)

    return cohort


def transform_rows(rows):
    for ix, row in enumerate(rows):
        if non_fm_sex(row):
            continue
        if over_120_age(row):
            continue

        add_imd_bands(row)
        add_ethnicity(row)
        add_high_level_ethnicity(row)
        add_missing_vacc_columns(row)
        add_vacc_dates(row)
        add_age_bands(row, range(1, 12 + 1))
        add_groupings_2(row)
        add_waves(row)
        add_extra_at_risk_cols(row)
        row = {k: v for k, v in row.items() if k in necessary_cols}
        yield row


def non_fm_sex(row):
    """Return True if sex is not F or M."""

    return row["sex"] not in ["F", "M"]


def over_120_age(row):
    """Return True if age is >= 120.

    There are a handful of patients with a recorded date of birth of 1900-01-01.
    """

    return int(row["age"]) >= 120


def add_imd_bands(row):
    """Add IMD band from 1 (most deprived) to 5 (least deprived), or 0 if missing."""

    if not row["imd"]:
        row["imd_band"] = 0
        return

    for band in range(1, 5 + 1):
        if int(row["imd"]) < band * 32844 / 5:
            row["imd_band"] = band
            return


def add_ethnicity(row):
    """Add ethnicity using bandings from PRIMIS spec."""

    if row["eth2001"]:
        # eth2001 already indicates whether a patient is in any of bands 1-16
        row["ethnicity"] = int(row["eth2001"])

    elif row["non_eth2001_dat"]:
        # Add band 17 (Patients with any other ethnicity code)
        row["ethnicity"] = 17

    elif row["eth_notgiptref_dat"]:
        # Add band 18 (Ethnicity not given - patient refused)
        row["ethnicity"] = 18

    elif row["eth_notstated_dat"]:
        # Add band 19 (Ethnicity not stated)
        row["ethnicity"] = 19

    else:
        # Add band 20 (Ethnicity not recorded)
        row["ethnicity"] = 20


def add_high_level_ethnicity(row):
    """Add high-level ethnicity categories, based on bandings from PRIMIS spec."""

    # Get mapping from category (1-16) to high-level category (1-5)
    category_to_high_level_category = {}
    with open("codelists/primis-covid19-vacc-uptake-eth2001.csv") as f:
        for record in csv.DictReader(f):
            category = int(record["grouping_16_id"])
            high_level_category = int(record["grouping_6_id"])

            if category in category_to_high_level_category:
                assert category_to_high_level_category[category] == high_level_category
            else:
                category_to_high_level_category[category] = high_level_category

    # Set high_level_ethnicity based on ethnicity column
    row["high_level_ethnicity"] = category_to_high_level_category.get(
        row["ethnicity"], 6  # 6 is "unknown"
    )


def add_missing_vacc_columns(row):
    """Add columns for vaccines that are not yet available but which are referenced by
    the spec.
    """

    for prefix in ["mo", "nx", "jn", "gs", "vl"]:
        assert f"{prefix}d1rx_dat" not in row
        assert f"{prefix}d2rx_dat" not in row
        row[f"{prefix}d1rx_dat"] = ""
        row[f"{prefix}d2rx_dat"] = ""


def add_vacc_dates(row):
    """Record earliest date of first and second vaccinations.

    In some cases, a patient will have only one covadm1/2_dat and covrx1/2_dat.
    """

    for ix in 1, 2:
        covadm_dat = row[f"covadm{ix}_dat"]
        covrx_dat = row[f"covrx{ix}_dat"]
        vacc_dat_fn = f"vacc{ix}_dat"

        if covadm_dat and covrx_dat:
            row[vacc_dat_fn] = min(covadm_dat, covrx_dat)
        elif covadm_dat:
            row[vacc_dat_fn] = covadm_dat
        else:
            row[vacc_dat_fn] = covrx_dat


def add_age_bands(row, bands):
    for band in bands:
        lower, upper = age_bands[band]
        if lower is None:
            lower = -1
        if upper is None:
            upper = 999
        if lower <= int(row["age"]) < upper:
            row["age_band"] = band
            return

    assert False


def add_waves(row):
    age = int(row["age"])

    if row["longres_dat"]:
        # Wave 1: Residents in Care Homes
        # (The spec includes staff in care homes, but occupation codes are not well
        # recorded)
        row["wave"] = 1

    elif age >= 80:
        # Wave 2: Age 80 or over
        # (This spec includes frontline H&SC workers, but see above.)
        row["wave"] = 2

    elif 75 <= age <= 79:
        # Wave 3: Age 75 - 79
        row["wave"] = 3

    elif row["shield_group"] or (70 <= age <= 74):
        # Wave 4: Clinically Extremely Vulnerable or age 70 - 74
        row["wave"] = 4

    elif 65 <= age <= 69:
        # Wave 5: Age 65 - 69
        row["wave"] = 5

    elif (16 <= age <= 64) and row["atrisk_group"]:
        # Wave 6: Age 16-64 in a defined At Risk group
        row["wave"] = 6

    elif 60 <= age <= 64:
        # Wave 7: Age 60 - 64
        row["wave"] = 7

    elif 55 <= age <= 59:
        # Wave 8: Age 55 - 59
        row["wave"] = 8

    elif 50 <= age <= 54:
        # Wave 9: Age 50 - 54
        row["wave"] = 9

    else:
        row["wave"] = 0


def add_extra_at_risk_cols(row):
    """Add columns for extra at-risk groups."""

    for col in extra_at_risk_cols:
        date_col = col.replace("_group", "_dat")
        if date_col in row:
            row[col] = bool(row[date_col])


if __name__ == "__main__":
    import sys

    run(input_path=sys.argv[1])
