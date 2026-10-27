# Project 1 - synchronous FIFO verification

EEE4701 team repo. The current starting point is Kyle's HW4 FIFO testbench,
with a project verification plan and functional-coverage instrumentation.
The pyvsc regression, final report, and demo are still pending.

**Deadline:** November 8, 2026 (Webcourses date confirmed by Kyle).

## 1. Setup

Use Python 3.12, Icarus Verilog, and make. From the repo root:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Eustis, the course environment is available with:

```bash
source /opt/course/cocotb-env/bin/activate
```

The initial local run used Icarus 13.0, cocotb 1.9.2, and cocotb-coverage 1.2.0.
On macOS, if building cocotb fails with an unsupported Mach-O filetype linker
error, the local install succeeded with:

```bash
LDSHARED='clang -dynamiclib -undefined dynamic_lookup' \
LDCXXSHARED='clang++ -dynamiclib -undefined dynamic_lookup' \
python -m pip install -r requirements.txt
```

## 2. Run

Run the clean testbench and produce coverage:

```bash
make -C tb/fifo SIM=icarus RANDOM_SEED=4701
```

The coverage report is written to `artifacts/coverage.yml`. It separates
directed normal operations, directed reset cases, and each HW4 random seed.
The current random tests use Python random; they are not the pyvsc deliverable.

Run the released mutation pool:

```bash
mkdir -p artifacts
PYTHONPATH=lib RANDOM_SEED=4701 python -u -m craft_mutate.mutate \
  --tb tb/fifo --pool tb/fifo/mutants_released.yaml --sim icarus \
  --gate --json artifacts/mutation.json
```

The mutation harness runs clean RTL first. See `FINDINGS.md` for recorded
results and `evidence/` for the corresponding logs. Mutation runs also invoke
the testbench; rerun the clean command before copying a coverage report into
evidence so the report cannot be mistaken for a clean run after a mutant run.

## 3. Files and team work

| Path | Purpose |
|------|---------|
| `dut/` | Unchanged supplied RTL and spec. |
| `lib/models/` | Supplied reference queue. |
| `lib/fifo_coverage.py` | Coverage sampler and closure checks. |
| `tb/fifo/test_fifo.py` | Reused HW4 driver, monitor, scoreboard, and sequences. |
| `crv/` | Handoff for the constrained-random work; implementation pending. |
| `vplan.md` | Requirements, coverage model, test matrix, and closure criteria. |
| `TASKS.md` | Proposed ownership, interface agreement, and remaining work. |
| `FINDINGS.md` | Mutation evidence and residual risk. |
| `closure.md` | Coverage status and remaining CRV work. |
| `CONTRIBUTIONS.md` | Actual completed work and proposed responsibilities. |

The starter import is commit `17ae090`. The unchanged HW4 reuse is commit
`7d77943`. `SOURCE.md` records where that code came from. Each person should
make their own commits and update the contribution record when work is done.

Jackal's repo access still needs confirmation. Read
`TASKS.md` before starting a layer so we agree on the interfaces.
