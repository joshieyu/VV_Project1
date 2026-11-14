# Contributions - Project 1 FIFO

**Members:** Kyle Coutray (`kylecoutray`), `joshieyu`, Aaron Money (Jackal, `atm101010`).
**Repo:** https://github.com/joshieyu/VV_Project1
**Last updated:** 2026-11-14

Kyle owns the verification plan, scoreboard and coverage work, closure and
survivor analysis, cross-reviews, and corresponding report sections. His plan
maps FIFO requirements to tests, coverage bins, and checks. His coverage
analysis tested whether a compact occupancy/request model concealed holes;
his starter-survivor analysis separates faults the stimulus did not reach
from faults the checker did not observe. He also reviewed the environment and
security integration. The baseline reuses his HW4 queue scoreboard and
directed/random sequences (`SOURCE.md`); those are prior coursework, not new
Project 1 code. The records below distinguish completed work from the final
team CRV analysis and reproduction still pending; `ai_log.md` documents tool
assistance.

## 1. Completed work

| Member | What they owned | Evidence |
|--------|-----------------|----------|
| Kyle Coutray | Established the supplied-source baseline and reused the existing HW4 driver, monitor, queue scoreboard and tests. | `17ae090`, `7d77943`; `SOURCE.md`; `evidence/starter/`, `evidence/hw4/` |
| Kyle Coutray | Verification plan, phase-specific occupancy/request coverage, setup and task handoff. | `dba08bb`; `vplan.md`, `lib/fifo_coverage.py`, `README.md`, `TASKS.md` |
| Kyle Coutray | Coverage closure and mutation analysis, including reachability and observability explanations for two starter survivors. | `closure.md`, `FINDINGS.md`; retained clean/mutation evidence |
| Kyle Coutray | Cross-reviewed PRs 1, 3 and 4; reproduced the report/security integration from a fresh clone. | Section 3; `evidence/kyle-review/` |
| Kyle Coutray | Validated coverage-model granularity with a before-run prediction and controlled DUT probes; retained the exact model after the compact model hid 24 holes. | `ed2b5cc`; `tb/fifo/test_coverage_probe.py`; `evidence/kyle-check-machine/` |
| Kyle Coutray | Report contract/feature table, baseline coverage, survivor analysis, own AI-use summary and reproduction note. | Owned portions of `report/latex/sections/`; final team CRV results remain pending. |
| joshieyu | Extracted the driver and monitor into `tb/fifo/fifo_driver.py` and `fifo_monitor.py`, added the shared per-cycle `FifoEnv`, extended monitor samples with `rst_n`/`wr_en`/`rd_en`/`wr_data`, and stepped the scoreboard from sampled inputs after checking them against the request. Validated by an unchanged clean run (byte-identical coverage), 8/8 released, and three injected environment faults. | branch `josh-driver-monitor`; `evidence/driver-monitor/`; `report/environment.md` |
| joshieyu | EEE5703 graduate extension: measured pyvsc rates, Markov-chain occupancy and corner bound, and a coverage vs. found/total regression. | `grad/` |
| joshieyu | Security & Trust thread (vplan S1): coverpoint for read requests while empty after a reset or a drain, an exposure count for pre-reset data on `rd_data`, and an opt-in strict assertion. Shows the clean RTL leaks pre-reset data while empty, which the spec allows. 8/8 released still found. | branch `josh-security-trust`; `tb/fifo/fifo_trust.py`; `evidence/security/` |
| joshieyu | Team report setup: LaTeX skeleton synced with Overleaf, build and sync instructions, and `AGENTS.md` rules for teammates' AI agents. Wrote the environment, graduate extension, security, and AI-use (environment and extension part) sections. | branch `josh-report-skeleton`; `report/latex/`, `report/README.md`, `AGENTS.md` |
| joshieyu | Demo script for the environment and security segment, with each command checked against a run. Recorded and uploaded the demo. | `report/demo_environment.md`; https://youtu.be/8VbUyT3RlDk |

