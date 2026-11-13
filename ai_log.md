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
- 2026-11-05: the report skeleton in `report/latex/` and its Overleaf subtree
  setup. The assistant wrote the environment and grad-extension sections, using
  `report/environment.md` and the extension's own numbers. It also wrote
  `AGENTS.md` for teammates' agents.

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
**Reviewed for functionality by joshieyu:** [x]

The assistant drafted `tb/fifo/fifo_trust.py`, the observer hook in
`fifo_env.py`, the `rd_data_raw` field in `fifo_monitor.py`, the S1 sequence
in `test_fifo.py`, and the vplan, README, and evidence notes. It also
rewrote `report/demo_environment.md` to add the S1 segment. Each command in
that script was rerun and its output matched the script.

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

## Kyle Coutray - coverage, reviews, and report

**Tool:** OpenAI Codex, terminal agent.
**Dates:** 2026-10-27 (baseline); 2026-11-04 (PR 1 review); 2026-11-12
(PRs 3 and 4, report and evidence updates).
**Reviewed for functionality by Kyle Coutray:** [ ]

**Prompts (verbatim, abridged):**

> We gotta plan out what to do, triage/assign tasks to people, then make
> separate commits for our own work.

> can you take a look at the other PRs, and the repo, and the project itself
> and see what we need to? also you'll have to do the tasks that my
> parterner assigned. just do it as if you're me: **Kyle**

The second prompt included the assigned plan, coverage, mutation, AI-log,
closure, findings, and cross-review work.

### Project scope and reused work

Kyle's assigned scope is the verification plan, scoreboard/coverage layer,
closure and survivor analysis, cross-review, and corresponding report text.
He provided his existing HW4 testbench for the project baseline. Commit
`7d77943` imports that coursework unchanged, including its driver, monitor,
queue scoreboard, directed sequences, and Python-random campaigns; see
`SOURCE.md`. The assistance below covers the new Project 1 changes,
analysis, validation runs, and documentation.

### Codex assistance within that scope

- Baseline `vplan.md`, `lib/fifo_coverage.py`, coverage hooks in the reused
  HW4 test, `closure.md`, `FINDINGS.md`, and team setup/contribution docs.
- PR 1's environment and graduate analysis, including the per-seed RNG
  lifetime error recorded above in Joshua's error 5.
- PR 3's report skeleton and PR 4's monitor/observer, S1 stimulus and XS1
  coverage, with independent clean, strict, and released-mutation runs.
- Kyle's report sections and evidence-backed updates to his closure,
  findings, contribution, and AI records. Jackal's final CRV numbers are
  pending; the graduate extension is a separate experiment.

### Check the Machine

No before-run prediction was preserved for the October baseline work or
the earlier PR 1 review. The results below do not retroactively supply one.
The PR 1 review found a continuing RNG stream across nominal seeds; after
the fresh-object fix, the 9,000-trial rerun reproduced totals and sample
hashes. See PR 1's review and `grad/results/mc_reproduce.log`.

**Prediction recorded before the fresh-clone integration run (2026-11-12):**
combining PRs 3 and 4 should retain X1 and X2 at 36/36, all four HW4 random
crosses at 36/36, XS1 at 4/4, and the released mutation score at 8/8.
A failure would indicate integration or environment drift. This predicts
neither Jackal's CRV closure nor hidden-mutant performance.

**Documentation risk identified before drafting the report:** closed Python
random bins or the graduate experiment could be mislabeled as the team's
final CRV result. Keep that distinction and the missing evidence explicit.

**Outcome:** the fresh-clone prediction held. `evidence/kyle-review/fresh/`
contains the clean JUnit/log, coverage and mutation JSON: both 36-bin
directed/reset crosses and each HW4 random cross close, XS1 is 4/4, and the
released score is 8/8 (all test-failed). Coverage is byte-identical to PR 4's
committed security evidence. The tested source is `384eb1e`; final team CRV
and final submission reproduction are still pending.

**Review corrections and limits:**

- The strict-mode command returned shell status zero while cocotb reported
  failure. The review checked the test summary/JUnit, not shell status alone.
- No missing team CRV measurement was replaced with a Python-random or
  graduate-extension result. The report draft labels its numbers as baseline
  and keeps the final-result/convergence TODOs.
- No historical prediction was invented for the baseline work. The human
  functionality-review checkbox above remains for Kyle to complete.
- Shared-project access was initially denied and subsequently granted.
  After Git authentication and pulling Overleaf `75d523e`, the reviewed
  draft was transferred into Kyle's owned portions of `report/latex/sections/`
  (`plan.tex`, `coverage.tex`, `mutation.tex`, `ai.tex`, and
  `reproducibility.tex`). Other members' sections and pending work remain.
  A six-page scratch preview was built and visually checked with Tectonic,
  then with the prescribed latexmk/pdfLaTeX command. The final TeX pass has
  no warnings; see `evidence/kyle-review/report-preview/`.
