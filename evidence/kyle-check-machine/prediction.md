# Before-run prediction - Kyle's coverage-model experiment

Recorded November 12, 2026 (America/Chicago), before the first execution of
`tb/fifo/test_coverage_probe.py`. UTC reference: 2026-11-13 03:49:16.
This is a new experiment, not a reconstructed October record.

**Tool:** OpenAI Codex. **Scope:** vplan F2-F5 and X1.

**Prompt context:** Kyle accepted the proposed new, dated coverage/constraint
experiment to complete the Check the Machine evidence. Codex proposed and
drafted the compact model, the comparison test, and this prediction.

**Candidate model:** cross the three occupancy bands (empty, interior, full)
with the four requested operations. This compact alternative has 12 bins.

**Prediction:** the compact model will hide holes among the interior counts.
A phase sampling each request only at counts 0, 1, and 8 should close all
12 compact bins, while the exact occupancy/request model reaches only
12/36. Counts 2-7 should account for 24 unhit exact bins. Thus a claim of
complete X1 coverage from the compact model would be wrong.

**Verification:** apply those probes to the clean FIFO through `FifoEnv`
and the existing queue scoreboard. Sample compact and exact models on the
same probe cycles. Reset/fill/drain setup remains checked but is deliberately
outside this measurement phase; these are controlled model-validation
samples, not a claim about random-regression traffic. Then sample all 36
exact pairs in a separate phase to check that the retained exact model can
close when the missing situations are supplied. Save the sampled triples,
hit totals, missing bins, coverage YAML, simulation log and JUnit.

**Decision criterion:** if the prediction holds, reject the compact model
as a replacement for X1 and retain the existing exact occupancy model.
Record any unexpected result or required implementation fix after running.
No result is asserted yet in this before-run record.
