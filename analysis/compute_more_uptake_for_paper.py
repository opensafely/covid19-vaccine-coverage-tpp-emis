import os
import pandas as pd

from compute_uptake import compute_uptake


def run(input_path="output/cohort.pickle", output_dir="output"):
    backend = os.getenv("OPENSAFELY_BACKEND", "expectations")
    cohort = pd.read_pickle(input_path)
    uptake = compute_uptake(cohort, "vacc1_dat", "wave")
    os.makedirs(f"{output_dir}/{backend}/paper/all", exist_ok=True)
    uptake.to_csv(f"{output_dir}/{backend}/paper/all/wave.csv")


if __name__ == "__main__":
    run()
