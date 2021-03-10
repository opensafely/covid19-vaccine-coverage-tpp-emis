import csv

from pandas.testing import assert_frame_equal
from pandas.testing import assert_index_equal

from analysis.transform import load_raw_cohort, transform
from analysis.transform_2 import transform_2


def test_transform_2():
    raw_cohort = load_raw_cohort("tests/input.csv")
    cohort = transform(raw_cohort).reset_index(drop=True)

    with open("tests/input.csv") as f:
        reader = csv.DictReader(f)
        cohort_2 = transform_2(reader).reset_index(drop=True)

    cohort_2 = cohort_2[cohort.columns]
    assert_frame_equal(cohort, cohort_2)
