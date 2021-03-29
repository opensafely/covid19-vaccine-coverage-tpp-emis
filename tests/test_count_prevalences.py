from analysis.count_prevalences import count_prevalences
from analysis.transform_fast import load_raw_cohort, transform


def test_count_prevalences():
    raw_cohort = load_raw_cohort("tests/input.csv")
    cohort = transform(raw_cohort)

    prevalences = count_prevalences(cohort)

    expected_total = 0
    expected_immuno_group = 0
    expected_ethnicity_1 = 0

    for ix, row in cohort.iterrows():
        if row["age_band"] != 3:
            continue
        if row["sex"] != "M":
            continue

        expected_total += 1
        if row["immuno_group"]:
            expected_immuno_group += 1
        if row["high_level_ethnicity"] == 1:
            expected_ethnicity_1 += 1

    assert prevalences.loc[3, "M"]["total"] == (expected_total // 7) * 7
    assert prevalences.loc[3, "M"]["immuno_group"] == (expected_immuno_group // 7) * 7
    assert prevalences.loc[3, "M"]["ethnicity_1"] == (expected_ethnicity_1 // 7) * 7
