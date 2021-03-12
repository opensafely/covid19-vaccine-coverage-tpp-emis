import glob
import os
import pandas as pd

from combine_cumsums import combine_cumsums


def run():
    for emis_path in sorted(glob.glob("released-output/emis/paper/*/*.csv")):
        print(emis_path)
        tpp_path = emis_path.replace("/emis/", "/tpp/")
        emis_df = pd.read_csv(emis_path, index_col=0)
        tpp_df = pd.read_csv(tpp_path, index_col=0)
        combined_df = combine_cumsums(emis_df, tpp_df)
        combined_path = emis_path.replace("/emis/", "/combined/")
        os.makedirs(os.path.dirname(combined_path), exist_ok=True)
        combined_df.to_csv(combined_path)


if __name__ == "__main__":
    run()
