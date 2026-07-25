#!/usr/bin/env python3
"""
Parses Locust *_stats.csv files produced by run_sweep.py, builds the
Load / Environment / Avg Response Time / Throughput / Errors summary table,
and plots line graphs comparing environments across the load sweep.

Expects filenames of the form: results_<environment>_u<load>_stats.csv
e.g. results_local_native_u50_stats.csv, results_render_u100_stats.csv

Usage:
    python analyze.py --results-dir results --out-dir report_output
"""

import argparse
import re
import sys
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

FILENAME_RE = re.compile(r"results_(?P<env>.+)_u(?P<load>\d+)_stats\.csv$")


def parse_one_file(path: Path) -> dict:
    match = FILENAME_RE.search(path.name)
    if not match:
        raise ValueError(
            f"Filename {path.name} doesn't match expected pattern "
            f"'results_<env>_u<load>_stats.csv' — rename it or fix the regex."
        )
    env = match.group("env")
    load = int(match.group("load"))

    df = pd.read_csv(path)
    agg_row = df[df["Name"] == "Aggregated"]
    if agg_row.empty:
        raise ValueError(
            f"No 'Aggregated' row found in {path.name} — was this a run with "
            f"zero requests, or a malformed/truncated CSV?"
        )
    agg_row = agg_row.iloc[0]

    request_count = agg_row["Request Count"]
    failure_count = agg_row["Failure Count"]

    return {
        "Environment": env,
        "Load": load,
        "Avg Response Time (ms)": round(agg_row["Average Response Time"], 2),
        "Throughput (req/s)": round(agg_row["Requests/s"], 2),
        "Errors": int(failure_count),
        "Error Rate (%)": round(100 * failure_count / request_count, 2) if request_count else 0.0,
    }


def build_summary(results_dir: Path) -> pd.DataFrame:
    files = sorted(results_dir.glob("results_*_stats.csv"))
    if not files:
        print(f"No files matching 'results_*_stats.csv' found in {results_dir}/")
        sys.exit(1)

    rows = []
    for f in files:
        try:
            rows.append(parse_one_file(f))
        except ValueError as e:
            print(f"Skipping {f.name}: {e}")

    summary = pd.DataFrame(rows).sort_values(["Environment", "Load"]).reset_index(drop=True)
    return summary


def plot_metric(summary: pd.DataFrame, metric: str, ylabel: str, out_path: Path, logy: bool = False):
    fig, ax = plt.subplots(figsize=(8, 5))
    for env, group in summary.groupby("Environment"):
        group = group.sort_values("Load")
        ax.plot(group["Load"], group[metric], marker="o", label=env)
    ax.set_xlabel("Load (concurrent users)")
    ax.set_ylabel(ylabel)
    ax.set_title(f"{ylabel} vs Load")
    if logy:
        ax.set_yscale("log")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"Saved {out_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", default="results")
    parser.add_argument("--out-dir", default="report_output")
    args = parser.parse_args()

    results_dir = Path(args.results_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(exist_ok=True)

    summary = build_summary(results_dir)

    csv_out = out_dir / "summary_table.csv"
    summary.to_csv(csv_out, index=False)
    print(f"\nSummary table saved to {csv_out}\n")
    print(summary.to_string(index=False))

    plot_metric(summary, "Avg Response Time (ms)", "Avg Response Time (ms)", out_dir / "response_time_vs_load.png")
    plot_metric(summary, "Throughput (req/s)", "Throughput (req/s)", out_dir / "throughput_vs_load.png")
    plot_metric(summary, "Error Rate (%)", "Error Rate (%)", out_dir / "error_rate_vs_load.png")


if __name__ == "__main__":
    main()
