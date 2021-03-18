import base64
import os
from datetime import datetime, timedelta

import jinja2
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import pandas as pd

from compute_uptake_for_paper import at_risk_cols, cols, demographic_cols, other_cols
from ethnicities import ethnicities, high_level_ethnicities
from groups import groups, at_risk_groups


wave_column_headings = {
    "total": "All",
    "all_priority": "Priority groups",
    "1": "In care home",
    "2": "80+",
    "3": "75-79",
    "4": "CEV or 70-74",
    "5": "65-69",
    "6": "At risk",
    "7": "60-64",
    "8": "55-59",
    "9": "50-54",
    "0": "Other",
}


def run(base_path, earliest_date, latest_date):
    backend = base_path.rstrip("/").split("/")[-1]
    titles = get_titles()
    label_maps = get_label_maps()

    tables_path = f"{base_path}/tables"
    charts_path = f"{base_path}/charts"
    reports_path = f"{base_path}/reports"
    os.makedirs(tables_path, exist_ok=True)
    os.makedirs(charts_path, exist_ok=True)
    os.makedirs(reports_path, exist_ok=True)

    for key in ["dose_1", "dose_2", "pf", "az"]:
        in_path = f"{base_path}/cumulative_coverage/all/{key}/all_{key}_by_wave.csv"
        generate_summary_table_for_all(
            in_path, tables_path, key, earliest_date, latest_date
        )
        generate_charts_for_all(in_path, charts_path, key, earliest_date, latest_date)
        generate_report_for_all(
            backend,
            tables_path,
            charts_path,
            reports_path,
            key,
            earliest_date,
            latest_date,
        )

        for wave in range(1, 9 + 1):
            in_path = f"{base_path}/cumulative_coverage/wave_{wave}/{key}"

            generate_summary_table_for_wave(
                in_path,
                tables_path,
                wave,
                key,
                earliest_date,
                latest_date,
                titles,
                label_maps,
            )

            generate_charts_for_wave(
                in_path,
                charts_path,
                wave,
                key,
                earliest_date,
                latest_date,
                titles,
                label_maps,
            )

            generate_report_for_wave(
                backend,
                tables_path,
                charts_path,
                reports_path,
                wave,
                key,
                earliest_date,
                latest_date,
            )


def generate_summary_table_for_all(
    in_path, tables_path, key, earliest_date, latest_date
):
    uptake = load_uptake(in_path, earliest_date, latest_date)
    last_week_date = uptake.index[-9]
    summary = pd.DataFrame(
        {
            "latest": uptake.iloc[-2],
            "last_week": uptake.iloc[-8],
            "total": uptake.iloc[-1],
        }
    )
    summary.loc["total"] = summary.sum()

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

    rows = {str(wave): f"Wave {wave}" for wave in range(1, 9 + 1)}
    rows["0"] = "Other"
    rows["total"] = "Population"
    summary = summary.loc[list(rows)]
    summary.rename(index=rows, inplace=True)

    summary.to_csv(f"{tables_path}/all_{key}.csv", float_format="%.1f%%")


