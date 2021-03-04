import numpy as np
import pandas as pd

from analysis.transform import load_raw_cohort, transform


def test_immuno_group():
    raw_cohort = load_raw_cohort("tests/input.csv")
    cohort = transform(raw_cohort)

    for ix, row in cohort.iterrows():
        # IF IMMRX_DAT <> NULL     | Select | Next
        if pd.notnull(row["immrx_dat"]):
            assert row["immuno_group"]
            continue

        # IF IMMDX_COV_DAT <> NULL | Select | Reject
        if pd.notnull(row["immdx_cov_dat"]):
            assert row["immuno_group"]
        else:
            assert not row["immuno_group"]


def test_ckd_group():
    raw_cohort = load_raw_cohort("tests/input.csv")
    cohort = transform(raw_cohort)

    for ix, row in cohort.iterrows():
        # IF CKD_COV_DAT <> NULL (diagnoses) | Select | Next
        if pd.notnull(row["ckd_cov_dat"]):
            assert row["ckd_group"]
            continue

        # IF CKD15_DAT = NULL  (No stages)   | Reject | Next
        if pd.isnull(row["ckd15_dat"]):
            assert not row["ckd_group"]
            continue

        # IF CKD35_DAT>=CKD15_DAT            | Select | Reject
        if gte(row["ckd35_dat"], row["ckd15_dat"]):
            assert row["ckd_group"]
        else:
            assert not row["ckd_group"]


def test_ast_group():
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


def test_cns_group():
    raw_cohort = load_raw_cohort("tests/input.csv")
    cohort = transform(raw_cohort)

    for ix, row in cohort.iterrows():
        # IF CNS_COV_DAT <> NULL | Select | Reject
        if pd.notnull(row["cns_cov_dat"]):
            assert row["cns_group"]
        else:
            assert not row["cns_group"]


def test_resp_group():
    raw_cohort = load_raw_cohort("tests/input.csv")
    cohort = transform(raw_cohort)

    for ix, row in cohort.iterrows():
        # IF AST_GROUP <> NULL    | Select | Next
        if row["ast_group"]:
            assert row["resp_group"]
            continue

        # IF RESP_COV_DAT <> NULL | Select | Reject
        if pd.notnull(row["resp_cov_dat"]):
            assert row["resp_group"]
        else:
            assert not row["resp_group"]


def test_bmi_group():
    raw_cohort = load_raw_cohort("tests/input.csv")
    cohort = transform(raw_cohort)

    for ix, row in cohort.iterrows():
        # IF SEV_OBESITY_DAT > BMI_DAT | Select | Next
        if gt(row["sev_obesity_dat"], row["bmi_dat"]):
            assert row["bmi_group"]
            continue

        # IF BMI_VAL >=40              | Select | Reject
        if gte(row["bmi_val"], 40):
            assert row["bmi_group"]
        else:
            assert not row["bmi_group"]


def test_diab_group():
    raw_cohort = load_raw_cohort("tests/input.csv")
    cohort = transform(raw_cohort)

    for ix, row in cohort.iterrows():
        # IF DIAB_DAT > DMRES_DAT | Select | Reject
        if gt(row["diab_dat"], row["dmres_dat"]):
            assert row["diab_group"]
        else:
            assert not row["diab_group"]


def test_sevment_group():
    raw_cohort = load_raw_cohort("tests/input.csv")
    cohort = transform(raw_cohort)

    for ix, row in cohort.iterrows():
        # IF SEV_MENTAL_DAT > SMHRES_DAT | Select | Reject
        if gt(row["sev_mental_dat"], row["smhres_dat"]):
            assert row["sevment_group"]
        else:
            assert not row["sevment_group"]


