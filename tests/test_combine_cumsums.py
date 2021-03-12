from pandas.testing import assert_index_equal, assert_series_equal

from analysis.combine_cumsums import combine_cumsums
from analysis.compute_uptake import compute_uptake
from analysis.transform import load_raw_cohort, transform


def test_combine_cumsums():
    raw_cohort = load_raw_cohort("tests/input.csv")
    cohort = transform(raw_cohort)
    uptake = compute_uptake(cohort, "vacc1_dat", "sex")
    # Drop the last two non-total rows
    uptake1 = uptake.drop(uptake.iloc[-3:-1].index)
    # Drop the first two rows
    uptake2 = uptake.drop(uptake.iloc[:2].index)
    combined = combine_cumsums(uptake1, uptake2)

    assert_index_equal(combined.index, uptake.index)

    num_date_rows = len(uptake) - 1
    for ix in range(num_date_rows):
        if ix < 2:
            # Check the first two rwos come from uptake1
            assert_series_equal(combined.iloc[ix], uptake1.iloc[ix])
        elif ix < num_date_rows - 2:
            assert_series_equal(
                combined.iloc[ix], uptake1.iloc[ix] + uptake2.iloc[ix - 2]
            )
        else:
            # Check the last two rows come from adding the last value of uptake1 with
            # the corresponding value of uptake2.
            assert_series_equal(
                combined.iloc[ix],
                uptake1.iloc[-2] + uptake2.iloc[ix - 2],
                check_names=False,
            )

    assert_series_equal(
        combined.loc["total"], uptake1.loc["total"] + uptake2.loc["total"]
    )
