# Project 1 - work plan

**Last updated:** 2026-10-27

**Deadline:** November 8, 2026 (Webcourses date confirmed by Kyle).

The split below is proposed. Kyle has started setup and the verification plan. The other owners need to confirm their tasks. Jackal is the third member; his repo access still needs confirmation.

## 1. Ownership

| Owner | Work | Done when | Review by |
|-------|------|-----------|-----------|
| Kyle | Verification plan, queue scoreboard, coverage model, closure analysis | Checks match the spec; coverage exports show hits and holes; closure claims cite runs. | joshieyu |
| joshieyu (proposed) | Driver/monitor extraction, reset and cycle interface, environment demo | Existing checks pass after moving reusable layers out of the test; pin samples agree with what the scoreboard receives. | Jackal |
| Jackal (proposed) | pyvsc transactions, burst/boundary constraints, seeded regression, mutation campaigns | Distribution is measured, seeds replay, random-phase X1 closes, and mutation evidence is saved. | Kyle |
| Everyone | Findings, report sections, demo, contributions | Each person explains their own layer and reviews another person's work. | Rotate |

## 2. Integration agreement

- Keep `dut/fifo.sv` unchanged. Test the contract in `dut/specs/fifo.md`.
- Current request arguments are `(wr_en, rd_en, wr_data)`. `FifoModel.step` takes `(wr_en, wr_data, rd_en)`; preserve that distinction.
- Drive at the falling edge; check the outgoing FWFT head before advancing the queue; check updated state after the rising edge.
- The driver owns pins, the monitor samples pins, and the scoreboard owns expected state. Extend the monitor to capture request/reset inputs when separating the layers.
- Update constraints from reference occupancy, not a possibly faulty DUT flag.
- Keep idle, write-only, read-only, and simultaneous requests reachable at every occupancy. Full writes and empty reads are legal requests with defined blocked behavior.
- Reuse the coverage sampler from the random sequence. Give it a separate phase name so directed coverage cannot fill random-phase holes.

## 3. Order of work

1. Confirm team access, current project spec, and proposed owners.
2. Everyone reproduces the clean run before changing code.
3. Driver/monitor extraction and pyvsc work can proceed against the agreed interface.
4. Measure initial random coverage and distribution. Save that evidence before tuning constraints.
5. Close holes, rerun released mutations, inspect failures, and record seed replay.
6. Write the 4-6 page report and record the demo from the final tested revision.
7. A different teammate checks out the final revision and repeats the documented commands.

Proposed checkpoints, leaving the final day for submission:

| Date | Target |
|------|--------|
| November 1 | Everyone can run the baseline; driver/monitor extraction and initial pyvsc stimulus are ready for integration. |
| November 4 | Integrated random regression runs; initial coverage, distribution, and seed-replay evidence are saved. |
| November 6 | Coverage holes addressed, mutations rerun, cross-reviews completed, and report draft ready. |
| November 7 | Final report and demo ready; another teammate reproduces the final revision. |
| November 8 | Check the final deliverables and submit by the Webcourses cutoff. |

## 4. Commit workflow

Use a branch per person's work. Kyle's branches use `kyle-...`; teammates choose their own names. Make commits for complete changes, such as driver/monitor extraction, transaction constraints, or coverage closure. Everyone commits through their own account.

Record reused HW4 code separately from new work. Update `CONTRIBUTIONS.md` with actual commits and review evidence. Do not fill in completion or equal-share claims ahead of the work.

## 5. Submission work still open

- Confirm the three ambiguities in vplan section 5 with course staff.
- Implement and validate the pyvsc regression, including the course-pinned pyvsc version and actual seed replay.
- Complete CRV convergence analysis; baseline coverage is not CRV closure.
- Write `REPORT.pdf` (4-6 pages) and record/link the demo.
- Confirm each person's contributions and submit by November 8.
