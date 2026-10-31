"""Coverage vs. found/total across a random-only regression.

For each (stimulus, cycle budget, seed): one clean run exports X1 coverage,
then the released mutant pool runs through the course harness with the same
settings. Stimulus is driven from the reference queue, so every run of a
point gets the same transactions until a check fails.

    PYTHONPATH=lib python grad/run_regression.py --jobs 4
"""
import argparse
import csv
import json
import os
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
TB = ROOT / "grad" / "tb"
POOL = ROOT / "tb" / "fifo" / "mutants_released.yaml"
OUT = ROOT / "grad" / "results"


def x1_hits(cov_path, name):
    db = yaml.safe_load(open(cov_path))
    return db[f"{name}.occupancy_x_request"]["bins:_hits"]


def run_point(stim, cycles, seed):
    env = dict(os.environ, GRAD_STIM=stim, GRAD_SEED=str(seed),
               GRAD_CYCLES=str(cycles), PYTHONPATH=str(ROOT / "lib"))
    with tempfile.TemporaryDirectory(prefix="grad_") as td:
        cov = Path(td) / "cov.yml"
        clean = subprocess.run(
            ["make", "-s", "-C", str(TB), "SIM=icarus", f"SIM_BUILD={td}/build",
             f"COCOTB_RESULTS_FILE={td}/results.xml"],
            env=dict(env, GRAD_COV=str(cov)), capture_output=True, text=True)
        if not cov.exists():
            sys.exit(f"clean run failed: {stim} {cycles} {seed}\n{clean.stdout[-2000:]}")
        hits = x1_hits(cov, f"grad.{stim}_{seed}")
        stream = next(line.split("stream=")[1].split()[0]
                      for line in clean.stdout.splitlines() if "stream=" in line)

        mut_json = Path(td) / "mutation.json"
        subprocess.run(
            [sys.executable, "-m", "craft_mutate.mutate", "--tb", str(TB),
             "--pool", str(POOL), "--sim", "icarus", "--json", str(mut_json)],
            env=env, capture_output=True, text=True, check=True)
        mutation = json.load(open(mut_json))

    row = {"stim": stim, "cycles": cycles, "seed": seed, "stream": stream,
           "bins_hit": sum(1 for n in hits.values() if n),
           "found": mutation["found"], "total": mutation["total"]}
    for r in mutation["mutants"]:
        row[r["id"]] = int(r["found"])
        assert r["why"] in ("passed", "test-failed"), f"{r['id']}: {r['why']}"
    print(f"{stim:8s} N={cycles:5d} seed={seed}: X1 {row['bins_hit']:2d}/36, "
          f"found {row['found']}/{row['total']}", flush=True)
    return row, {"point": [stim, cycles, seed], "x1": hits}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stims", default="phased,uniform")
    ap.add_argument("--cycles", default="8,16,32,64,128,256,512,1024")
    ap.add_argument("--seeds", default="1,2,3,4,5")
    ap.add_argument("--jobs", type=int, default=4)
    args = ap.parse_args()

    points = [(s, int(n), int(k)) for s in args.stims.split(",")
              for n in args.cycles.split(",") for k in args.seeds.split(",")]
    with ThreadPoolExecutor(args.jobs) as pool:
        results = list(pool.map(lambda p: run_point(*p), points))

    OUT.mkdir(parents=True, exist_ok=True)
    rows = [r for r, _ in results]
    with open(OUT / "regression.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    bins = [{"point": b["point"], "x1": {str(k): v for k, v in b["x1"].items()}}
            for _, b in results]
    json.dump(bins, open(OUT / "regression_bins.json", "w"), indent=1)


if __name__ == "__main__":
    main()
