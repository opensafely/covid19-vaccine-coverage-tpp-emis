from analysis.compute_uptake import compute_uptake
from analysis.transform_fast import load_raw_cohort, transform


def test_compute_uptake():
    raw_cohort = load_raw_cohort("tests/input.csv")
    cohort = transform(raw_cohort)

    uptake = compute_uptake(cohort, "vacc1_dat", "age_band")

    expected_total = 0
    expected_by_nyd = 0

    for ix, row in cohort.iterrows():
        if row["age_band"] != 3:
            continue

        expected_total += 1
        if str(row["vacc1_dat"]) <= "2021-01-01":
            expected_by_nyd += 1

    assert uptake[3]["total"] == (expected_total // 7) * 7
    assert uptake[3]["2021-01-01"] == (expected_by_nyd // 7) * 7
