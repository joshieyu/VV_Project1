# Kyle - Check the Machine coverage-model experiment

Run November 12, 2026 (America/Chicago), with Icarus 13.0, Python 3.12,
cocotb 1.9.2 and cocotb-coverage 1.2.0. This is a new model-validation
experiment for vplan F2-F5/X1, separate from Jackal's pending CRV regression.

The candidate source and `prediction.md` were committed as `ed2b5cc`
**before the first execution**. `source-revision.txt` records the full hash.
The prediction wording is unchanged from `ed2b5cc`. Kyle made the prediction,
and it was committed with the before-run source. The original attribution note
incorrectly credited Codex and is corrected in `prediction.md`. Kyle later
confirmed his functionality review in `ai_log.md`.

## Reproduce

Activate the project environment, then run from the repository root:

```bash
make -C tb/fifo SIM=icarus RANDOM_SEED=4701 MODULE=test_coverage_probe
```

The command writes `artifacts/check_machine/results.json` and `coverage.yml`.
Retained copies, `run.log`, and `results.xml` are in this directory. Check the
JUnit/test summary, since this make flow can return zero even on test failure.
The probe is opt-in; the default test module remains `test_fifo`.

## Prediction and measurement

A compact candidate crosses empty/interior/full with the four requests.
The prediction was that it would report closure while hiding exact interior
count/request holes. The experiment samples every request at counts 0, 1,
and 8 through the existing driver, monitor and queue scoreboard. Both models
see exactly the same 12 probe cycles. Checked reset/fill/drain cycles are
deliberately outside that sampling phase. Thus the table describes the
controlled probe phase, not all traffic executed by the testbench.

| Model and sampling phase | Hit / total | Missing |
|--------------------------|------------:|--------:|
| Compact model, sparse probes | 12/12 | 0 |
| Exact model, same sparse probes | 12/36 | 24 |
| Exact model, separate full probe matrix | 36/36 | 0 |

The 24 holes are all four requests at each count from 2 through 7;
`results.json` lists them and all sampled triples. The clean DUT test passed
at 4,571 ns. The prediction held.

## Decision and limits

Reject the compact candidate as an X1 replacement and retain the existing
0-8 occupancy model. This is a model-selection correction, not a newly
discovered defect in the production coverage code. Supplying the full matrix
closed the exact model. No implementation fix was required after the first
run, and no constraint-tuning, final CRV, or mutation-score improvement is
claimed. The experiment shows why a percentage depends on the chosen bins;
it does not prove every data pattern or history is covered.

## Integration and report checks

The default `make -C tb/fifo SIM=icarus RANDOM_SEED=4701` run still passes
one test at 552,631 ns (`default-suite.log`, `default-suite.xml`), and its
coverage YAML matches `evidence/security/coverage.yml` byte-for-byte.
The mutation suite was not rerun for this opt-in model probe; no default
stimulus, checker, DUT or coverage sampler changed.