The HW4 driver, monitor, scoreboard, and sequences are reused work. They are
not claimed as new Project 1 code. Reviews are recorded in section 3.

## 2. Proposed responsibilities

| Member | Proposed work | Status |
|--------|---------------|--------|
| Kyle Coutray | Scoreboard, coverage model, vplan, and closure analysis. | Baseline, model-quality check and cross-reviews complete; report sections drafted. Final team CRV analysis and final-revision reproduction pending. |
| joshieyu | Driver/monitor extraction, sampled interface, environment demo, Security & Trust thread, report setup. | Environment validated locally and on Eustis. Security code, report sections, and demo written and recorded. |
| Jackal | pyvsc transactions, constraints, seeded regression, mutation campaigns. | Awaiting team agreement. |

## 3. Reviews and shared work

Each member reviews another layer and adds the commit or artifact reviewed
plus what was checked here. Each person writes their report section and
contributes to the demo.

Kyle's review entries used Codex for code inspection and validation-command
execution; the scope and results are recorded in his `ai_log.md` section.

| Reviewer | Reviewed | What was checked | Result |
|----------|----------|------------------|--------|
| Kyle Coutray (2026-11-04) | PR 1, corrected head `cced221`: environment and graduate analysis | RNG lifetime per Monte Carlo seed; 9,000-trial reproduction after the fresh-object fix. | The continuing-stream defect was caught; corrected totals and sample hashes reproduced. [Review](https://github.com/joshieyu/VV_Project1/pull/1#pullrequestreview-5773473258). |
| Kyle Coutray (2026-11-12) | PR 4, `04384c1`: monitor, observer, S1 sequence and vplan | Raw samples, observer timing, reset/drain contexts, clean/strict/mutation runs; fresh-clone integration at `384eb1e`. | Clean passes; XS1 4/4; released 8/8, all test-failed; strict mode fails at 10,011 ns. Coverage matches security evidence. [Review](https://github.com/joshieyu/VV_Project1/pull/4#pullrequestreview-5885378932); `evidence/kyle-review/`. |
| Kyle Coutray (2026-11-12) | PR 3, `0e69159`: report skeleton | Owned sections, evidence references, dependency on PR 4, subtree workflow and four-page Tectonic build. | Approved as a skeleton. Final CRV/demo work remains; current local report validation is separate. [Review](https://github.com/joshieyu/VV_Project1/pull/3#pullrequestreview-5885379053). |
| joshieyu (with Claude Code, 2026-11-12) | Kyle's `7d77943`, `dba08bb`, and `3cc7995`: `vplan.md`, `FifoScoreboard` in `tb/fifo/test_fifo.py`, `lib/fifo_coverage.py`, `closure.md`, `FINDINGS.md` | Scoreboard steps the supplied reference queue and checks count, full, empty, and the head before and after every edge. Coverage bins match vplan C1-C4 and X1-X2, sampled from the reference count before the edge. The startup reset is not sampled, as `closure.md` says. Every closure row (36/36 per phase) matches `evidence/project-baseline/coverage.yml`. Every score in `FINDINGS.md` matches the `mutation.log` files in `evidence/starter/`, `evidence/hw4/`, and `evidence/project-baseline/`. | No errors found. Open items: `vplan.md`, `closure.md`, and `FINDINGS.md` still describe pyvsc as pending and need updating once `crv/` lands; vplan ambiguities 1 and 2 are still unconfirmed with course staff; each reset-cross bin is hit only once, so reset coverage has no margin. |

## 4. Final checks

- [x] Third member identified: Jackal.
- [ ] Jackal's GitHub username and repo access confirmed.
- [ ] Each member has made their own commits.
- [ ] Every completed-work claim has supporting code or evidence.
- [ ] Each member has reviewed another layer.
- [ ] Final report and demo match the tested revision.
- [ ] All members agree this record describes their actual work.
