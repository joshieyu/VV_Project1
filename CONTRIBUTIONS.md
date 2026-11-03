# Contributions - Project 1 FIFO

**Members:** Kyle Coutray (`kylecoutray`), `joshieyu`, Jackal (GitHub username to confirm).
**Repo:** https://github.com/joshieyu/VV_Project1
**Last updated:** 2026-10-27

## 1. Completed work

| Member | What they owned | Evidence |
|--------|-----------------|----------|
| Kyle Coutray | Initialized the team repo with unchanged supplied FIFO sources, licenses, reference model, and mutation harness. | `17ae090` |
| Kyle Coutray | Reused his existing HW4 testbench and measured the original starter's 1/8 released score. | `7d77943`; `evidence/starter/` |
| Kyle Coutray | Drafted the Project 1 vplan, instrumented phase-specific occupancy/request coverage, and checked the baseline suite. | `dba08bb`; `evidence/hw4/`, `evidence/project-baseline/` |
| Kyle Coutray | Prepared setup instructions, proposed task split, baseline survivor analysis, and coverage status. | `README.md`, `TASKS.md`, `FINDINGS.md`, `closure.md` |
| joshieyu | Extracted the driver and monitor into `tb/fifo/fifo_driver.py` and `fifo_monitor.py`, added the shared per-cycle `FifoEnv`, extended monitor samples with `rst_n`/`wr_en`/`rd_en`/`wr_data`, and stepped the scoreboard from sampled inputs after checking them against the request. Validated by an unchanged clean run (byte-identical coverage), 8/8 released, and three injected environment faults. | branch `josh-driver-monitor`; `evidence/driver-monitor/`; `report/environment.md` |
| joshieyu | EEE5703 graduate extension: measured pyvsc rates, Markov-chain occupancy and corner bound, and a coverage vs. found/total regression. | `grad/` |

The HW4 driver, monitor, scoreboard, and sequences are reused work. They are
not claimed as new Project 1 code. No review is recorded yet.

## 2. Proposed responsibilities

| Member | Proposed work | Status |
|--------|---------------|--------|
| Kyle Coutray | Scoreboard, coverage model, vplan, and closure analysis. | Initial baseline complete; CRV integration and final analysis pending. |
| joshieyu | Driver/monitor extraction, sampled interface, environment demo. | Implemented and validated locally; clean run repeated on Eustis. |
| Jackal | pyvsc transactions, constraints, seeded regression, mutation campaigns. | Awaiting team agreement. |

## 3. Reviews and shared work

No cross-review has been completed yet. Each member should review another
layer and add the commit or artifact reviewed plus what was checked here.
Each person writes their report section and contributes to the demo.

## 4. Final checks

- [x] Third member identified: Jackal.
- [ ] Jackal's GitHub username and repo access confirmed.
- [ ] Each member has made their own commits.
- [ ] Every completed-work claim has supporting code or evidence.
- [ ] Each member has reviewed another layer.
- [ ] Final report and demo match the tested revision.
- [ ] All members agree this record describes their actual work.
