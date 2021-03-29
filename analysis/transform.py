import os

import transform_fast, transform_slow


def run(input_path="output/input.csv", output_path="output/cohort.pickle"):
    backend = os.getenv("OPENSAFELY_BACKEND", "expectations")

    if backend == "emis":
        transform_slow.run(input_path, output_path)
    else:
        transform_fast.run(input_path, output_path)


if __name__ == "__main__":
    import sys

    run(input_path=sys.argv[1])
