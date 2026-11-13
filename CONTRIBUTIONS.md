# Contributions - Project 1 FIFO

**Members:** Kyle Coutray (`kylecoutray`), `joshieyu`, Jackal (`atm101010`).
**Repo:** https://github.com/joshieyu/VV_Project1
**Last updated:** 2026-11-12

## 1. Completed work

| Member | What they owned | Evidence |
|--------|-----------------|----------|
| Kyle Coutray | Initialized the team repo with unchanged supplied FIFO sources, licenses, reference model, and mutation harness. | `17ae090` |
| Kyle Coutray | Reused his existing HW4 testbench and measured the original starter's 1/8 released score. | `7d77943`; `evidence/starter/` |
| Kyle Coutray | Drafted the Project 1 vplan, instrumented phase-specific occupancy/request coverage, and checked the baseline suite. | `dba08bb`; `evidence/hw4/`, `evidence/project-baseline/` |
| Kyle Coutray | Prepared setup instructions, proposed task split, baseline survivor analysis, and coverage status. | `README.md`, `TASKS.md`, `FINDINGS.md`, `closure.md` |
| Kyle Coutray | Drafted the report contract/feature table, baseline coverage, two survivor analyses, own AI summary and reproduction note. | `report/latex/sections/`; `closure.md`, `FINDINGS.md`, `ai_log.md` |
| Kyle Coutray | Reviewed PRs 3 and 4, reproduced their combined revision from a fresh clone, and updated his coverage, survivor, and AI records. | `evidence/kyle-review/`; section 3 below |
| joshieyu | Extracted the driver and monitor into `tb/fifo/fifo_driver.py` and `fifo_monitor.py`, added the shared per-cycle `FifoEnv`, extended monitor samples with `rst_n`/`wr_en`/`rd_en`/`wr_data`, and stepped the scoreboard from sampled inputs after checking them against the request. Validated by an unchanged clean run (byte-identical coverage), 8/8 released, and three injected environment faults. | branch `josh-driver-monitor`; `evidence/driver-monitor/`; `report/environment.md` |
| joshieyu | EEE5703 graduate extension: measured pyvsc rates, Markov-chain occupancy and corner bound, and a coverage vs. found/total regression. | `grad/` |
| joshieyu | Security & Trust thread (vplan S1): coverpoint for read requests while empty after a reset or a drain, an exposure count for pre-reset data on `rd_data`, and an opt-in strict assertion. Shows the clean RTL leaks pre-reset data while empty, which the spec allows. 8/8 released still found. | branch `josh-security-trust`; `tb/fifo/fifo_trust.py`; `evidence/security/` |
| joshieyu | Team report setup: LaTeX skeleton synced with Overleaf, build and sync instructions, and `AGENTS.md` rules for teammates' AI agents. Wrote the environment, graduate extension, security, and AI-use (environment and extension part) sections. | branch `josh-report-skeleton`; `report/latex/`, `report/README.md`, `AGENTS.md` |
| joshieyu | Demo script for the environment and security segment, with each command checked against a run. | `report/demo_environment.md` |

The HW4 driver, monitor, scoreboard, and sequences are reused work. They are
not claimed as new Project 1 code. Reviews are recorded in section 3.

## 2. Proposed responsibilities

| Member | Proposed work | Status |
|--------|---------------|--------|
| Kyle Coutray | Scoreboard, coverage model, vplan, and closure analysis. | Baseline and PR 3/4 reviews complete; owned report sections drafted after the Overleaf pull. Final team CRV analysis and final-revision reproduction pending. |
| joshieyu | Driver/monitor extraction, sampled interface, environment demo, Security & Trust thread, report setup. | Environment validated locally and on Eustis. Security code, report sections, and demo script written; demo recording pending. |
| Jackal | pyvsc transactions, constraints, seeded regression, mutation campaigns. | Awaiting team agreement. |

## 3. Reviews and shared work

Each member reviews another layer and adds the commit or artifact reviewed
plus what was checked here. Each person writes their report section and
contributes to the demo.

| Reviewer | Reviewed | What was checked | Result |
|----------|----------|------------------|--------|
| Kyle Coutray (with Codex, 2026-11-04) | PR 1, corrected head `cced221` | Environment refactor and graduate Monte Carlo seed isolation; reran all 9,000 trials after fresh transaction construction per seed. | Found the continuing-RNG-stream defect before the fix; corrected totals and sample hashes reproduced. [Approval](https://github.com/joshieyu/VV_Project1/pull/1#pullrequestreview-5773473258). |
| Kyle Coutray (with Codex, 2026-11-12) | PR 4, `04384c1`: monitor, environment observer, S1 checker/stimulus and vplan | Independent clean/strict/released runs, observer timing, raw-data handling, reset/drain contexts and coverage traceability. Repeated clean/mutation from a fresh clone of integration candidate `384eb1e`. | Clean passes; XS1 4/4; 8/8 released, all test-failed; strict mode fails on the documented stale value at 10,011 ns. Coverage matches committed security evidence byte-for-byte. [Review](https://github.com/joshieyu/VV_Project1/pull/4#pullrequestreview-5885378932); `evidence/kyle-review/`. Final submission and Eustis reproduction are not claimed. |
| Kyle Coutray (with Codex, 2026-11-12) | PR 3, `0e69159`: report skeleton and subtree workflow | Built four-page draft with Tectonic and visually inspected all pages; checked section ownership, evidence references and dependency on PR 4. | Approved as a skeleton; final CRV, report and demo work remains. Preserve subtree merge commits. Overleaf access and prescribed latexmk build remain unverified by Kyle. [Review](https://github.com/joshieyu/VV_Project1/pull/3#pullrequestreview-5885379053). |
| joshieyu (with Claude Code, 2026-11-12) | Kyle's `7d77943`, `dba08bb`, and `3cc7995`: `vplan.md`, `FifoScoreboard` in `tb/fifo/test_fifo.py`, `lib/fifo_coverage.py`, `closure.md`, `FINDINGS.md` | Scoreboard steps the supplied reference queue and checks count, full, empty, and the head before and after every edge. Coverage bins match vplan C1-C4 and X1-X2, sampled from the reference count before the edge. The startup reset is not sampled, as `closure.md` says. Every closure row (36/36 per phase) matches `evidence/project-baseline/coverage.yml`. Every score in `FINDINGS.md` matches the `mutation.log` files in `evidence/starter/`, `evidence/hw4/`, and `evidence/project-baseline/`. | No errors found. Open items: `vplan.md`, `closure.md`, and `FINDINGS.md` still describe pyvsc as pending and need updating once `crv/` lands; vplan ambiguities 1 and 2 are still unconfirmed with course staff; each reset-cross bin is hit only once, so reset coverage has no margin. |

## 4. Final checks

- [x] Third member identified: Jackal.
- [ ] Jackal's GitHub username and repo access confirmed.
- [ ] Each member has made their own commits.
- [ ] Every completed-work claim has supporting code or evidence.
- [ ] Each member has reviewed another layer.
- [ ] Final report and demo match the tested revision.
- [ ] All members agree this record describes their actual work.
