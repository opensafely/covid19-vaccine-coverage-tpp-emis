import os

import pandas as pd


def run(input_path="output/cohort.pickle", output_path="output/prevalences.pickle"):
    backend = os.getenv("OPENSAFELY_BACKEND", "expectations")
    output_path = output_path[:-7] + f"_{backend}" + ".pickle"

    cohort = pd.read_pickle(input_path)
    prevalences = count_prevalences(cohort)
    prevalences.to_pickle(output_path)


def count_prevalences(cohort):
    prevalences = pd.DataFrame(
        {"total": cohort.groupby(["age_band", "sex"])["patient_id"].count()}
    )

    for col in cohort.columns:
        if not col.endswith("_group"):
            continue

        prevalences[col] = (
            cohort[cohort[col]].groupby(["age_band", "sex"])["patient_id"].count()
        )

    for high_level_ethnicity_category in [1, 2, 3, 4, 5, 6]:
        prevalences[f"ethnicity_{high_level_ethnicity_category}"] = (
            cohort[cohort["high_level_ethnicity"] == high_level_ethnicity_category]
            .groupby(["age_band", "sex"])["patient_id"]
            .count()
        )

    prevalences.fillna(0, inplace=True)
    return ((prevalences // 7) * 7).astype(int)


if __name__ == "__main__":
    run()
