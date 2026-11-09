# AI log - Project 1 FIFO

Each member records their own AI use: the prompt, the prediction made before
running, the evidence, and every fix.

## joshieyu - environment layer and graduate extension

**Tool:** Claude Code (Anthropic, Claude Opus 5.5), terminal agent with shell access to this repo.
**Date:** 2026-10-31.
**Reviewed for functionality by joshieyu:** [x]

**Prompt (verbatim, abridged to the task):**

> Help me complete my portion of my verification/validation group project ...
> Also help me complete the graduate extension as a latex file ... Make sure to
> include AI disclosures where appropriate.

The teammate's task list for the driver/monitor layer was pasted with it.

### What the assistant drafted

- `tb/fifo/fifo_driver.py`, `fifo_monitor.py`, `fifo_env.py`, and the rewiring
  of `tb/fifo/test_fifo.py`.
- `report/environment.md` and `report/demo_environment.md`.
- `grad/`: the pyvsc constraint used for the extension, the random-only test,
  the regression and analysis scripts, and `grad/Project1_Extension.tex`.

### Check the Machine: predictions, evidence, fixes

| # | Prediction before running | Evidence | Outcome |
|---|---------------------------|----------|---------|
| 1 | Moving the driver and monitor out of the test changes no stimulus or sampling, so coverage stays identical. | `diff artifacts/coverage.yml evidence/project-baseline/coverage.yml` reports no difference. Simulated time is 552,341 ns both times. | Held. |
| 2 | Stepping the queue from sampled inputs would hide a broken driver unless sampled inputs are checked against the request. | Injected faults in `evidence/driver-monitor/sabotage.log`. All three fail, and two fail on the input check. | Held. The input check was kept. |
| 3 | A roll-plus-`implies` constraint on the pinned pyvsc would not give its nominal rate. HW5 measured compression toward 0.5. | Nominal 0.30 measured 0.37. With `vsc.solve_order(roll, enable)` it measured 0.31. | Held. The extension constraint uses `solve_order`, and the analysis measures every band instead of trusting the text. |
| 4 | With 50/50 end bands, the phased constraint would close X1 about as fast as uniform. The estimate was about 0.014 per cycle for the rarest end bin, against about 0.016 for uniform. | `grad/results/regression.csv`: phased closed X1 in 5/5 seeds at N=256. Uniform closed it in 3/5 at N=256 and 5/5 at N=512. | **Wrong.** Phased was about twice as fast, because the uniform walk diffuses and takes long stretches away from the ends. The extension reports the measured result. |
| 5 | The exact chain says a=0.75 reaches full-with-read within 48 draws with P=0.9999. A pyvsc Monte Carlo should agree. | After the reseeding fix (error 5): 2999/3000 seeds, 0.9997 [0.9981, 0.9999]. The chain built on measured rates gives 0.9998. The first run reported 0.9993 [0.9976, 0.9998] from one continuing stream. | Consistent both times. 3000 seeds cannot resolve the fourth digit, and the write-up says so. |

**Errors the assistant made and fixed:**

1. The first post-refactor clean run redirected its log to a bad path. The
   simulation did not run, so the first coverage diff compared stale files.
   It was caught because the log was missing, then rerun. Only the rerun is
   cited.
2. `grad/run_regression.py` read the harness JSON key `rows`, but the harness
   writes `mutants`. The single-point smoke test failed, and the key was fixed
   before the full grid.
3. A draft of `report/environment.md` said the pre-edge sample is the *only*
   place the outgoing head can be checked. The previous cycle's post-edge
   sample shows the same head, so the sentence was rewritten.
4. The first extension draft said the regression was 720 simulations. The
   harness also reruns clean RTL for every point, so the real count is 800.
   The draft was corrected.
5. Kyle Coutray's review of PR 1 (2026-11-04) found that `monte_carlo` in
   `grad/analyze.py` built one pyvsc object outside the loop. A pyvsc object
   seeds its own generator from the stdlib one on its first `randomize()`, so
   the later `random.seed()` calls did nothing. The 3000 "trials" were one
   continuing stream. The assistant had assumed pyvsc reads the stdlib
   generator on every draw. Each trial now seeds and then builds a new
   object, and the analysis was rerun. Phased went from 0.9993 to 0.9997,
   unordered from 0.8997 to 0.8983, and uniform from 0.1897 to 0.2010. All
   three still contain the chain value. `grad/results/mc_reproduce.log` shows
   nine trials reproducing when run alone. It also shows that changing an
   earlier seed no longer changes a later trial.
6. Rebuilding the write-up with `-halt-on-error` showed that it used
   `\mathbb` without loading `amssymb`. The first PDF had been built past that
   error. The package was added and the PDF rebuilt with no errors.

The numbers in the report and the extension come from the logged runs in
`evidence/driver-monitor/` and `grad/results/`, not from the assistant's
claims.

### Security & Trust coverpoint (2026-11-09)

**Prompt:** "Build it" (accepting the assistant's offer to build the missing
Security & Trust coverpoint).
**Reviewed for functionality by joshieyu:** [ ]

The assistant drafted `tb/fifo/fifo_trust.py`, the observer hook in
`fifo_env.py`, the `rd_data_raw` field in `fifo_monitor.py`, the S1 sequence
in `test_fifo.py`, and the vplan, README, and evidence notes.

| # | Prediction before running | Evidence | Outcome |
|---|---------------------------|----------|---------|
| 6 | Reset clears the pointers but not memory, so an empty FIFO right after a reset would show a word written before it. This was predicted from the RTL, which is why it is reported as a trust finding and not as a spec failure. | `evidence/security/clean.log`: 2439 of 7058 read requests at empty showed a pre-reset word. `strict.log` fails at 10,011 ns on 0xaa. | Held. |
| 7 | The observer only reads samples, so the released pool would stay 8/8 and no mutant result would change. | `evidence/security/mutation.log`: 8/8, all `test-failed`. | Held. |

**Errors in this part:**

- The first draft only counted the after-reset case when the reset discarded
  data. A reset of an empty FIFO also moves the read pointer back to slot 0,
  so it can expose old data too. Fixed before the first run.
- The first evidence note said every coverage item other than `fifo.trust`
  was unchanged. A YAML diff showed the directed and reset hit counts grew
  (all bins still closed). The note was corrected before commit.
