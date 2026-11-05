# Report section - Verification environment

**Author:** joshieyu (driver, monitor, cycle interface)
**Source:** `tb/fifo/fifo_driver.py`, `tb/fifo/fifo_monitor.py`, `tb/fifo/fifo_env.py`
**Evidence:** `evidence/driver-monitor/`

## Layers

```
requests -> FifoDriver -> fifo.sv -> FifoMonitor -> scoreboard (FifoModel queue)
                                          \-> coverage sampler (phase-named)
```

Each layer owns one thing. The driver is the only code that assigns DUT
inputs. The monitor only reads pins. The scoreboard owns expected state. The
coverage sampler only counts. `FifoEnv` connects them for one clock cycle. Its
caller passes in the scoreboard and coverage samplers. That lets a directed
test and a random test share the same pin-level code and choose their own
checker and coverage phase.

| Layer | API | Responsibility |
|-------|-----|----------------|
| `FifoDriver` | `init()`, `cycle(wr, rd, data)`, `reset(wr, rd, data)` | Drive `rst_n`, `wr_en`, `rd_en`, `wr_data` on the falling edge. Return 1 ns after the next rising edge. |
| `FifoMonitor` | `before_edge()`, `sample()` | Return one dict with the inputs at the pins and the outputs. |
| `FifoEnv` | `start()`, `cycle(...)`, `reset(...)` | Check the old state, sample coverage, step the reference queue from the sampled inputs, then check the new state. |

## Timing

The clock period is 10 ns. A cycle that starts at falling edge *t* runs as follows:

1. *t*: the driver applies the request. The monitor's pre-edge task waits on
   the same falling edge.
2. *t* + 1 ns: the monitor samples the new inputs and the **old** state. The
   scoreboard checks count, flags, and the FWFT head before the model moves.
   That includes the head a read on this edge will pop.
3. *t* + 5 ns: the rising edge. The DUT acts on the pre-edge state.
4. *t* + 6 ns: the driver returns. The monitor samples the **updated** state,
   and the scoreboard checks it against the stepped model.

Reset uses the same path with `rst_n = 0`. The pre-edge check requires the old
state to hold until the edge. That is the synchronous-reset contract. The
post-edge check requires `count = 0`, `empty = 1`, `full = 0`. `FIFO_TRACE=N`
logs both samples for the first N cycles.

## Sample format and what the scoreboard sees

Each sample holds `rst_n`, `wr_en`, `rd_en`, `wr_data`, `count`, `full`,
`empty`, and `rd_data`. `rd_data` is `None` while the DUT reports empty,
because the spec leaves it undefined then.

The reference queue steps on the **sampled** inputs, not the arguments the
test asked for. It models what actually reached the DUT. That would hide a
driver bug, since a queue fed by a broken driver agrees with the DUT. So
`FifoEnv` first checks that every sampled input equals the request. A
mismatch fails with a message that names the pin.

## Validation

| Check | Result |
|-------|--------|
| Clean suite after extraction | Pass. Simulated time is 552,341 ns, unchanged from the baseline. |
| `artifacts/coverage.yml` against `evidence/project-baseline/coverage.yml` | Byte-identical, so every cycle and coverage sample is the same. |
| Released mutant pool | 8/8 found, all `test-failed`. 20 s locally. |
| Monitor samples at the falling edge with no settle time (injected) | Fails: `rst_n: drove 1, monitor saw 0` |
| Driver never asserts `rd_en` (injected) | Fails: `rd_en: drove 1, monitor saw 0` |
| Driver returns at the rising edge with no settle time (injected) | Fails: `count: got 0, expected 1` |
| Reuse by a random test | `grad/tb/test_grad.py` drives pyvsc stimulus through the same `FifoEnv` with a random-only coverage phase. |

The three injected faults were each applied to a working copy. Each was
reverted after its run, and none was committed.

## Limits

- Outputs are sampled twice per cycle. A glitch between samples is not seen.
- `int(...)` on an X/Z output raises an error. That is a failure, not a
  silent pass. X/Z inputs are out of scope (vplan section 1).
- `rd_data` is not checked while empty.
- Only WIDTH=8 and DEPTH=8 are exercised.
