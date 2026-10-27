# Verification plan - synchronous FIFO

**Author:** Kyle Coutray
**Spec version:** `dut/specs/fifo.md`, supplied fall2026 packet.
**Date:** 2026-10-27

## 1. Scope

**In scope:** The synchronous FWFT FIFO at WIDTH=8 and DEPTH=8. Check reset, request acceptance, count, flags, data order, and pointer wrap. Extend the HW4 checks with pyvsc stimulus and measured functional coverage.

**Out of scope:** Other parameter values, physical timing, X/Z stimulus, and features absent from the supplied spec.

**Assumptions about the environment:** Drive on the falling edge. Sample the old state before the rising edge and the updated state 1 ns after it. Reset is active-low and synchronous. Read/write acceptance uses the state before the edge. Data is checked only when the reference queue is nonempty.

## 2. Feature list

| ID | Feature | Req | Priority | How it is verified |
|----|---------|-----|----------|--------------------|
| F1 | Synchronous reset clears state, including with active requests | Behavior 1 | H | directed reset checks; request/occupancy cross |
| F2 | Writes are accepted unless full; blocked writes preserve data | Behavior 2 | H | queue scoreboard; directed and CRV |
| F3 | Reads are accepted unless empty; blocked reads preserve state | Behavior 3 | H | queue scoreboard; directed and CRV |
| F4 | Simultaneous requests use pre-edge occupancy | Behavior 2-4 | H | occupancy x request cross; scoreboard |
| F5 | Full, empty, and count agree with the reference queue | Behavior 5 | H | checks before and after each edge |
| F6 | Valid FWFT head and FIFO ordering are correct | Behavior 3, 6 | H | compare the outgoing head before advancing the queue; drain each campaign |
| F7 | Repeated accepted reads and writes preserve order through wrap | Corner cases | H | repeated fill/drain and interleaved traffic |

## 3. Coverage model

| ID | Coverpoint | Bins | Why these bins |
|----|-----------|------|----------------|
| C1 | Pre-edge occupancy in normal operation | 0 through 8 | Includes both boundaries and every interior count. |
| C2 | Requested operation in normal operation | idle, write, read, simultaneous | Requests differ from accepted operations at full and empty. |
| C3 | Pre-edge occupancy when reset is applied | 0 through 8 | Reset must discard any amount of queued data. |
| C4 | Requests when reset is applied | idle, write, read, simultaneous | Checks whether requests interfere with reset. |

**Crosses**

| ID | Cross | The interaction it is aimed at |
|----|-------|-------------------------------|
| X1 | C1 x C2: 36 bins | Incorrect gating and count updates at a particular occupancy. |
| X2 | C3 x C4: 36 bins | Reset ignored or delayed when requests are active. |

Sample occupancy from the checked reference queue before its update. Sample the requested operation, including dropped/ignored requests. Record directed and random phases separately so directed tests cannot hide gaps in CRV. These bins do not measure every data pattern, pointer position, or request history; F6/F7 still need their checks and tests.

**Illegal / ignore bins:** None in these crosses. The spec explicitly permits write-while-full and read-while-empty. Do not exclude those bins. `rd_data` while empty is not compared because the spec does not define it. Out-of-range count is a scoreboard failure, not an ignored bin.

## 4. Test matrix

| Test or sequence | Features | Kind | Pass criterion |
|------------------|----------|------|----------------|
| HW4 reset matrix | F1, F5 | directed | Old state holds until the rising edge; reset then clears count/flags for every occupancy/request pair. |
| Fill, drain, and blocked requests | F2, F3, F5, F6 | directed | Accepted data drains in order; blocked requests do not corrupt it. |
| Simultaneous requests and request-pair sweep | F2-F6 | directed | At empty only write is accepted; at full only read; inside the boundaries both are accepted. |
| Repeated wrap and data sweeps | F2-F7 | directed | Reference queue and valid head match across repeated reuse of slots. |
| Existing HW4 seeded traffic | F2-F7 | Python random baseline | Every checked sample agrees with the queue; trailing data drains correctly. |
| Project constrained-random campaigns | F2-F7 | pyvsc, pending | Multiple recorded seeds pass; normal occupancy x request coverage closes; measured rates support the claimed distribution. |

## 5. Risk and spec ambiguity

| # | Ambiguity or risk | Where in the spec | How I resolved it | Residual |
|---|-------------------|-------------------|-------------------|----------|
| 1 | Handout mentions almost_full and optional FWFT; packet has neither option. | Handout vs. ports/parameters | Plan follows the packet's FWFT contract. | Confirm whether Webcourses supplies a newer project DUT. |
| 2 | Handout asks for two survivor analyses even if final released score is perfect. | Mutation task | Preserve measured starter survivors and compare them with the improved suite. | Confirm that baseline survivor analysis is acceptable. |
| 3 | Security task asks for illegal/undefined controls, but example reset/boundary cases are defined here. | Handout Security & Trust | Cover reset with requests and boundary behavior; describe the contract accurately. | Confirm whether these satisfy that task or another case is required. |
| 4 | A high score can hide weak random stimulus. | Project coverage/reproducibility tasks | Keep phase-specific coverage and measure distributions. | CRV and seed replay remain pending. |

## 6. Closure criteria

- Functional coverage target: **100%** of C1-C4 and X1-X2 in the complete suite. Additionally, the pyvsc phase must close X1 across the recorded regression without credit from directed tests. Reset bins may be directed because they verify synchronous timing and reset priority.
- Mutation target: **90% or better** on the hidden pool at grading. Record released found/total separately; never infer a hidden result from it.
- Checks: clean RTL passes first; mutation failures must be inspected for assertion failures rather than build errors or timeouts.
- Reproducibility: record commands, versions, seeds, cycle budgets, and source revision. Replay the same pyvsc seed and compare the generated transactions.
- Continue checking beyond the last new coverage bin and drain the queue before stopping.

### what this does NOT verify

This does not prove every data combination or request history. The tests use WIDTH=8 and DEPTH=8 and sample at defined times, so other sizes and between-sample glitches remain unverified. Coverage says which situations occurred; the scoreboard and mutation results are separate evidence about checking quality.