def generate_charts_for_all(in_path, charts_path, key, earliest_date, latest_date):
    uptake = load_uptake(in_path, earliest_date, latest_date)

    uptake_total = uptake.iloc[:-1] / 1_000_000
    uptake_total["total"] = uptake_total.loc[:, "0":"9"].sum(axis=1)
    uptake_total["all_priority"] = uptake_total.loc[:, "1":"9"].sum(axis=1)
    uptake_total = uptake_total.loc[:, ["total", "all_priority", "0"]]
    uptake_total = uptake_total[
        [col for col in wave_column_headings if col in uptake_total.columns]
    ]
    uptake_total.rename(columns=wave_column_headings, inplace=True)
    uptake_total.plot()
    ax = plt.gca()
    ax.xaxis.set_tick_params(rotation=90)
    ax.set_ylim(ymin=0)
    ax.set_title("Total number of patients vaccinated (million)")
    plt.savefig(f"{charts_path}/all_{key}_total.png", dpi=300, bbox_inches="tight")
    plt.close()

    uptake_pc = 100 * uptake / uptake.loc["total"]
    uptake_pc.drop("total", inplace=True)
    uptake_pc.fillna(0, inplace=True)
    columns = {str(wave): f"Wave {wave}" for wave in range(1, 9 + 1)}
    columns["0"] = "Other"
    uptake_pc = uptake_pc[
        [col for col in wave_column_headings if col in uptake_pc.columns]
    ]
    uptake_pc.rename(columns=wave_column_headings, inplace=True)
    uptake_pc.plot()
    ax = plt.gca()
    ax.set_title("Proportion of patients vaccinated")
    ax.xaxis.set_tick_params(rotation=90)
    ax.yaxis.set_major_formatter(PercentFormatter())
    ax.set_ylim([0, 100])
    plt.savefig(f"{charts_path}/all_{key}_percent.png", dpi=300, bbox_inches="tight")
    plt.close()


def generate_report_for_all(
    backend, tables_path, charts_path, out_path, key, earliest_date, latest_date
):

    subtitle = {
        "dose_1": "First dose",
        "dose_2": "Second dose",
        "pf": "Pfizer",
        "az": "AstraZeneca",
    }[key]

    summary = pd.read_csv(f"{tables_path}/all_{key}.csv", index_col=0)

    charts = []
    with open(f"{charts_path}/all_{key}_total.png", "rb") as f:
        charts.append(base64.b64encode(f.read()).decode("utf8"))
    with open(f"{charts_path}/all_{key}_percent.png", "rb") as f:
        charts.append(base64.b64encode(f.read()).decode("utf8"))

    ctx = {
        "subtitle": subtitle,
        "backend": backend,
        "latest_date": latest_date,
        "charts": charts,
        "table": summary.to_html(
            classes=["table", "table-sm"], border="0", float_format="%.1f%%"
        ),
    }

    with open("templates/summary.html") as f:
        template = jinja2.Template(f.read())

    with open(f"{out_path}/all_{key}.html", "w") as f:
        f.write(template.render(ctx))


def generate_summary_table_for_wave(
    in_path, out_path, wave, key, earliest_date, latest_date, titles, label_maps
):
    uptake = load_uptake(
        f"{in_path}/wave_{wave}_{key}_by_sex.csv", earliest_date, latest_date
    )
    if uptake is None:
        return

    last_week_date = uptake.index[-9]
    overall_summary = compute_summary(uptake)
    summaries = {"Overall": pd.DataFrame({"-": overall_summary.sum(axis=0)}).transpose()}

    at_risk_summary = {}
    other_summary = {}

    for col in cols:
        title = titles[col]
        labels = label_maps[col]
        uptake = load_uptake(
            f"{in_path}/wave_{wave}_{key}_by_{col}.csv", earliest_date, latest_date
        )

        if col in demographic_cols:
            summaries[title] = compute_summary(uptake, labels)
        elif col in at_risk_cols:
            summary = compute_summary(uptake)
            if "True" in summary.index:
                at_risk_summary[titles[col]] = summary.loc["True"]
        elif col in other_cols:
            summary = compute_summary(uptake)
            if "True" in summary.index:
                other_summary[titles[col]] = summary.loc["True"]
        else:
            assert False, col

    summaries["Clinical Risk Groups"] = pd.DataFrame.from_dict(
        at_risk_summary, orient="index"
    )
    summaries["Other Groups"] = pd.DataFrame.from_dict(other_summary, orient="index")
    summaries = {k: v for k, v in summaries.items() if not v.empty}

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

    summary.to_csv(f"{out_path}/wave_{wave}_{key}.csv", float_format="%.1f%%")


