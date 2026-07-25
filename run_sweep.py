#!/usr/bin/env python3
"""
Runs a Locust load sweep against a running Strapi instance, producing one
set of CSV result files per load level, consistently named so analyze.py
can parse them automatically.

Usage:
    python run_sweep.py --env local_native --host http://localhost:1337
    python run_sweep.py --env local_constrained --host http://localhost:1337
    python run_sweep.py --env render --host https://your-app.onrender.com

Each run writes into ./results/results_<env>_u<N>_*.csv
The file that matters downstream is the *_stats.csv (has Avg RT, Requests/s,
Failure Count per endpoint, plus an "Aggregated" row across all endpoints).
"""

import argparse
import subprocess
import sys
from pathlib import Path

# Adjust this list to whatever load levels you want in your sweep.
# Keep it identical across environments so rows line up in the final table.
LOAD_LEVELS = [10, 25, 50, 100, 200]

RUN_TIME = "2m"
SPAWN_RATE = "5"


def run_one(env: str, host: str, users: int, results_dir: Path) -> None:
    csv_prefix = results_dir / f"results_{env}_u{users}"
    cmd = [
        "locust",
        "-f",
        "locustfile.py",
        "--host",
        host,
        "--users",
        str(users),
        "--spawn-rate",
        SPAWN_RATE,
        "--run-time",
        RUN_TIME,
        "--headless",
        "--csv",
        str(csv_prefix),
        "--csv-full-history",
    ]
    print(f"\n{'='*60}")
    print(f"Running: env={env} users={users} host={host}")
    print(f"{'='*60}")
    result = subprocess.run(cmd)
    if result.returncode not in (0, 1):
        # Locust exits 1 when there were failed requests during the run —
        # that's expected/interesting data, not a crash. Anything else,
        # stop the sweep rather than silently produce a gap in your table.
        print(
            f"WARNING: locust exited with unexpected code {result.returncode} for users={users}"
        )
        sys.exit(result.returncode)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--env",
        required=True,
        help="Environment label, e.g. local_native, local_constrained, render",
    )
    parser.add_argument(
        "--host", required=True, help="Base URL of the running Strapi instance"
    )
    parser.add_argument(
        "--results-dir", default="results", help="Output directory for CSVs"
    )
    args = parser.parse_args()

    results_dir = Path(args.results_dir)
    results_dir.mkdir(exist_ok=True)

    for users in LOAD_LEVELS:
        run_one(args.env, args.host, users, results_dir)

    print(f"\nSweep complete. Results in {results_dir}/")


if __name__ == "__main__":
    main()
