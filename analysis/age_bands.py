import numpy as np


# Mapping from age band to (lower, upper).  The lower limit is inclusive, the upper
# limit is exclusive.
age_bands = {
    1: (None, 16),
    2: (16, 30),
    3: (30, 40),
    4: (40, 50),
    5: (50, 55),
    6: (55, 60),
    7: (60, 65),
    8: (65, 70),
    9: (70, 75),
    10: (75, 80),
    11: (80, 85),
    12: (85, 120),
    13: (65, 120),
    14: (16, 40),
    15: (50, 65),
    16: (16, 50),
    17: (65, 75),
    18: (75, None),
}


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
