import base64
import csv
import os
from datetime import datetime, timedelta

import jinja2
import matplotlib.pyplot as plt
import pandas as pd

from age_bands import age_bands
from groups import groups


def run():
    backend = os.getenv("OPENSAFELY_BACKEND", "expectations")

    demographic_cols = ["sex", "age_band", "high_level_ethnicity"]
    group_cols = [
        group for group in groups if "covax" not in group and "unstatvacc" not in group
    ]

    titles = get_titles(groups)
    label_maps = get_label_maps(group_cols)

    charts = make_charts(backend, demographic_cols + group_cols, titles, label_maps)
    summary = make_summary(backend, demographic_cols, group_cols, titles, label_maps)

    ctx = {
        "charts": charts,
        "summary": summary.to_html(classes=["table", "table-sm"], float_format="%.1f%%"),
    }

    with open("templates/report.html.template") as f:
        template = jinja2.Template(f.read())

    with open(f"output/report_{backend}.html", "w") as f:
        f.write(template.render(ctx))


def get_titles(groups):
    titles = {
        "age_band": "Age band",
        "sex": "Sex",
        "high_level_ethnicity": "Ethnicity",
    }

    titles.update(groups)

    return titles


def get_label_maps(group_cols):
    age_band_labels = {
        str(band): f"{lower if lower else ''}-{upper - 1 if upper else ''}"
        for band, (lower, upper) in age_bands.items()
        if band in range(1, 12 + 1)
    }

    high_level_ethnicity_labels = {}
    with open("codelists/primis-covid19-vacc-uptake-eth2001.csv") as f:
        for record in csv.DictReader(f):
            category = record["grouping_6_id"]
            label = record["grouping_6_label"]
            if category in high_level_ethnicity_labels:
                assert high_level_ethnicity_labels[category] == label
            else:
                high_level_ethnicity_labels[category] = label
    high_level_ethnicity_labels["6"] = "Unknown"

    labels = {
        "age_band": age_band_labels,
        "sex": {"F": "Female", "M": "Male"},
        "high_level_ethnicity": high_level_ethnicity_labels,
    }

    for group_col in group_cols:
        labels[group_col] = {"False": "no", "True": "yes"}

    return labels


def make_charts(backend, cols, titles, label_maps):
    charts = []

    for col in cols:
        labels = label_maps[col]
        base_filename = f"coverage_by_{col}_{backend}"

        uptake = pd.read_csv(f"output/{base_filename}.csv", index_col=0)

        uptake_pc = compute_uptake_percent(uptake, labels)
        uptake_pc.plot()
        plt.savefig(f"output/{base_filename}.png")

        with open(f"output/{base_filename}.png", "rb") as f:
            png_data = base64.b64encode(f.read()).decode("utf8")

        charts.append({"title": titles[col], "png_data": png_data})

    return charts


def compute_uptake_percent(uptake, labels):
    uptake_pc = 100 * uptake / uptake.loc["total"]
    uptake_pc.drop("total", inplace=True)
    uptake_pc.sort_values(
        uptake_pc.last_valid_index(), axis=1, ascending=False, inplace=True
    )
    uptake_pc.rename(columns=labels, inplace=True)
    return uptake_pc


def make_summary(backend, demographic_cols, group_cols, titles, label_maps):
    summaries = {}

    uptake = pd.read_csv(f"output/coverage_by_sex_{backend}.csv", index_col=0)
    latest_date = datetime.strptime(uptake.index[-2], "%Y-%m-%d").date()
    last_week_date = datetime.strptime(uptake.index[-9], "%Y-%m-%d").date()
    assert latest_date - last_week_date == timedelta(days=7)
    summary = compute_summary(uptake, {})
    summaries["Overall"] = pd.DataFrame({"": summary.sum(axis=0)}).transpose()

    for col in demographic_cols:
        labels = label_maps[col]
        base_filename = f"coverage_by_{col}_{backend}"
        uptake = pd.read_csv(f"output/{base_filename}.csv", index_col=0)
        summary = compute_summary(uptake, labels)
        summaries[titles[col]] = summary

    other_group_cols = ["shield_group", "preg_group"]
    at_risk_group_cols = ["atrisk_group"] + [
        col
        for col in group_cols
        if col != "atrisk_group" and col not in other_group_cols
    ]

    at_risk_summary = {}
    for col in at_risk_group_cols:
        base_filename = f"coverage_by_{col}_{backend}"
        uptake = pd.read_csv(f"output/{base_filename}.csv", index_col=0)
        summary = compute_summary(uptake, {})
        at_risk_summary[titles[col]] = summary.loc["True"]
    summaries["Patients at risk"] = pd.DataFrame.from_dict(
        at_risk_summary, orient="index"
    )

    other_summary = {}
    for col in other_group_cols:
        base_filename = f"coverage_by_{col}_{backend}"
        uptake = pd.read_csv(f"output/{base_filename}.csv", index_col=0)
        summary = compute_summary(uptake, {})
        other_summary[titles[col]] = summary.loc["True"]
    summaries["Other"] = pd.DataFrame.from_dict(other_summary, orient="index")

    summary = pd.concat(summaries.values(), keys=summaries.keys())
    summary["latest_pc"] = 100 * summary["latest"] / summary["total"]
    summary["last_week_pc"] = 100 * summary["last_week"] / summary["total"]
    summary["in_last_week_pc"] = summary["latest_pc"] - summary["last_week_pc"]

    columns = {
        "latest_pc": f"Vaccinated at {latest_date} (%)",
        "latest": f"Vaccinated at {latest_date} (n)",
        "total": "Population",
        "last_week_pc": f"Vaccinated at {last_week_date} (%)",
        "in_last_week_pc": "Vaccinated in past week (%)",
    }
    summary = summary[list(columns)]
    summary.rename(columns=columns, inplace=True)

    return summary


def compute_summary(uptake, labels):
    latest_date = datetime.strptime(uptake.index[-2], "%Y-%m-%d").date()
    last_week_date = datetime.strptime(uptake.index[-9], "%Y-%m-%d").date()
    assert latest_date - last_week_date == timedelta(days=7)

    summary = pd.DataFrame(
        {
            "latest": uptake.iloc[-2],
            "last_week": uptake.iloc[-8],
            "total": uptake.iloc[-1],
        }
    )

    summary.rename(index=labels, inplace=True)
    return summary


if __name__ == "__main__":
    run()
