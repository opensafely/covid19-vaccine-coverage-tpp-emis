import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path


VACC_PRODUCT_NAMES = {
    "pf": "COVID-19 mRNA Vac BNT162b2 30mcg/0.3ml conc for susp for inj multidose vials (Pfizer-BioNTech)",
    "az": "COVID-19 Vac AstraZeneca (ChAdOx1 S recomb) 5x10000000000 viral particles/0.5ml dose sol for inj MDV",
    "mo": "TODO",
    # "nx": "???",
    "jn": "TODO",
    # "gs": "???",
    # "vl": "???",
}


def run(spec_path):
    with open(spec_path) as f:
        spec = json.load(f)

    study_definition_params = get_study_definition_params(spec["extraction_criteria"])

    out_path = (
        Path(os.path.abspath(__file__)).parents[1] / "analysis" / "study_definition.py"
    )

    with open(out_path, "w") as f:
        write_study_definition(study_definition_params, f)

    os.system(f"black {out_path}")


def get_study_definition_params(extraction_criteria):
    study_definition_params = [
        {
            "name": "population",
            "type": "registered_as_of",
            "args": ["ref_dat"],
            "kwargs": {"return_expectations": {"incidence": 0.95}},
        },
        {
            "name": "age",
            "type": "age_as_of",
            "args": ["ref_dat"],
            "kwargs": {
                "return_expectations": {
                    "int": {"distribution": "population_ages"},
                    "rate": '"universal"',
                },
            },
        },
        {
            "name": "sex",
            "type": "sex",
            "args": [],
            "kwargs": {
                "return_expectations": {
                    "category": {
                        "ratios": {"F": 0.49, "M": 0.49, "U": 0.01, "I": 0.01},
                    },
                    "rate": '"universal"',
                },
            },
        },
    ]

    seen_ethnicity = False

    for r in extraction_criteria:
        if r["details"] == "dm+d code when available":
            continue

        name = r["name"].lower()
        if name.endswith("_cod"):
            name = name[:-4]

        param_name = name + "_dat"
        comment = r.get("title")
        args = []
        kwargs = {"returning": '"date"'}

        if name.startswith("eth2001_"):
            if seen_ethnicity:
                continue
            seen_ethnicity = True
            param_name = "eth2001"
            comment = "Ethnicity"
            variable_type = "with_these_clinical_events"
            args = ["codelists.eth2001"]
            kwargs.update(
                returning='"category"',
                find_last_match_in_period=True,
                on_or_before='"index_date"',
                return_expectations={
                    "category": {
                        "ratios": {
                            str(category): 2 ** -category if category < 8 else 2 ** -7
                            for category in range(1, 9)
                        },
                    },
                    "rate": '"universal"',
                },
            )

        elif name == "bmi":
            variable_type = "with_these_clinical_events"
            args = [f"codelists.{name}"]
            kwargs.update(
                ignore_missing_values=True,
                find_last_match_in_period=True,
                on_or_before='"index_date"',
            )

        elif name == "sev_obesity":
            variable_type = "with_these_clinical_events"
            args = [f"codelists.{name}"]
            kwargs.update(
                ignore_missing_values=True,
                find_last_match_in_period=True,
                on_or_after='"bmi_stage_dat"',
                on_or_before='"index_date"',
            )

        elif name.startswith("covadm"):
            variable_type = "with_vaccination_record"
            kwargs["tpp"] = {
                "target_disease_matches": '"SARS-2 CORONAVIRUS"',
            }
            kwargs["emis"] = {
                "procedure_codes": f"codelists.{name}",
            }
            kwargs.update(get_date_criteria_kwargs(r))

        elif re.search("[12]rx", name):
            variable_type = "with_vaccination_record"
            product_name = VACC_PRODUCT_NAMES[name[:2]]
            if product_name == "TODO":
                continue
            kwargs["tpp"] = {
                "product_name_matches": f'"{product_name}"',
            }
            codelist_name = re.sub(r"\d", "", name)
            kwargs["emis"] = {
                "product_codes": f"codelists.{codelist_name}",
            }
            kwargs.update(get_date_criteria_kwargs(r))

        elif re.match("covrx[12]", name):
            variable_type = "with_vaccination_record"
            product_names = ", ".join(
                f'"{name}"' for name in VACC_PRODUCT_NAMES.values() if name != "TODO"
            )
            kwargs["tpp"] = {"product_name_matches": f"[{product_names}]"}
            kwargs["emis"] = {
                "product_codes": f"codelists.covrx",
            }
            kwargs.update(get_date_criteria_kwargs(r))

        else:
            if "rx" in name:
                variable_type = "with_these_medications"
            else:
                variable_type = "with_these_clinical_events"

            if name.startswith("astrxm"):
                codelist_name = "astrx"
            else:
                codelist_name = name

            args = [f"codelists.{codelist_name}"]
            kwargs.update(get_date_criteria_kwargs(r))

        study_definition_params.append(
            {
                "name": param_name,
                "comment": comment,
                "type": variable_type,
                "args": args,
                "kwargs": kwargs,
            }
        )

        if name == "bmi":
            kwargs = kwargs.copy()
            kwargs.update(
                returning='"numeric_value"',
                return_expectations={
                    "float": {"distribution": "normal", "mean": 25, "stddev": 5},
                },
            )
            study_definition_params.append(
                {
                    "name": "bmi_val",
                    "type": "with_these_clinical_events",
                    "args": [f"codelists.{name}"],
                    "kwargs": kwargs,
                }
            )

    return study_definition_params


