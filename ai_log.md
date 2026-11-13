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

**Dates:** October 27, November 4, and November 12, 2026.

**Reviewed for functionality by Kyle Coutray:** [x]

### Prompts and scope

**Planning prompt (verbatim excerpt):**

> plan out what to do, triage/assign tasks to people, then make separate
> commits for our own work.

**Verification prompts (paraphrased):**

> **Understanding the contract**
>
> “Before suggesting changes, quiz me on reset priority, simultaneous read/write at empty and full, and FWFT behavior. Let me answer first. Then compare my answers against the supplied FIFO contract and identify misunderstandings.”
>
> 1. **Reviewing your existing HW4 testbench**
>    “Inspect my existing HW4 scoreboard against the Project 1 requirements. Identify which requirements it already checks and which need additional verification. Explain each proposed addition and its purpose before implementing it.”
> 2. **Developing the verification plan**
>    “Review the F1–F7 requirement-to-test mapping in my draft `vplan.md`. Identify missing requirements, redundant coverage, and assumptions that need clarification. Keep my structure and explain the reason for each suggested change.”
> 3. **Making a genuine before-run prediction**
>    “Before running the experiment, I predict that sampling all four requests only at counts 0, 1, and 8 will close the compact 12-bin model but leave the exact model at 12/36, with every request at counts 2–7 missing. Grouping the interior counts would hide those holes. Check whether the experiment can distinguish that prediction from an alternative outcome. Preserve my prediction separately from your feedback, then wait for me to finalize it before execution.”
> 4. **Interpreting coverage**
>    “Show me the raw coverage results and ask me to explain what closed and what remains untested. After I answer, check my interpretation. Keep directed coverage separate from random coverage, and explain why 100% occupancy coverage does not establish correct data ordering.”
> 5. **Analyzing survivors**
>    “For each survivor, help me distinguish failure to activate the fault from failure to observe its effect. Ask me to propose a catching sequence first. Then evaluate my proposal and identify the exact assertion that should fail.”
> 6. **Writing the report**
>    “Edit my analysis into a concise report section: the compact model closed 12/12 on sparse probes while the exact model reached 12/36; the starter did not activate `ignore_full`, and its count-only check could not observe `mem_corrupt`. Preserve my technical conclusions, flag unsupported claims, and trace every numerical result to evidence. Identify any substantive reasoning you add so I can review it.”
> 7. **Checking readiness**
>    “Walk me through reproducing the final revision from a fresh clone. Have me run the commands and interpret the outputs. Record failures and corrections, and leave my manual-review checkbox unchecked until I confirm the review.”

Kyle supplied the existing HW4 testbench, imported unchanged at `7d77943`
(`SOURCE.md`). Its driver, monitor, queue scoreboard and directed/random
sequences predate this project. The new project assistance was:

| Area | Codex assistance | Record |
|------|------------------|--------|
| Plan and coverage | Drafted `vplan.md`, `lib/fifo_coverage.py`, coverage hooks, and baseline setup/analysis docs. | `dba08bb`; `closure.md`, `FINDINGS.md` |
| Cross-review | Inspected PR 1's environment/graduate analysis and PRs 3/4's report/security layers; executed replay, clean, strict, mutation and build commands. | `CONTRIBUTIONS.md` section 3; `evidence/kyle-review/` |
| Report | Drafted Kyle's plan, coverage, survivor, AI-use and reproduction text; updated findings, closure and contribution records. | `report/latex/sections/`; this log |
| Model-quality check | Drafted the compact coverage candidate and `test_coverage_probe.py` to test Kyle's before-run prediction. | `ed2b5cc`; `evidence/kyle-check-machine/` |

### Predictions, measurements and decisions

I forgot to write down a prediction before running the new Project 1 coverage
model in October. The HW4 testbench was reused work. On November 12, I made
one for a separate coverage-model experiment and committed it before the run.

| Before-run record | Measurement | Outcome / decision |
|-------------------|-------------|--------------------|
| November 12 integration prediction: PRs 3/4 should retain directed/reset X1/X2 at 36/36, all four HW4 random crosses at 36/36, XS1 at 4/4, and released mutation score at 8/8. | Fresh clone of `384eb1e` reproduced those results; mutations all failed tests, and coverage matched security evidence byte-for-byte. | Held. Evidence: `evidence/kyle-review/fresh/`. This is baseline integration, not final team CRV. |
| Kyle's November 12 model prediction, committed with the candidate in `ed2b5cc` before execution: a compact empty/interior/full cross can close while hiding 24 exact count/request pairs. | The same 12 sampled probes gave compact 12/12 and exact 12/36. Counts 2-7 lacked all four requests. A separate full matrix closed exact coverage 36/36. Clean DUT checks passed at 4,571 ns. | Held. Reject the compact candidate as an X1 replacement and retain the existing exact model. No implementation fix was needed after the first run. Evidence: `evidence/kyle-check-machine/`. |

Kyle made the November 12 prediction before execution, and it was committed
with the candidate source in `ed2b5cc`. The prediction text remains unchanged;
the file's attribution note was corrected after Kyle clarified authorship.
Checked setup/reset/drain cycles are excluded from the probe phase.

### Review findings and corrections

- The PR 1 review found a continuing RNG stream across nominal Monte Carlo
  seeds. After Joshua's fresh-object fix, all 9,000 trials reproduced totals
  and sample hashes; see his error 5 above and the PR 1 review.
- Strict mode returned shell status zero even when cocotb failed. Validation
  used the test summary/JUnit rather than shell status alone.
- Report drafts distinguish HW4 Python-random and graduate-extension results
  from the missing team CRV results. Final CRV claims remain pending.
- A LaTeX spacing warning in the model-check paragraph was fixed by shortening
  the heading and reflowing its opening sentence. The six-page draft then
  built without final-pass warnings; current proposal validation is recorded
  in `report/restructure-validation.md`.
- The default suite still passes with byte-identical baseline coverage. The
  opt-in probe does not change the default test, production sampler or DUT.
  No mutation-score improvement is attributed to it.
