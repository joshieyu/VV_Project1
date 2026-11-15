# Coverage closure - FIFO baseline and CRV - Kyle Coutray

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
| CRV uniform, seed 4701 (128 draws) | 32/36 |
| CRV tuned, seed 4701 (128 draws) | 34/36 |
| CRV tuned, seeds 4701, 4702, 4703 (2,048 draws each) | 36/36 each |

The November 12 review of PR 4 (`04384c1`) and a fresh-clone integration
run (`384eb1e`) reproduced the directed and HW4 rows above. S1 additionally closes **XS1
4/4**, with both context and request coverpoints at 2/2. Clean logs, JUnit,
coverage, commands, and versions are retained in `evidence/kyle-review/`.
Coverage was copied only after rerunning clean RTL after mutation.

Final directed drains are counted in the directed group, not in random groups.
Each row's cross has its own nine occupancy bins and four request bins.

The HW4 campaigns use Python random. The team `crv/` campaigns use pyvsc and
record random-only X1 separately from the HW4 and directed phases. Their
per-run YAML, transaction CSV, statistics, and logs are in `evidence/crv/`.
Joshua's `grad/` experiment is a separate extension.

**Commands for the retained runs:**

```bash
make -C tb/fifo SIM=icarus RANDOM_SEED=4701
python crv/run_regression.py --sim icarus --seeds 4701,4702,4703 \
  --short-cycles 128 --cycles 2048 --mutate
```

`lib/fifo_coverage.py` exports `artifacts/coverage.yml`. A retained clean-run
copy and simulation log are stored in `evidence/project-baseline/`.

## 2. The convergence argument

The directed matrix explicitly visits every occupancy/request pair, so its
closed bins are expected. For random-only X1, the same 128-draw seed covered
32/36 with uniform requests. It missed `0,1,1`, `1,0,0`, `1,0,1`, and `2,0,0`
(pre-edge count, write, read). The prewritten tuned fill/drain mode covered
34/36 at that budget, missing `2,0,0` and `5,1,1`. Observed write/read rates
were 48.44%/44.53% (uniform) and 53.91%/50.00% (tuned). These measured rates
do not by themselves prove closure.

With tuned mode and 2,048 draws, seeds 4701, 4702, and 4703 each reached
36/36. Their last new bins appeared at draws 196, 202, and 131, leaving
1,852, 1,846, and 1,917 additional checked random requests, respectively.
The test then disabled random-only sampling and drained the reference queue
through checked cycles. Seed 4701 was replayed in a fresh process and its
transaction CSV matched byte for byte. The equal-budget comparison shows
that tuning reduced holes from four to two; the larger budget closed the
remaining holes. The retained stats record first-hit cycles, unlike the
accumulated YAML. Evidence: `evidence/crv/regression_summary.json`, the
per-run `.stats.json` files, and the matching logs and coverage YAML.

## 3. Bin justification

There are no illegal/ignore bins in either cross. `dut/specs/fifo.md`, Behavior
2 and 3, defines writes while full as dropped and reads while empty as ignored.
Both requests must be covered. Sampling uses the reference count before the
edge, so a request at full cannot be mislabeled as a request at count seven
after its simultaneous read.

Reset coverage counts each request pair at every pre-reset occupancy. The
initial startup reset is excluded because there is no initialized prior state
to compare. Subsequent resets are checked before and after the rising edge.

The November 12 model-quality experiment supports keeping all nine occupancy
bins rather than combining counts 1-7 into one interior bin. On the same 12
selected probe cycles, a three-band candidate closed 12/12 while the exact
model hit 12/36 and exposed 24 missing pairs. A separate full probe matrix
closed 36/36. The before-run prediction, controlled sampling scope, code,
and measured results are in `evidence/kyle-check-machine/`. This validates
the bin distinction; it is separate from CRV convergence.

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
   replay; those were measured independently in `evidence/crv/`.
5. XS1 measures sampled empty reads in two contexts. Its exposure count uses
   byte values seen before but not since reset; repeated values can hide
   provenance. It is not a complete data-remanence measurement.

## 6. Correlation with mutation

The starter scored 1/8 and the reused HW4 suite scored 8/8. That improvement
predates the new coverage instrumentation, so it is not a measured effect of
constraint tuning. See `FINDINGS.md` for the two baseline survivor analyses.
The PR 4 and fresh-clone runs also found 8/8 released mutants through test
failures (`evidence/kyle-review/`). The final tuned CRV run independently
found 8/8 through test failures (`evidence/crv/mutation.log`). Because the
HW4 suite already found 8/8, this does not show a mutation-score gain from
CRV tuning. The released pool cannot establish a hidden-pool result.
