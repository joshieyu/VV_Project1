"""Random-only FIFO regression: no directed cycles, so no directed coverage.

Configured by environment so the mutation harness can run it unchanged:
    GRAD_STIM    phased | uniform          (default phased)
    GRAD_SEED    stdlib random seed        (default 1)
    GRAD_CYCLES  random draws              (default 256)
    GRAD_COV     coverage YAML to export   (optional)
    GRAD_TXNS    transaction CSV to write  (optional)
"""
import hashlib
import os
import random

import cocotb
from fifo_coverage import make_sampler, export_coverage
from fifo_env import FifoEnv
from stimulus import STIMULI, FILL, next_phase

try:
    from fifo_scoreboard import FifoScoreboard
except ImportError:
    from test_fifo import FifoScoreboard


@cocotb.test()
async def test_grad(dut):
    stim = os.environ.get("GRAD_STIM", "phased")
    seed = int(os.environ.get("GRAD_SEED", "1"))
    cycles = int(os.environ.get("GRAD_CYCLES", "256"))

    env = FifoEnv(dut, FifoScoreboard(), make_sampler(f"grad.{stim}_{seed}"))
    await env.start()

    random.seed(seed)  # seeds txn's own generator on its first randomize()
    txn = STIMULI[stim]()
    phase = FILL
    stream = []
    for _ in range(cycles):
        txn.count = env.scoreboard.model.count
        txn.phase = phase
        txn.randomize()
        request = (int(txn.wr_en), int(txn.rd_en), int(txn.wr_data))
        stream.append(request)
        await env.cycle(*request)
        phase = next_phase(phase, env.scoreboard.model.count)

    # Drain so the last stored values are checked; not counted as coverage.
    env.sample_traffic = None
    for _ in range(8):
        await env.cycle(0, 1)

    digest = hashlib.sha256(repr(stream).encode()).hexdigest()[:16]
    dut._log.info(f"stim={stim} seed={seed} cycles={cycles} stream={digest}")
    if os.environ.get("GRAD_TXNS"):
        with open(os.environ["GRAD_TXNS"], "w") as f:
            f.write("wr_en,rd_en,wr_data\n")
            f.writelines(f"{w},{r},{d}\n" for w, r, d in stream)
    if os.environ.get("GRAD_COV"):
        export_coverage(os.environ["GRAD_COV"], dut._log.info)
