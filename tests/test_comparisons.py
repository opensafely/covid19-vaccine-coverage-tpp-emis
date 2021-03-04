import numpy as np
import pandas as pd
from pandas.testing import assert_series_equal

from analysis.comparisons import gt, gte, lt, lte


def test_comparisons():
    #  a | b | gt | gte | lt | lte
    # ---+---+----+-----+----+-----
    #  1 | 1 |  F |  T  |  F |  T
    #  1 | 2 |  F |  F  |  T |  T
    #  2 | 1 |  T |  T  |  F |  F
    #  1 | - |  T |  T  |  F |  F
    #  - | 1 |  F |  F  |  T |  T
    #  - | - |  F |  F  |  F |  F

    # This makes things line up nicely
    T = True
    F = False

    df = pd.DataFrame.from_records(
        [
            (1, 1, F, T, F, T),
            (1, 2, F, F, T, T),
            (2, 1, T, T, F, F),
            (1, 0, T, T, F, F),
            (0, 1, F, F, T, T),
            (0, 0, F, F, F, F),
        ],
        columns=["a", "b", "gt", "gte", "lt", "lte"],
    ).replace(0, np.nan)

    assert_series_equal(gt(df["a"], df["b"]), df["gt"], check_names=False)
    assert_series_equal(gte(df["a"], df["b"]), df["gte"], check_names=False)
    assert_series_equal(lt(df["a"], df["b"]), df["lt"], check_names=False)
    assert_series_equal(lte(df["a"], df["b"]), df["lte"], check_names=False)
