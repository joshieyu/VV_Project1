# Coverage closure - FIFO baseline - Kyle Coutray

## 1. The number

The initial instrumented HW4 run closes the normal directed cross and reset
cross: **36/36 bins each**. All associated occupancy/request coverpoints are
closed. The target in `vplan.md` is 100%.

| Phase | Occupancy x request bins |
|-------|--------------------------|
| Directed normal operations | 36/36 |
| Directed reset cases | 36/36 |
| HW4 Python random, seed 4701 (500 cycles) | 36/36 |
| HW4 Python random, seed 4702 (2,048 cycles) | 36/36 |
| HW4 Python random, seed 4703 (2,048 cycles) | 36/36 |
| HW4 Python random, seed 4704 (2,048 cycles) | 36/36 |

Final directed drains are counted in the directed group, not in random groups.
Each row's cross has its own nine occupancy bins and four request bins.

The current HW4 campaigns use Python random, not pyvsc. Their per-seed reports
are separate from directed coverage. Project constrained-random closure is
**pending**, even if the baseline bins are already closed.

**How the report was produced:**

```bash
make -C tb/fifo SIM=icarus RANDOM_SEED=4701
```

`lib/fifo_coverage.py` exports `artifacts/coverage.yml`. A retained clean-run
copy and simulation log are stored in `evidence/project-baseline/`.

## 2. The convergence argument

No pyvsc tuning/convergence result is claimed yet. The existing directed
matrix explicitly visits every occupancy and request pair; its closed bins
are expected. It was retained to check the spec and establish a working
baseline before changing the stimulus.

The constraints owner should save the first random-phase report, identify
missing bins, change constraints, and compare the next report using recorded
seeds and cycle budgets. Record vectors to closure and continued checking
after closure. Justify any directed closure separately.

## 3. Bin justification

There are no illegal/ignore bins in either cross. `dut/specs/fifo.md`, Behavior
2 and 3, defines writes while full as dropped and reads while empty as ignored.
Both requests must be covered. Sampling uses the reference count before the
edge, so a request at full cannot be mislabeled as a request at count seven
after its simultaneous read.

Reset coverage counts each request pair at every pre-reset occupancy. The
initial startup reset is excluded because there is no initialized prior state
to compare. Subsequent resets are checked before and after the rising edge.

## 4. What the cross is aimed at

The normal cross targets state-dependent acceptance, flag, and count errors.
The reset cross targets requests incorrectly taking priority over reset.
Neither cross alone detects corrupted data. The queue scoreboard must compare
the head and data order even after every cross bin has been hit.

## 5. Coverage vs. correctness - the blind spots

1. Every occupancy/request pair can occur while some data patterns and long
   histories remain untested.
2. These crosses do not measure all pointer positions or parameter values.
3. Sampled checks can miss transient errors between sampling points.
4. A closed directed model says nothing about the pyvsc distribution or seed
   replay until those are implemented and measured independently.

## 6. Correlation with mutation

The starter scored 1/8 and the reused HW4 suite scored 8/8. That improvement
predates the new coverage instrumentation, so it is not a measured effect of
constraint tuning. See `FINDINGS.md` for the two baseline survivor analyses.