def test_atrisk_group():
    raw_cohort = load_raw_cohort("tests/input.csv")
    cohort = transform(raw_cohort)

    for ix, row in cohort.iterrows():
        # IF IMMUNOGROUP <> NULL   | Select | Next
        if row["immuno_group"]:
            assert row["atrisk_group"]
            continue

        # IF CKD_GROUP <> NULL     | Select | Next
        if row["ckd_group"]:
            assert row["atrisk_group"]
            continue

        # IF RESP_GROUP <> NULL    | Select | Next
        if row["resp_group"]:
            assert row["atrisk_group"]
            continue

        # IF DIAB_GROUP <> NULL    | Select | Next
        if row["diab_group"]:
            assert row["atrisk_group"]
            continue

        # IF CLD_DAT <>NULL        | Select | Next
        if pd.notnull(row["cld_dat"]):
            assert row["atrisk_group"]
            continue

        # IF CNS_GROUP <> NULL     | Select | Next
        if row["cns_group"]:
            assert row["atrisk_group"]
            continue

        # IF CHD_COV_DAT <> NULL   | Select | Next
        if pd.notnull(row["chd_cov_dat"]):
            assert row["atrisk_group"]
            continue

        # IF SPLN_COV_DAT <> NULL  | Select | Next
        if pd.notnull(row["spln_cov_dat"]):
            assert row["atrisk_group"]
            continue

        # IF LEARNDIS_DAT <> NULL  | Select | Next
        if pd.notnull(row["learndis_dat"]):
            assert row["atrisk_group"]
            continue

        # IF SEVMENT_GROUP <> NULL | Select | Reject
        if row["sevment_group"]:
            assert row["atrisk_group"]
        else:
            assert not row["atrisk_group"]


def test_covax1d_group():
    raw_cohort = load_raw_cohort("tests/input.csv")
    cohort = transform(raw_cohort)

    for ix, row in cohort.iterrows():
        # IF COVRX1_DAT <> NULL  | Select | Next
        if pd.notnull(row["covrx1_dat"]):
            assert row["covax1d_group"]
            continue

        # IF COVADM1_DAT <> NULL | Select | Reject
        if pd.notnull(row["covadm1_dat"]):
            assert row["covax1d_group"]
        else:
            assert not row["covax1d_group"]


def test_covax2d_group():
    raw_cohort = load_raw_cohort("tests/input.csv")
    cohort = transform(raw_cohort)

    for ix, row in cohort.iterrows():
        # IF COVAX1D_GROUP <> NULL | Next   | Reject
        if not row["covax1d_group"]:
            assert not row["covax2d_group"]
            continue

        # IF COVRX2_DAT <> NULL    | Select | Next
        if pd.notnull(row["covrx2_dat"]):
            assert row["covax2d_group"]
            continue

        # IF COVADM2_DAT <> NULL   | Select | Reject
        if pd.notnull(row["covadm2_dat"]):
            assert row["covax2d_group"]
        else:
            assert not row["covax2d_group"]


def test_unstatvacc1_group():
    raw_cohort = load_raw_cohort("tests/input.csv")
    cohort = transform(raw_cohort)

    for ix, row in cohort.iterrows():
        # IF COVAX1D_GROUP <> NULL | Next   | Reject
        if not row["covax1d_group"]:
            assert not row["unstatvacc1_group"]
            continue

        # IF AZD1RX_DAT <> NULL    | Reject | Next
        if pd.notnull(row["azd1rx_dat"]):
            assert not row["unstatvacc1_group"]
            continue

        # IF PFD1RX_DAT <> NULL    | Reject | Next
        if pd.notnull(row["pfd1rx_dat"]):
            assert not row["unstatvacc1_group"]
            continue

        # IF MOD1RX_DAT <> NULL    | Reject | Next
        if pd.notnull(row["mod1rx_dat"]):
            assert not row["unstatvacc1_group"]
            continue

        # IF NXD1RX_DAT <> NULL    | Reject | Next
        if pd.notnull(row["nxd1rx_dat"]):
            assert not row["unstatvacc1_group"]
            continue

        # IF JND1RX _DAT <> NULL   | Reject | Next
        if pd.notnull(row["jnd1rx_dat"]):
            assert not row["unstatvacc1_group"]
            continue

        # IF GSD1RX_DAT <> NULL    | Reject | Next
        if pd.notnull(row["gsd1rx_dat"]):
            assert not row["unstatvacc1_group"]
            continue

        # IF VLD1RX_DAT <> NULL    | Reject | Select
        if pd.notnull(row["vld1rx_dat"]):
            assert not row["unstatvacc1_group"]
        else:
            assert row["unstatvacc1_group"]


