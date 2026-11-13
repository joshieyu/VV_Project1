# FINDINGS - Project 1 FIFO - Kyle Coutray

## Score

| Suite / pool | found | total | % |
|--------------|------:|------:|--:|
| Supplied starter / released | 1 | 8 | 12.5% |
| Reused HW4 / released | 8 | 8 | 100% |
| HW4 with Project 1 coverage / released | 8 | 8 | 100% |
| Hidden (reported at grading) | not run | not available | - |

**Command run:**

```bash
PYTHONPATH=lib RANDOM_SEED=4701 python -u -m craft_mutate.mutate \
  --tb tb/fifo --pool tb/fifo/mutants_released.yaml --sim icarus \
  --gate --json artifacts/mutation.json
```

The starter was run without `--gate` so its low score could be recorded. Its
source is commit `17ae090`; its output is in `evidence/starter/`. The unchanged
HW4 source is commit `7d77943`; its output is in `evidence/hw4/`. Both passed
on clean RTL first. The HW4 suite found all eight through failed tests, with
no build/crash or timeout outcomes. These runs used Icarus 13.0 and cocotb 1.9.2.

Commit `dba08bb` adds coverage instrumentation. The complete released campaign
was rerun against that source and remained 8/8; evidence is in
`evidence/project-baseline/`. This establishes the instrumented baseline,
not completion of the constrained-random project.

## Survivors

These are measured **starter survivors**, not survivors of the final project
suite. The project still needs its pyvsc regression. Confirm with course staff
that baseline survivor analysis meets the handout's two-survivor requirement.

| Mutant | What it changes | Reachable by starter stimulus? | Observable by starter checks? | Why it survived / what catches it |
|--------|-----------------|--------------------------------|-------------------------------|---------------------------------|
| ignore_full | Accepts writes even while full. | No. The starter writes only three entries into an eight-entry FIFO. | Its count check could expose overflow if reached, but the starter never gets there. | Fill all eight entries, attempt another write, check count/full and drain the original contents. The reused HW4 suite catches it. |
| mem_corrupt | Stores each written byte plus one. | Yes. Every starter write activates the fault. | No. The starter checks count but never data. | Check the valid FWFT head and every outgoing item against the reference queue. The reused HW4 suite catches it. |

The other starter survivors were `full_offbyone`, `empty_offbyone`,
`ignore_empty`, `rd_data_wrptr`, and `wrptr_wrap_early`. Only `count_wr_dec`
was found by the starter. No released mutants survived the reused HW4 suite.

## What I changed, and what it bought

| Change | Score before | Score after | Which survivors it caught |
|--------|-------------:|------------:|---------------------------|
| Reused the existing HW4 driver, monitor, queue scoreboard, and boundary/data/request tests. | 1/8 | 8/8 | All seven starter survivors. This is reused coursework, not newly written Project 1 stimulus. |

The Project 1 coverage instrumentation counts pre-edge occupancy and requests
separately for directed operations, reset, and random campaigns. It measures
which combinations occurred; it is not evidence that pyvsc constraints have
been implemented or that coverage improvements caused the baseline score.

## Residual risk

1. Reachability: only WIDTH=8 and DEPTH=8 are tested. Coverage of every count
   and request pair does not cover every stored-data combination or long
   request history. The pyvsc distribution and replay behavior remain untested.
2. Observability: count, flags, and valid head data are sampled before and after
   the active edge. Between-sample glitches can be missed. Empty `rd_data` is
   not checked because the contract leaves it undefined.
3. The released pool has only eight mutants. A perfect released score does
   not establish the hidden score or correctness for every fault class.

**If I had another day:** I would finish the pyvsc campaigns, measure their
distribution and coverage independently of the directed checks, and replay
the same seeds before making closure claims.