def compute_summary(uptake, labels=None):
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

    if labels is not None:
        summary.rename(index=labels, inplace=True)
    return summary


def generate_charts_for_wave(
    in_path, out_path, wave, key, earliest_date, latest_date, titles, label_maps
):
    for col in cols:
        title = titles[col]
        labels = label_maps[col]
        uptake = load_uptake(
            f"{in_path}/wave_{wave}_{key}_by_{col}.csv", earliest_date, latest_date
        )
        if uptake is None:
            return

        uptake_pc = compute_uptake_percent(uptake, labels)
        uptake_pc.plot()
        ax = plt.gca()
        ax.set_title(title, fontsize=16)
        ax.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0)
        ax.xaxis.set_tick_params(rotation=90)
        ax.yaxis.set_major_formatter(PercentFormatter())
        ax.set_ylim([0, 100])
        plt.savefig(
            f"{out_path}/wave_{wave}_{key}_{col}.png", dpi=300, bbox_inches="tight"
        )
        plt.close()


def compute_uptake_percent(uptake, labels):
    uptake_pc = 100 * uptake / uptake.loc["total"]
    uptake_pc.drop("total", inplace=True)
    uptake_pc.fillna(0, inplace=True)
    uptake_pc.sort_values(
        uptake_pc.last_valid_index(), axis=1, ascending=False, inplace=True
    )
    uptake_pc.rename(columns=labels, inplace=True)
    return uptake_pc


def generate_report_for_wave(
    backend, tables_path, charts_path, out_path, wave, key, earliest_date, latest_date
):

    subtitle = {
        "dose_1": "First dose",
        "dose_2": "Second dose",
        "pf": "Pfizer",
        "az": "AstraZeneca",
    }[key]

    subtitle = f"{subtitle} / Priority Group {wave}"

    try:
        summary = pd.read_csv(f"{tables_path}/wave_{wave}_{key}.csv", index_col=[0, 1])
    except FileNotFoundError:
        return

    charts = []
    for col in cols:
        with open(f"{charts_path}/wave_{wave}_{key}_{col}.png", "rb") as f:
            charts.append(base64.b64encode(f.read()).decode("utf8"))

    ctx = {
        "subtitle": subtitle,
        "backend": backend,
        "latest_date": latest_date,
        "charts": charts,
        "table": summary.to_html(
            classes=["table", "table-sm"], border="0", float_format="%.1f%%"
        ),
    }

    with open("templates/summary.html") as f:
        template = jinja2.Template(f.read())

    with open(f"{out_path}/wave_{wave}_{key}.html", "w") as f:
        f.write(template.render(ctx))


def get_titles():
    titles = {
        "sex": "Sex",
        "ethnicity": "Ethnicity",
        "high_level_ethnicity": "Ethnicity (broad categories)",
        "imd_band": "Index of Multiple Deprivation",
    }

    titles.update(groups)
    titles.update(at_risk_groups)

    return titles


def get_label_maps():
    labels = {
        "sex": {"F": "Female", "M": "Male"},
        "ethnicity": {str(k): v for k, v in ethnicities.items()},
        "high_level_ethnicity": {str(k): v for k, v in high_level_ethnicities.items()},
        "imd_band": {
            "0": "Unknown",
            "1": "1 (most deprived)",
            "2": "2",
            "3": "3",
            "4": "4",
            "5": "5 (least deprived)",
        },
    }

    for group in groups:
        labels[group] = {"False": "no", "True": "yes"}

    for group in at_risk_groups:
        labels[group] = {"False": "no", "True": "yes"}

    return labels


def load_uptake(path, earliest_date, latest_date):
    try:
        uptake = pd.read_csv(path, index_col=0)
    except FileNotFoundError:
        return

    return uptake.loc[
        ((uptake.index >= earliest_date) & (uptake.index <= latest_date))
        | (uptake.index == "total")
    ]


if __name__ == "__main__":
    import sys

    run(*sys.argv[1:])