def test_unstatvacc2_group():
    raw_cohort = load_raw_cohort("tests/input.csv")
    cohort = transform(raw_cohort)

    for ix, row in cohort.iterrows():
        # IF COVAX2D_GROUP <> NULL | Next   | Reject
        if not row["covax2d_group"]:
            assert not row["unstatvacc2_group"]
            continue

        # IF AZD2RX_DAT <> NULL    | Reject | Next
        if pd.notnull(row["azd2rx_dat"]):
            assert not row["unstatvacc2_group"]
            continue

        # IF PFD2RX_DAT <> NULL    | Reject | Next
        if pd.notnull(row["pfd2rx_dat"]):
            assert not row["unstatvacc2_group"]
            continue

        # IF MOD2RX_DAT <> NULL    | Reject | Next
        if pd.notnull(row["mod2rx_dat"]):
            assert not row["unstatvacc2_group"]
            continue

        # IF NXD2RX_DAT <> NULL    | Reject | Next
        if pd.notnull(row["nxd2rx_dat"]):
            assert not row["unstatvacc2_group"]
            continue

        # IF JND2RX _DAT <> NULL   | Reject | Next
        if pd.notnull(row["jnd2rx_dat"]):
            assert not row["unstatvacc2_group"]
            continue

        # IF GSD2RX_DAT <> NULL    | Reject | Next
        if pd.notnull(row["gsd2rx_dat"]):
            assert not row["unstatvacc2_group"]
            continue

        # IF VLD2RX_DAT <> NULL    | Reject | Select
        if pd.notnull(row["vld2rx_dat"]):
            assert not row["unstatvacc2_group"]
        else:
            assert row["unstatvacc2_group"]


def test_shield_group():
    raw_cohort = load_raw_cohort("tests/input.csv")
    cohort = transform(raw_cohort)

    for ix, row in cohort.iterrows():
        # IF SHIELD_DAT = NULL                           | Reject | Next
        if pd.isnull(row["shield_dat"]):
            assert not row["shield_group"]
            continue

        # IF SHIELD_DAT <> NULL AND NONSHIELD_DAT = NULL | Select | Next
        if (pd.notnull(row["shield_dat"])) & (pd.isnull(row["nonshield_dat"])):
            assert row["shield_group"]
            continue

        # IF SHIELD_DAT > NONSHIELD_DAT                  | Select | Reject
        if gt(row["shield_dat"], row["nonshield_dat"]):
            assert row["shield_group"]
        else:
            assert not row["shield_group"]


def test_preg_group():
    raw_cohort = load_raw_cohort("tests/input.csv")
    cohort = transform(raw_cohort)

    for ix, row in cohort.iterrows():
        # IF PREG_DAT<> NULL        | Next   | Reject
        if pd.isnull(row["preg_dat"]):
            assert not row["preg_group"]
            continue

        # IF PREGDEL_DAT > PREG_DAT | Reject | Select
        if gt(row["pregdel_dat"], row["preg_dat"]):
            assert not row["preg_group"]
        else:
            assert row["preg_group"]


def gt(lhs, rhs):
    if pd.isna(lhs):
        return False

    if pd.isna(rhs):
        return True

    return lhs > rhs


def gte(lhs, rhs):
    if pd.isna(lhs):
        return False

    if pd.isna(rhs):
        return True

    return lhs >= rhs
