import pandas as pd


def combine_cumsums(df1, df2):
    df1 = df1.copy()
    df2 = df2.copy()
    for col in df1.columns:
        if col not in df2.columns:
            df2[col] = 0
    for col in df2.columns:
        if col not in df1.columns:
            df1[col] = 0

    dates1 = list(df1.index)[:-1]
    earliest1, latest1 = min(dates1), max(dates1)
    dates2 = list(df2.index)[:-1]
    earliest2, latest2 = min(dates2), max(dates2)

    earliest, latest = min(earliest1, earliest2), max(latest1, latest2)
    index = [str(date.date()) for date in pd.date_range(earliest, latest)] + ["total"]

    df = pd.DataFrame(index=index, columns=df1.columns).fillna(0).astype(int)

    for date in index:
        if date in df1.index:
            df.loc[date] += df1.loc[date]
        elif date > latest1:
            df.loc[date] += df1.loc[latest1]

        if date in df2.index:
            df.loc[date] += df2.loc[date]
        elif date > latest2:
            df.loc[date] += df2.loc[latest2]

    return df
