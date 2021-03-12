import os
import pandas as pd

from compute_uptake import compute_uptake
from groups import at_risk_groups


demographic_cols = [
    "sex",
    "ethnicity",
    "high_level_ethnicity",
    "imd_band",
]
at_risk_cols = ["atrisk_group"] + list(at_risk_groups)
other_cols = ["shield_group", "bmi_group", "preg_group"]

cols = demographic_cols + at_risk_cols + other_cols


def run(input_path="output/cohort.pickle", output_dir="output"):
    backend = os.getenv("OPENSAFELY_BACKEND", "expectations")
    cohort = pd.read_pickle(input_path)

    for wave in range(1, 9 + 1):
        dir_path = f"{output_dir}/{backend}/paper/wave-{wave}"
        os.makedirs(dir_path, exist_ok=True)
        wave_cohort = cohort[cohort["wave"] == wave]
        for col in cols:
            uptake = compute_uptake(wave_cohort, "vacc1_dat", col)
            uptake.to_csv(f"{dir_path}/{col}.csv")


if __name__ == "__main__":
    run()
