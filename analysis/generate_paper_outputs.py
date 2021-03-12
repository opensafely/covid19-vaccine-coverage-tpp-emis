from datetime import datetime, timedelta

import jinja2
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import pandas as pd

from compute_uptake_for_paper import at_risk_cols, cols, demographic_cols, other_cols
from ethnicities import ethnicities, high_level_ethnicities
from groups import groups, at_risk_groups


def run(backend):
    titles = get_titles()
    label_maps = get_label_maps()

    for wave in range(1, 9 + 1):
        print("-" * 80)
        print(f"wave: {wave}")
        dir_path = f"released-output/{backend}/paper/wave-{wave}"

        uptake = pd.read_csv(f"{dir_path}/sex.csv", index_col=0)
        latest_date = datetime.strptime(uptake.index[-2], "%Y-%m-%d").date()
        last_week_date = datetime.strptime(uptake.index[-9], "%Y-%m-%d").date()
        assert latest_date - last_week_date == timedelta(days=7)
        overall_summary = compute_summary(uptake)
        summaries = {
            "Overall": pd.DataFrame({"": overall_summary.sum(axis=0)}).transpose()
        }

        at_risk_summary = {}
        other_summary = {}

        for col in cols:
            print(col)
            title = titles[col]
            labels = label_maps[col]
            uptake = pd.read_csv(f"{dir_path}/{col}.csv", index_col=0)

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

            plot_uptake_percent(uptake, title, labels, col, dir_path)

        summaries["Clinical Risk Groups"] = pd.DataFrame.from_dict(
            at_risk_summary, orient="index"
        )
        summaries["Other Groups"] = pd.DataFrame.from_dict(
            other_summary, orient="index"
        )

        save_summary_table(wave, summaries, latest_date, last_week_date, dir_path)


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


def save_summary_table(wave, summaries, latest_date, last_week_date, dir_path):
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

    summary.to_csv(f"{dir_path}/summary.csv", float_format="%.1f%%")

    ctx = {
        "wave": wave,
        "table": summary.to_html(
            classes=["table", "table-sm"], border="0", float_format="%.1f%%"
        ),
    }

    with open("templates/summary.html") as f:
        template = jinja2.Template(f.read())

    with open(f"{dir_path}/summary-wave-{wave}.html", "w") as f:
        f.write(template.render(ctx))


def plot_uptake_percent(uptake, title, labels, col, dir_path):
    uptake_pc = compute_uptake_percent(uptake, labels)
    uptake_pc.plot()
    ax = plt.gca()
    ax.set_title(title, fontsize=16)
    ax.xaxis.set_tick_params(rotation=90)
    ax.yaxis.set_major_formatter(PercentFormatter())
    ax.set_ylim([0, 100])
    plt.savefig(f"{dir_path}/{col}.png", dpi=300, bbox_inches="tight")
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


if __name__ == "__main__":
    import sys

    run(sys.argv[1])