def get_date_criteria_kwargs(r):
    criteria = r["criteria"].lower()

    criteria = criteria.replace(" ", "")
    match = re.match("(any|latest|earliest)", criteria)
    if not match:
        return

    date_type = match.groups()[0]
    if date_type in ["any", "latest"]:
        kwargs = {"find_last_match_in_period": True}
    else:
        kwargs = {"find_first_match_in_period": True}

    for fragment in sorted(criteria[match.span()[1] :].split("and")):
        k, v = get_date_criteria_param(fragment)
        kwargs[k] = v

    kwargs["date_format"] = '"YYYY-MM-DD"'

    return kwargs


def get_date_criteria_param(fragment):
    if fragment.startswith("<="):
        type = "on_or_before"
        offset = 0
        fragment = fragment[2:]
    elif fragment.startswith("<"):
        type = "on_or_before"
        offset = 1
        fragment = fragment[1:]
    elif fragment.startswith(">="):
        type = "on_or_after"
        offset = 0
        fragment = fragment[2:]
    elif fragment.startswith(">"):
        type = "on_or_after"
        offset = -1
        fragment = fragment[1:]
    else:
        assert False, fragment

    if fragment[0] == "(":
        assert fragment[-1] == ")", fragment
        fragment = fragment[1:-1]

    try:
        date = datetime.strptime(fragment, "%d/%m/%Y")
        date += timedelta(offset)
        return type, f'"{date.strftime("%Y-%m-%d")}"'
    except ValueError:
        pass

    if re.match(r"\w+$", fragment):
        assert offset == 0, offset
        if fragment == "run_dat":
            fragment = "index_date"
        return type, f'"{fragment}"'

    match = re.match(r"(\w+)([+-])(\d+)d(?:ays)?", fragment)
    field, sign, delta = match.groups()
    if field == "run_dat":
        field = "index_date"
    delta = int(delta) + offset
    return type, f'"{field} {sign} {delta} days"'


def write_study_definition(study_definition_params, f):
    p = lambda *args, **kwargs: print(*args, file=f, **kwargs)

    p(
        """
from datetime import date

from cohortextractor import StudyDefinition, patients
import codelists

ref_dat = "2021-03-31"
start_dat = "2020-12-01"


study = StudyDefinition(
index_date=str(date.today()),  # run_dat
default_expectations={
    "date": {"earliest": start_dat, "latest": "today"},
    "rate": "uniform",
    "incidence": 0.05,
},""".strip()
    )

    for param in study_definition_params:
        if "comment" in param:
            p("    # " + param["comment"])
        p("    {name}=patients.{type}".format(**param), end="")
        if param["args"] or param["kwargs"]:
            p("(")
            for arg in param["args"]:
                p(f"        {arg},")
            for k, v in param["kwargs"].items():
                if isinstance(v, dict):
                    p(f"        {k}={{")
                    for k1, v1 in v.items():
                        p(f'            "{k1}": {v1},')
                    p("        },")
                else:
                    p(f"        {k}={v},")
            p("    ),")
        else:
            p("(),")
    p(")")


if __name__ == "__main__":
    import sys

    run(sys.argv[1])
