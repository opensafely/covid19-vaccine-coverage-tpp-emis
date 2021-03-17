import os
import pandas as pd

from groups import groups


def run(input_path="output/cohort.pickle", output_dir="output"):
    """Produce dataframes computing uptake stratified by age band, sex, and high-level
    ethnicity codes, for the whole population and for each clinical subgroup in the
    PRIMIS spec.
    """

    backend = os.getenv("OPENSAFELY_BACKEND", "expectations")

    cohort = pd.read_pickle(input_path)
    demographic_cols = ["age_band", "sex", "high_level_ethnicity"]
    group_cols = [
        group for group in groups if "covax" not in group and "unstatvacc" not in group
    ]

    for col in demographic_cols:
        path = f"{output_dir}/coverage_by_{col}_{backend}.csv"
        compute_uptake(cohort, "vacc1_dat", col).to_csv(path)

        for group_col in group_cols:
            group_cohort = cohort[cohort[group_col]]
            path = f"{output_dir}/coverage_for_{group_col}_by_{col}_{backend}.csv"
            compute_uptake(group_cohort, "vacc1_dat", col).to_csv(path)

    for col in group_cols:
        path = f"{output_dir}/coverage_by_{col}_{backend}.csv"
        compute_uptake(cohort, "vacc1_dat", col).to_csv(path)


def compute_uptake(cohort, event_col, stratification_col):
    stratification_series = cohort[stratification_col]
    stratification_vals = sorted(stratification_series.value_counts().index)

    event_dates = cohort[cohort[event_col].notnull()][event_col]
    if event_dates.empty:
        return

    earliest, latest = min(event_dates), max(event_dates)
    index = [str(date.date()) for date in pd.date_range(earliest, latest)]

    uptake = pd.DataFrame(index=index)

    for stratification_val in stratification_vals:
        filtered = cohort[stratification_series == stratification_val]
        series = pd.Series(0, index=index)
        for date, count in filtered[event_col].value_counts().iteritems():
            series[str(date.date())] = count
        uptake[stratification_val] = series.cumsum()

    uptake.loc["total"] = stratification_series.value_counts()
    uptake.fillna(0, inplace=True)
    return ((uptake // 7) * 7).astype(int)


if __name__ == "__main__":
    run()
