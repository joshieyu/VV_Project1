# Demo segment - environment (joshieyu, about 2 minutes)

Record from the final tested revision with the environment activated.

## 1. Layers (30 s)

Show `tb/fifo/fifo_driver.py`, `fifo_monitor.py`, and `fifo_env.py` side by side.

- The driver is the only code that assigns pins, and it drives on the falling edge.
- The monitor only reads pins. Each sample includes the inputs that reached the DUT.
- `FifoEnv.cycle` checks the old state, samples coverage, steps the queue from
  the *sampled* inputs, then checks the new state.

## 2. Timing on a real trace (40 s)

```bash
FIFO_TRACE=4 make -C tb/fifo SIM=icarus RANDOM_SEED=4701 2>&1 | grep "after-edge sample"
```

Point at cycle 3. It requests a write and a read together while the FIFO is
empty. The pre-edge sample shows `count 0`. The post-edge sample shows
`count 1` and `rd_data 165` (0xa5). Only the write was accepted, which matches
Behavior 4 of the spec.

## 3. The environment checks itself (30 s)

Show `evidence/driver-monitor/sabotage.log`. Each of the three timing or
driver bugs fails with a message that names the layer at fault. Stress that
the queue steps on sampled inputs. Without the input check, a broken driver
would pass.

## 4. Reuse and result (20 s)

```bash
make -C tb/fifo SIM=icarus RANDOM_SEED=4701
diff artifacts/coverage.yml evidence/project-baseline/coverage.yml && echo identical
```

The coverage is byte-identical to the pre-refactor baseline, and the released
pool is still 8/8 (`evidence/driver-monitor/mutation.log`). Then show
`grad/tb/test_grad.py`, a pyvsc random-only test that reuses the same `FifoEnv`.
