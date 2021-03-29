from pandas.testing import assert_index_equal, assert_series_equal

from analysis.combine_cumsums import combine_cumsums
from analysis.compute_uptake import compute_uptake
from analysis.transform_fast import load_raw_cohort, transform


def test_combine_cumsums():
    raw_cohort = load_raw_cohort("tests/input.csv")
    cohort = transform(raw_cohort)
    uptake = compute_uptake(cohort, "vacc1_dat", "imd_band")

    # Drop the last two non-total rows and last column
    uptake1 = uptake.drop(uptake.iloc[-3:-1].index).loc[:, 0:4]
    # Drop the first two rows and first column
    uptake2 = uptake.drop(uptake.iloc[:2].index).loc[:, 1:5]

    combined = combine_cumsums(uptake1, uptake2)

    assert_index_equal(combined.index, uptake.index)
    assert list(combined.columns) == [0, 1, 2, 3, 4, 5]

    num_date_rows = len(uptake) - 1

    # Check that all items in first column come from uptake1
    for ix in range(num_date_rows):
        if ix < num_date_rows - 2:
            assert combined[0][ix] == uptake1[0][ix]
        else:
            assert combined[0][ix] == uptake1[0][-2]
    assert combined[0]["total"] == uptake1[0]["total"]

    # Check that all items in last column come from uptake2
    for ix in range(num_date_rows):
        if ix < 2:
            assert combined[5][ix] == 0
        else:
            assert combined[5][ix] == uptake2[5][ix - 2]
    assert combined[5]["total"] == uptake2[5]["total"]

    combined = combined.loc[:, 1:4]
    uptake1 = uptake1.loc[:, 1:4]
    uptake2 = uptake2.loc[:, 1:4]

    # Check all other columns
    for ix in range(num_date_rows):
        if ix < 2:
            # Check the first two rows come from uptake1
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
