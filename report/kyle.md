# Kyle's report draft

Prepared November 12, 2026. Pending transfer into Kyle's owned LaTeX
sections after the required Overleaf pull. Project access is now available;
Git authentication is being set up. Other members' sections are unchanged.

## DUT and verification plan

The supplied contract (`dut/specs/fifo.md`) is an 8-bit, eight-entry
synchronous FIFO with a first-word fall-through output. Active-low reset
clears count and pointers on the rising edge. Acceptance uses pre-edge
occupancy: writes at full are dropped and reads at empty are ignored.
With simultaneous requests, only the write is accepted at empty, only the
read at full, and both in the interior. Count and flags must match the
reference queue; the valid head must preserve insertion order.

| vplan ID | Requirement | Test / coverage or check |
|----------|-------------|-------------------------|
| F1 | Synchronous reset and priority | Reset matrix; C3/C4 and X2; state checks |
| F2 | Accepted and blocked writes | Fill/overflow sequences; X1; queue contents |
| F3 | Accepted and ignored reads | Drain/underflow sequences; X1; state checks |
| F4 | Simultaneous acceptance | Boundary/interior request sweep; X1 |
| F5 | Count/full/empty | Reference checks before and after each edge |
| F6 | FWFT head and ordering | Valid-head comparison and campaign drains |
| F7 | Pointer wrap | Repeated fill/drain and interleaved traffic |
| S1 | Undefined empty output | Reset/drain empty reads; XS1; exposure observer |

F1-F7 have high priority; the S1 trust observation has medium priority
because empty output data is outside the functional contract. Full writes
and empty reads are legal requests, not illegal stimulus. The plan follows
the supplied packet's FWFT contract; the handout's almost-full/optional-FWFT
wording still needs clarification. Acceptance of starter survivors for the
two-survivor requirement also needs confirmation (`vplan.md`, section 5).
Other sizes, between-sample transients, and all possible data histories
remain outside the demonstrated coverage.

## Coverage model and closure

X1 crosses pre-edge reference occupancy 0-8 with idle, write, read, and
simultaneous requests: 36 bins. X2 uses the same dimensions when reset is
applied. No bins are illegal or ignored because the contract defines both
blocked boundary requests. Startup reset has no initialized prior state
and is excluded from X2. Directed and random traffic have distinct sampler
names so directed hits cannot fill random holes (F1-F5).

The retained clean run tests integration candidate `384eb1e`:

```bash
make -C tb/fifo SIM=icarus RANDOM_SEED=4701
```

The coverage and clean log are in `evidence/kyle-review/fresh/`.

| Phase | Cross hits / bins |
|-------|------------------|
| Directed X1 | 36/36 |
| Reset X2 | 36/36 |
| HW4 Python random, each of seeds 4701-4704 | 36/36 each |
| S1 reset/drain context x empty-read request | 4/4 |

These are baseline results, not final team CRV closure. The directed matrix
explicitly visits each occupancy/request pair, so its closure is expected.
The final YAML gives hit totals, not the order of holes closing. F6/F7
still require data/order checks after bin closure. Joshua's `grad/`
experiment is separate from Jackal's pending team `crv/` implementation.

**TODO Kyle and Jackal:** after the team regression, report random-only
hits/holes, seeds and budgets, measured request rates, constraint changes,
the last-new-bin draw index, replay results, and continued checking/drain.
Justify any directed closure separately. See `closure.md`.

## Mutation: two measured survivor analyses

**Jackal's final-score subsection remains pending.** The examples below are
measured starter survivors, not survivors of the final project suite.
`evidence/starter/mutation.log` records 1/8; the reused HW4 and current
security integration find 8/8 (`FINDINGS.md`, `evidence/kyle-review/`).
The improvement predates CRV tuning.

| Survivor | Why missed | What catches it |
|----------|------------|-----------------|
| `ignore_full` (F2/F5) | The starter writes three items into an eight-entry FIFO, so the faulty full write is unreachable. | Fill to eight, attempt another write, check unchanged count/full and drain the original data. The full/write X1 bin shows reachability; assertions detect the fault. |
| `mem_corrupt` (F6) | Writes activate the corruption, but the starter checks count without checking data. | Compare every valid FWFT head against the reference queue and drain in order. Occupancy coverage alone cannot detect it. |

Both are caught by the reused HW4 and reviewed integration suite. No
released mutant survives those suites. Confirm that baseline survivors
satisfy the assignment before treating this as the final survivor analysis;
retain Jackal's final run and any additional survivors when available.

## Check the Machine: Kyle

Codex drafted the coverage model, plan, baseline analyses, and these report
sections, and assisted the PR reviews. `ai_log.md` records prompts, files,
evidence, and corrections. Before the fresh-clone integration run, the
recorded prediction was that both 36-bin directed/reset crosses, all four
HW4 random crosses, XS1 (4/4), and the released score (8/8) would remain
closed. The run supported it (`evidence/kyle-review/`). No before-run
prediction was preserved for the October work, so none is reconstructed.
Review also caught the PR 1 RNG-lifetime error described in Joshua's
section. Kyle's manual functionality-review checkbox remains pending.

## Kyle's reproduction and contribution record

Kyle's fresh clone of candidate `384eb1e` reproduced clean coverage and
8/8 released, using Icarus 13.0 and the existing Python environment. This
does not replace reproduction of the final integrated submission or an
Eustis run. Kyle owns the vplan, coverage and closure analysis, reused HW4
scoreboard, baseline survivor analysis, and reviews recorded in
`CONTRIBUTIONS.md` section 3. Other members complete their own records.
