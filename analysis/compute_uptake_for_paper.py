import os
import pandas as pd

from compute_uptake import compute_uptake
from groups import at_risk_groups


def run(input_path="output/cohort.pickle", output_dir="output"):
    backend = os.getenv("OPENSAFELY_BACKEND", "expectations")
    cohort = pd.read_pickle(input_path)

    cols = [
        "sex",
        "ethnicity",
        "high_level_ethnicity",
        "imd_band",
        "shield_group",
        "atrisk_group",
    ]
    cols += list(at_risk_groups)
    cols += ["bmi_group", "preg_group"]

    for wave in range(1, 9 + 1):
        dir_path = f"{output_dir}/{backend}/paper/wave-{wave}"
        os.makedirs(dir_path, exist_ok=True)
        wave_cohort = cohort[cohort["wave"] == wave]
        for col in cols:
            uptake = compute_uptake(wave_cohort, "vacc1_dat", col)
            uptake.to_csv(f"{dir_path}/{col}.csv")


if __name__ == "__main__":
    run()
