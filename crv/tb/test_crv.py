"""Random-only Cocotb FIFO regression, separate from HW4 directed coverage.

Inputs (make command or environment):
  CRV_MODE       uniform | tuned  (default tuned)
  CRV_SEED       integer         (default 4701)
  CRV_CYCLES     random draws    (default 2048)
  CRV_COV_FILE   optional path to coverage YAML
  CRV_TRACE_FILE optional path to exact transaction CSV
  CRV_STATS_FILE optional path to run statistics JSON
  CRV_REQUIRE_CLOSED 1 => require 36/36 X1 bins in this run (optional)
"""
from collections import Counter
import csv
import hashlib
import json
import os
from pathlib import Path
import random

import cocotb
from fifo_coverage import export_coverage, make_sampler, require_closed
from fifo_env import FifoEnv
from test_fifo import FifoScoreboard
from stimulus import DEPTH, FILL, FifoTransaction, next_phase


def write_csv(path, rows):
    dest = Path(path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w", newline="") as file:
        writer = csv.writer(file, lineterminator="\n")
        writer.writerow(("cycle", "pre_count", "phase", "wr_en", "rd_en", "wr_data"))
        writer.writerows(rows)
    return hashlib.sha256(dest.read_bytes()).hexdigest()


@cocotb.test()
async def test_crv(dut):
    mode = os.environ.get("CRV_MODE", "tuned")
    seed = int(os.environ.get("CRV_SEED", "4701"))
    cycles = int(os.environ.get("CRV_CYCLES", "2048"))
    if cycles <= 0:
        raise ValueError("CRV_CYCLES must be positive")

    # A fresh simulator process, fresh transaction object, and stdlib RNG seed
    # are necessary for pyvsc's per-object first-randomize seed capture.
    random.seed(seed)
    txn = FifoTransaction(mode)
    prefix = f"fifo.crv_{mode}_seed_{seed}"
    env = FifoEnv(dut, FifoScoreboard(), make_sampler(prefix, DEPTH))
    await env.start()

    phase = FILL
    rows = []
    seen = set()
    first_hit = {}
    counts = Counter()
    requests = Counter()
    phase_requests = Counter()
    state_samples = Counter()
    state_wr = Counter()
    state_rd = Counter()
    burst_write = burst_read = max_write_burst = max_read_burst = 0

    for i in range(1, cycles + 1):
        pre_count = env.scoreboard.model.count
        txn.count = pre_count
        txn.phase = phase
        txn.randomize()
        wr, rd, data = int(txn.wr_en), int(txn.rd_en), int(txn.wr_data)
        if wr not in (0, 1) or rd not in (0, 1) or not (0 <= data <= 255):
            raise AssertionError("pyvsc produced an out-of-range request")

        # These rows are the *generated requests*, not a post-DUT trace.
        rows.append((i, pre_count, phase, wr, rd, data))
        key = (pre_count, wr, rd)
        if key not in seen:
            seen.add(key)
            first_hit[f"{pre_count},{wr},{rd}"] = i
        counts[pre_count] += 1
        requests[(wr, rd)] += 1
        phase_requests[(phase, wr, rd)] += 1
        state_samples[(pre_count, phase)] += 1
        state_wr[(pre_count, phase)] += wr
        state_rd[(pre_count, phase)] += rd
        burst_write = burst_write + 1 if (wr, rd) == (1, 0) else 0
        burst_read = burst_read + 1 if (wr, rd) == (0, 1) else 0
        max_write_burst = max(max_write_burst, burst_write)
        max_read_burst = max(max_read_burst, burst_read)

        # FifoEnv samples pre-edge occupancy for random-only X1 and checks
        # reference queue, count, full/empty and FWFT head before/after edge.
        await env.cycle(wr, rd, data)
        phase = next_phase(phase, env.scoreboard.model.count)

    # Stop random-only coverage before the directed drain. This verifies the
    # final queued values without fabricating random coverage hits.
    env.sample_traffic = None
    for _ in range(DEPTH):
        await env.cycle(0, 1)
    assert env.scoreboard.model.count == 0

    missing = [f"{c},{w},{r}" for c in range(DEPTH + 1)
               for w in (0, 1) for r in (0, 1)
               if (c, w, r) not in seen]
    # Hash independent of any filesystem timestamps or simulation metadata.
    trace_path = os.environ.get("CRV_TRACE_FILE")
    if trace_path:
        digest = write_csv(trace_path, rows)
    else:
        # Same exact serialization as the persistent CSV, for comparison.
        from io import StringIO
        buf = StringIO(newline="")
        writer = csv.writer(buf, lineterminator="\n")
        writer.writerow(("cycle", "pre_count", "phase", "wr_en", "rd_en", "wr_data"))
        writer.writerows(rows)
        digest = hashlib.sha256(buf.getvalue().encode()).hexdigest()

    stats = {
        "mode": mode, "seed": seed, "cycles": cycles,
        "covered": len(seen), "total": 36, "missing": missing,
        "last_new_bin_cycle": max(first_hit.values()) if first_hit else None,
        "checks_after_last_new_bin": cycles - max(first_hit.values()) if first_hit else 0,
        "first_hit_cycles": first_hit,
        "occupancy_hits": {str(c): counts[c] for c in range(DEPTH + 1)},
        "request_hits": {f"{w},{r}": requests[w, r]
                         for w in (0, 1) for r in (0, 1)},
        "phase_request_hits": {f"{p},{w},{r}": phase_requests[p, w, r]
                               for p in (FILL, 1) for w in (0, 1) for r in (0, 1)},
        "state_rates": {
            f"{c},{p}": {
                "samples": state_samples[c, p],
                "write_rate": (state_wr[c, p] / state_samples[c, p])
                              if state_samples[c, p] else None,
                "read_rate": (state_rd[c, p] / state_samples[c, p])
                             if state_samples[c, p] else None,
            }
            for c in range(DEPTH + 1) for p in (FILL, 1)
        },
        "longest_write_only_burst": max_write_burst,
        "longest_read_only_burst": max_read_burst,
        "observed_write_rate": sum(w * n for (w, r), n in requests.items()) / cycles,
        "observed_read_rate": sum(r * n for (w, r), n in requests.items()) / cycles,
        "trace_sha256": digest,
    }
    stats_path = os.environ.get("CRV_STATS_FILE")
    if stats_path:
        dest = Path(stats_path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(stats, indent=2) + "\n")

    dut._log.info(
        f"CRV mode={mode} seed={seed} cycles={cycles} "
        f"X1={len(seen)}/36 missing={missing} "
        f"last_new_bin={stats['last_new_bin_cycle']} trace_sha256={digest}"
    )
    if os.environ.get("CRV_COV_FILE"):
        export_coverage(os.environ["CRV_COV_FILE"], dut._log.info)
    if os.environ.get("CRV_REQUIRE_CLOSED", "0") == "1":
        require_closed(prefix)
