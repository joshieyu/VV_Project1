# EEE5703 graduate extension

Owner: joshieyu. The write-up is `Project1_Extension.tex` / `EEE5703_Project1_Extension.pdf`.

| File | Purpose |
|------|---------|
| `stimulus.py` | The pyvsc constraint analyzed here (`PhasedTxn`) and an unshaped baseline (`UniformTxn`). This is not the team `crv/` layer. |
| `tb/test_grad.py` | Random-only cocotb test. It reuses `FifoEnv`, the driver, the monitor, and the scoreboard from `tb/fifo`. |
| `run_regression.py` | For each stimulus, cycle budget, and seed: one clean run with X1 coverage, then the released pool. |
| `analyze.py` | Measures pyvsc rates and solves the Markov chain for the occupancy histogram and the corner bound. Also correlates coverage with found/total. |
| `results/` | `regression.csv`, `regression_bins.json`, `analysis.json`. |
| `figures/` | Figures used by the write-up. |

## Reproduce

From the repo root with the venv active. numpy and matplotlib are needed only
for `analyze.py`.

```bash
python -m pip install pyvsc==0.9.5.27214109393 numpy matplotlib
make -C grad/tb SIM=icarus GRAD_STIM=phased GRAD_SEED=1 GRAD_CYCLES=256   # one run
python grad/run_regression.py --jobs 6                                     # 80 points, ~10 min locally
PYTHONPATH=lib:grad python grad/analyze.py                                 # ~5 min
PYTHONPATH=lib:grad python grad/analyze.py --trial phased 10042            # one Monte Carlo trial
cd grad && pdflatex Project1_Extension.tex
```

Every run logs `stream=<hash>`, a hash of its generated transactions. The same
stimulus, seed, and budget give the same hash. Set `GRAD_TXNS=path.csv` to
save the transactions themselves.

The Monte Carlo in `analyze.py` runs trials with seeds 10000 to 12999. Each
trial seeds the stdlib generator and then builds a new transaction. A pyvsc
object takes its own seed from the stdlib generator on its first
`randomize()` and ignores `random.seed()` after that. `--trial` reruns one
trial alone. `analysis.json` stores the outcome and stream hash of three
sample trials per stimulus, so the two can be compared.

To analyze the team constraint once `crv/` lands, register its class in
`STIMULI` in `stimulus.py`. It needs `wr_en`, `rd_en`, `wr_data`, and the
non-random `count` and `phase` fields. Then rerun both scripts.
