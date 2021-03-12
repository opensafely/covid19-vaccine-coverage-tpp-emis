import numpy as np
import pandas as pd

from analysis.transform import load_raw_cohort, transform


def test_drop_non_fm_sex():
    raw_cohort = load_raw_cohort("tests/input.csv")
    cohort = transform(raw_cohort)

    raw_sex_counts = raw_cohort["sex"].value_counts()
    sex_counts = cohort["sex"].value_counts()

    assert set(sex_counts.index) == {"F", "M"}
    assert sex_counts["F"] == raw_sex_counts["F"]
    assert sex_counts["M"] == raw_sex_counts["M"]


def test_add_imd_bands():
    raw_cohort = load_raw_cohort("tests/input.csv")
    cohort = transform(raw_cohort)

    for ix, row in cohort.iterrows():
        if pd.isnull(row["imd"]):
            assert row["imd_band"] == 0
        elif row["imd"] <= 32844 * 0.2:
            assert row["imd_band"] == 1
        elif row["imd"] <= 32844 * 0.4:
            assert row["imd_band"] == 2
        elif row["imd"] <= 32844 * 0.6:
            assert row["imd_band"] == 3
        elif row["imd"] <= 32844 * 0.8:
            assert row["imd_band"] == 4
        else:
            assert row["imd_band"] == 5


def test_add_ethnicity():
    raw_cohort = load_raw_cohort("tests/input.csv")
    cohort = transform(raw_cohort)

    for ix, row in cohort.iterrows():
        if row["eth2001"] <= 16:
            assert row["ethnicity"] == row["eth2001"]
        elif pd.notnull(row["non_eth2001_dat"]):
            assert row["ethnicity"] == 17
        elif pd.notnull(row["eth_notgiptref_dat"]):
            assert row["ethnicity"] == 18
        elif pd.notnull(row["eth_notstated_dat"]):
            assert row["ethnicity"] == 19
        else:
            assert row["ethnicity"] == 20


def test_add_high_level_ethnicity():
    raw_cohort = load_raw_cohort("tests/input.csv")
    cohort = transform(raw_cohort)

    for ix, row in cohort.iterrows():
        if row["eth2001"] <= 3:
            assert row["high_level_ethnicity"] == 1
        elif row["eth2001"] <= 7:
            assert row["high_level_ethnicity"] == 2
        elif row["eth2001"] <= 11:
            assert row["high_level_ethnicity"] == 3
        elif row["eth2001"] <= 14:
            assert row["high_level_ethnicity"] == 4
        elif row["eth2001"] <= 16:
            assert row["high_level_ethnicity"] == 5
        else:
            assert row["high_level_ethnicity"] == 6


def test_add_vacc_dates():
    raw_cohort = load_raw_cohort("tests/input.csv")
    cohort = transform(raw_cohort)

    for ix, row in cohort.iterrows():
        vacc1_dates = []
        if pd.notnull(row["covadm1_dat"]):
            vacc1_dates.append(row["covadm1_dat"])
        if pd.notnull(row["covrx1_dat"]):
            vacc1_dates.append(row["covrx1_dat"])

        if vacc1_dates:
            assert row["vacc1_dat"] == min(vacc1_dates)

        vacc2_dates = []
        if pd.notnull(row["covadm2_dat"]):
            vacc2_dates.append(row["covadm2_dat"])
        if pd.notnull(row["covrx2_dat"]):
            vacc2_dates.append(row["covrx2_dat"])

        if vacc2_dates:
            assert row["vacc2_dat"] == min(vacc2_dates)


def test_add_age_bands():
    raw_cohort = load_raw_cohort("tests/input.csv")
    cohort = transform(raw_cohort)

    for ix, row in cohort.iterrows():
        if row["age"] < 16:
            assert row["age_band"] == 1
        elif row["age"] < 30:
            assert row["age_band"] == 2
        elif row["age"] < 40:
            assert row["age_band"] == 3
        elif row["age"] < 50:
            assert row["age_band"] == 4
        elif row["age"] < 55:
            assert row["age_band"] == 5
        elif row["age"] < 60:
            assert row["age_band"] == 6
        elif row["age"] < 65:
            assert row["age_band"] == 7
        elif row["age"] < 70:
            assert row["age_band"] == 8
        elif row["age"] < 75:
            assert row["age_band"] == 9
        elif row["age"] < 80:
            assert row["age_band"] == 10
        elif row["age"] < 85:
            assert row["age_band"] == 11
        else:
            assert row["age_band"] == 12


def test_add_groupings():
    raw_cohort = load_raw_cohort("tests/input.csv")
    cohort = transform(raw_cohort)

    for ix, row in cohort.iterrows():
        # IF ASTADM_DAT <> NULL | Select | Next
        if pd.notnull(row["astadm_dat"]):
            assert row["ast_group"]
            continue

        # IF AST_DAT <> NULL    | Next   | Reject
        if pd.isnull(row["ast_dat"]):
            assert not row["ast_group"]
            continue

        # IF ASTRXM1 <> NULL    | Next   | Reject
        if pd.isnull(row["astrxm1_dat"]):
            assert not row["ast_group"]
            continue

        # IF ASTRXM2 <> NULL    | Next   | Reject
        if pd.isnull(row["astrxm2_dat"]):
            assert not row["ast_group"]
            continue

        # IF ASTRXM3 <> NULL    | Select | Reject
        if pd.notnull(row["astrxm3_dat"]):
            assert row["ast_group"]
        else:
            assert not row["ast_group"]
