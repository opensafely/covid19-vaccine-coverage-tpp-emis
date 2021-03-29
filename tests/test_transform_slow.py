import csv

from pandas.testing import assert_frame_equal

from analysis.transform_fast import (
    load_raw_cohort,
    necessary_cols,
    transform as transform_fast,
)
from analysis.transform_slow import transform as transform_slow


def test_transform_slow():
    raw_cohort = load_raw_cohort("tests/input.csv")
    cohort = transform_fast(raw_cohort).reset_index(drop=True)[necessary_cols]

    with open("tests/input.csv") as f:
        reader = csv.DictReader(f)
        cohort_2 = transform_slow(reader).reset_index(drop=True)

    cohort_2 = cohort_2[cohort.columns]
    assert_frame_equal(cohort, cohort_2)
