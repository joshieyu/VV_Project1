# Recorded baseline evidence

Recorded on 2026-10-27 with Python 3.12, Icarus 13.0, cocotb 1.9.2,
cocotb-coverage 1.2.0, and PyYAML 6.0.3.

| Directory | Source revision | Result |
|-----------|-----------------|--------|
| `starter/` | `17ae090` | Clean passes; 1/8 released mutants found. |
| `hw4/` | `7d77943` | Clean passes; 8/8 released mutants found. |
| `project-baseline/` | `dba08bb` | Coverage-instrumented suite passes; 8/8 released mutants found. |

All found mutant outcomes are `test-failed`, with no build/crash or timeout
outcomes. The two later campaigns set `RANDOM_SEED=4701`; HW4 stimulus also
uses its explicit Python random seeds 4701-4704. The starter has no random
stimulus. No pyvsc or hidden-pool result is included.

The source revision identifies tested code; evidence and documentation are
committed afterward. `project-baseline/coverage.yml` is copied from a clean
run after the mutation campaign. `clean.log` contains that simulation's
summary. `fresh-checkout.log` records a clean run from an exported tracked
checkout using the same installed local simulator environment.

## Commands

Run from the repo root with the environment activated:

```bash
PYTHONPATH=lib RANDOM_SEED=4701 python -u -m craft_mutate.mutate \
  --tb tb/fifo --pool tb/fifo/mutants_released.yaml --sim icarus \
  --gate --json artifacts/mutation.json
make -C tb/fifo SIM=icarus RANDOM_SEED=4701
```

For the starter, omit `--gate` to record its expected low score. Select the
source revision in a separate checkout to reproduce an earlier suite.
Fresh checkout verification reuses the installed environment; it does not
prove a second teammate's environment is configured.
