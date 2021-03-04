import csv
import json
import os
import random
from datetime import date, timedelta
from pathlib import Path


ref_dat = date(2021, 3, 31)
run_dat = date(2021, 2, 14)
start_dat = date(2020, 12, 1)


def run(spec_path, num_records=10_000):
    with open(spec_path) as f:
        spec = json.load(f)

    generators = build_generators(spec)

    out_path = Path(os.path.abspath(__file__)).parents[1] / "output" / "input.csv"
    with open(out_path) as f:
        reader = csv.DictReader(f)
        expected_headers = reader.fieldnames

    expected_headers.remove("patient_id")
    assert sorted(expected_headers) == sorted(g[0] for g in generators)

    test_out_path = Path(os.path.abspath(__file__)).parents[1] / "tests" / "input.csv"
    with open(test_out_path, "w") as f:
        write_input_csv(generators, num_records, f)


def write_input_csv(generators, num_records, f):
    fieldnames = ["patient_id"] + [g[0] for g in generators]
    writer = csv.DictWriter(f, fieldnames)
    writer.writeheader()
    for ix in range(num_records):
        row = {"patient_id": ix}
        for fieldname, fn in generators:
            row[fieldname] = fn(row)
        writer.writerow(row)


def build_generators(spec):
    extraction_criteria = spec["extraction_criteria"]

    generators = [
        ("age", lambda r: random.randrange(16, 100)),
        ("sex", lambda r: random.choices(["F", "M", "I", "U"], [49, 49, 1, 1])[0]),
    ]
    seen_ethnicity = False

    for r in extraction_criteria:
        if r["details"] == "dm+d code when available":
            continue

        name = r["name"].lower()
        if name.endswith("_cod"):
            name = name[:-4]

        if name.startswith("eth2001_"):
            if seen_ethnicity:
                continue
            seen_ethnicity = True

            # Set eth2001 to None / 1 / 5 / 11 in proportion 30 / 50 / 15 5.
            fn = lambda r: random.choices([None, 1, 5, 11], [30, 50, 15, 5])[0]
            generators.append(("eth2001", fn))
            continue

        if name == "ckd35":
            # Only set ckd35_dat if ckd15_dat is set, since ckd35 codelist is a subset
            # of ckd15 codelist.
            fn = (
                lambda r: choose_date_between(run_dat - timedelta(days=365), run_dat)
                if r["ckd15_dat"] and random.random() < 0.5
                else None
            )
            generators.append(("ckd35_dat", fn))
            continue

        if name == "bmi":
            # Set bmi_dat for 50% of patients.
            fn = (
                lambda r: choose_date_between(run_dat - timedelta(days=365), run_dat)
                if random.random() < 0.5
                else None
            )
            generators.append(("bmi_dat", fn))

            # Only set bmi_val if bmi_dat is set.
            fn = lambda r: random.randint(10, 50) if r["bmi_dat"] else None
            generators.append(("bmi_val", fn))
            continue

        if name == "sev_obesity":
            # Set sev_obesity_dat to bmi_stage_dat if bmi_val >= 35.
            fn = lambda r: r["bmi_stage_dat"] if (r["bmi_val"] or 0) >= 35 else None
            generators.append(("sev_obesity_dat", fn))
            continue

        if name == "pregdel":
            # Set pregdel_dat for 10% of female patients under 40.
            fn = (
                lambda r: choose_date_between(run_dat - timedelta(days=253), run_dat)
                if r["sex"] == "F" and r["age"] < 40 and random.random() < 0.1
                else None
            )
            generators.append(("pregdel_dat", fn))
            continue

        if name == "preg":
            # Set preg_dat to pregdel_dat for all patients with pregdel_dat set, and for
            # 10% of other female patients under 40.
            def preg_fn(r):
                if r["pregdel_dat"]:
                    return r["pregdel_dat"]
                else:
                    if r["sex"] == "F" and r["age"] < 40 and random.random() < 0.1:
                        return choose_date_between(
                            run_dat - timedelta(days=253), run_dat
                        )

            generators.append(("preg_dat", preg_fn))
            continue

        if name == "covadm1":
            # Increase probability of having covadm1_dat set with age.
            fn = (
                lambda r: choose_date_between(start_dat, run_dat)
                if random.random() < r["age"] / 100
                else None
            )
            generators.append(("covadm1_dat", fn))
            continue

        if name == "covadm2":
            # Only set covadm2_dat if covadm1_dat is set, and increase probability of
            # having covadm2_dat set with age.
            fn = (
                lambda r: choose_date_between(
                    r["covadm1_dat"] + timedelta(days=20), run_dat
                )
                if r["covadm1_dat"] and random.random() < r["age"] / 1000
                else None
            )
            generators.append(("covadm2_dat", fn))
            continue

        if name == "pfd1rx":
            # Set pfd1rx_dat if covadm1_dat is set, for 50% of patients.
            fn = lambda r: r["covadm1_dat"] if random.random() < 0.5 else None
            generators.append(("pfd1rx_dat", fn))
            continue

        if name == "pfd2rx":
            # Set pfd2rx_dat to covadm2_dat if pfd1rx_dat is set.
            fn = lambda r: r["covadm2_dat"] if r["pfd1rx_dat"] else None
            generators.append(("pfd2rx_dat", fn))
            continue

        if name == "azd1rx":
            # Set azd1rx_dat if covadm1_dat is set and pfd1rx_dat isn't, most of the
            # time.
            fn = (
                lambda r: None
                if r["pfd1rx_dat"] or random.random() < 0.95
                else r["covadm1_dat"]
            )
            generators.append(("azd1rx_dat", fn))
            continue

        if name == "azd2rx":
            # Set azd2rx_dat to covadm2_dat if azd1rx_dat is set.
            fn = lambda r: r["covadm2_dat"] if r["azd1rx_dat"] else None
            generators.append(("azd2rx_dat", fn))
            continue

        if name in ["mod1rx", "mod2rx", "jnd1rx", "jnd2rx"]:
            # Ignore vaccines that are not yet available.
            continue

        if name == "covrx1":
            # Set covrx1_dat to pfd1rx_dat or azd1rx_dat
            fn = lambda r: r["pfd1rx_dat"] or r["azd1rx_dat"]
            generators.append(("covrx1_dat", fn))
            continue

        if name == "covrx2":
            # Set covrx2_dat to pfd2rx_dat or azd2rx_dat
            fn = lambda r: r["pfd2rx_dat"] or r["azd2rx_dat"]
            generators.append(("covrx2_dat", fn))
            continue

        # Set {name}_dat for 20% of patients.
        fn = (
            lambda r: choose_date_between(run_dat - timedelta(days=365), run_dat)
            if random.random() < 0.2
            else None
        )
        generators.append((f"{name}_dat", fn))

    return generators


def choose_date_between(d0, d1):
    if d0 >= d1:
        return None
    dates = [d0 + timedelta(days=offset) for offset in range((d1 - d0).days)]
    return random.choice(dates)


if __name__ == "__main__":
    import sys

    run(spec_path=sys.argv[1])
