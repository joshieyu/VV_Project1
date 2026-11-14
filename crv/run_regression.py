"""Run baseline, tuned, and replay FIFO CRV campaigns with retained evidence.

From the repo root:
  python crv/run_regression.py --sim icarus --seeds 4701,4702,4703 \
      --short-cycles 128 --cycles 2048
  python crv/run_regression.py --mutate

This runner only reports results that were actually produced by make/cocotb.
It never merges directed (HW4) coverage into random-only X1.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
TB = ROOT / "crv" / "tb"


def run_case(out, mode, seed, cycles, tag, sim):
    stem = f"{tag}_{mode}_{seed}_{cycles}"
    cov = out / f"{stem}.coverage.yml"
    trace = out / f"{stem}.transactions.csv"
    stats = out / f"{stem}.stats.json"
    log = out / f"{stem}.log"
    sim_dir = out / f"{stem}.sim_build"
    result = out / f"{stem}.results.xml"
    env = dict(os.environ, CRV_MODE=mode, CRV_SEED=str(seed),
               CRV_CYCLES=str(cycles), CRV_COV_FILE=str(cov),
               CRV_TRACE_FILE=str(trace), CRV_STATS_FILE=str(stats))
    env.pop("CRV_REQUIRE_CLOSED", None)
    command = ["make", "-s", "-C", str(TB), f"SIM={sim}",
               f"SIM_BUILD={sim_dir}", f"COCOTB_RESULTS_FILE={result}"]
    completed = subprocess.run(command, env=env, text=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
    log.write_text("COMMAND: " + " ".join(command) + "\n" +
                   f"CRV_MODE={mode} CRV_SEED={seed} CRV_CYCLES={cycles}\n" +
                   completed.stdout)
    if completed.returncode != 0 or not all(p.exists() for p in (cov, trace, stats)):
        raise RuntimeError(f"{stem} failed; inspect {log}")

    summary = json.loads(stats.read_text())
    covdata = yaml.safe_load(cov.read_text())
    cross = f"fifo.crv_{mode}_seed_{seed}.occupancy_x_request"
    hitmap = covdata[cross]["bins:_hits"]
    cross_hits = sum(bool(v) for v in hitmap.values())
    if summary["covered"] != cross_hits:
        raise AssertionError(f"{stem}: CSV/state cross disagrees with YAML")
    print(f"{stem}: X1 {cross_hits}/36  first/last="
          f"{summary['last_new_bin_cycle']}, stream={summary['trace_sha256'][:16]}")
    return dict(stem=stem, summary=summary, covered_bins=set(summary["first_hit_cycles"]),
                trace=trace, stats=stats, cov=cov, log=log)


def run_mutants(out, seed, cycles, sim):
    env = dict(os.environ, CRV_MODE="tuned", CRV_SEED=str(seed),
               CRV_CYCLES=str(cycles), PYTHONPATH=str(ROOT / "lib"))
    for key in ("CRV_COV_FILE", "CRV_TRACE_FILE", "CRV_STATS_FILE", "CRV_REQUIRE_CLOSED"):
        env.pop(key, None)
    log = out / "mutation.log"
    results = out / "mutation.json"
    cmd = [sys.executable, "-u", "-m", "craft_mutate.mutate",
           "--tb", str(TB), "--dut", str(ROOT / "dut/fifo.sv"),
           "--pool", str(ROOT / "tb/fifo/mutants_released.yaml"),
           "--sim", sim, "--json", str(results)]
    p = subprocess.run(cmd, env=env, text=True, stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, cwd=ROOT)
    log.write_text("COMMAND: " + " ".join(cmd) + "\n" +
                   f"CRV_MODE=tuned CRV_SEED={seed} CRV_CYCLES={cycles}\n" + p.stdout)
    if p.returncode or not results.exists():
        raise RuntimeError(f"mutation run failed; inspect {log}")
    score = json.loads(results.read_text())
    print(f"Released mutation: {score['found']}/{score['total']} "
          f"({score['percent']:.1f}%). See {log}")
    suspicious = [m for m in score["mutants"] if m["why"] not in ("test-failed", "passed")]
    if suspicious:
        print("WARNING: Some mutants failed by timeout/build/crash:", suspicious)
    return score


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sim", default="icarus")
    ap.add_argument("--seeds", default="4701,4702,4703")
    ap.add_argument("--short-cycles", type=int, default=128)
    ap.add_argument("--cycles", type=int, default=2048)
    ap.add_argument("--out", type=Path, default=ROOT / "evidence/crv")
    ap.add_argument("--mutate", action="store_true")
    args = ap.parse_args()
    if not (args.short_cycles > 0 and args.cycles >= args.short_cycles):
        ap.error("--cycles must be >= --short-cycles > 0")
    seeds = [int(s) for s in args.seeds.split(",")]
    if len(seeds) != len(set(seeds)):
        ap.error("seeds must be distinct")
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)

    # Fair like-for-like comparison: identical seed and 128-draw budget.
    baseline = run_case(out, "uniform", seeds[0], args.short_cycles, "before", args.sim)
    short_tuned = run_case(out, "tuned", seeds[0], args.short_cycles, "after_short", args.sim)
    print(f"At equal budget: baseline holes={baseline['summary']['missing']} ")
    print(f"At equal budget: tuned holes={short_tuned['summary']['missing']}")

    # Full-budget random-only regression: aggregate distinct seed runs.
    tuned = [run_case(out, "tuned", s, args.cycles, "final", args.sim) for s in seeds]
    total = set().union(*(r["covered_bins"] for r in tuned))
    missing = [f"{c},{w},{r}" for c in range(9) for w in (0, 1)
               for r in (0, 1) if f"{c},{w},{r}" not in total]
    print(f"Random-only aggregate X1 {len(total)}/36; holes={missing}")

    # Independent process and fresh pyvsc object to test complete transaction
    # stream replay, including the seed-dependent pre-edge occupancy history.
    replay = run_case(out, "tuned", seeds[0], args.cycles, "replay", args.sim)
    replay_match = tuned[0]["trace"].read_bytes() == replay["trace"].read_bytes()
    print(f"Replay seed={seeds[0]} byte-for-byte CSV match: {replay_match}")
    result = {
        "baseline_128_or_configured": baseline["summary"],
        "tuned_same_budget": short_tuned["summary"],
        "full_budget_seeds": [r["summary"] for r in tuned],
        "aggregate_covered": len(total), "aggregate_missing": missing,
        "replay_match": replay_match,
        "note": "CRV normal-operation random-only X1; directed/reset excluded",
    }
    (out / "regression_summary.json").write_text(json.dumps(result, indent=2) + "\n")
    if args.mutate:
        run_mutants(out, seeds[0], args.cycles, args.sim)
    if missing or not replay_match:
        sys.exit("CRV regression incomplete: inspect missing bins or replay mismatch")
    print(f"PASS: random-only X1 closure and seed replay; evidence saved to {out}")


if __name__ == "__main__":
    main()
