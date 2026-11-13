# Demo segment: environment and security (joshieyu, about 3 minutes)

Record from the final tested revision, in a fresh terminal at the repo root
with the environment activated (`source .venv/bin/activate`). Run the clean
command once before recording so `sim_build/` is warm and the run takes a few
seconds. Use a large terminal font.

Each part lists what to show, then what to say. The "Say" lines are a guide,
not a script to read word for word.

## 1. The layers (40 s)

**Show:** `tb/fifo/fifo_driver.py`, `fifo_monitor.py`, and `fifo_env.py`
side by side. Scroll to `FifoEnv.cycle` in `fifo_env.py`.

**Say:**

- "We split the testbench into three layers. The driver is the only code that
  sets pins. It drives on the falling edge."
- "The monitor only reads pins. Each sample includes the inputs that actually
  reached the DUT, not just its outputs."
- "`FifoEnv.cycle` ties them together. Every cycle it checks the old state,
  samples coverage, steps the reference queue from the sampled inputs, and
  then checks the new state. The scoreboard is the HW4 reference queue,
  reused."

## 2. Timing on a real trace (40 s)

**Run:**

```bash
FIFO_TRACE=4 make -C tb/fifo SIM=icarus RANDOM_SEED=4701 2>&1 | grep "after-edge sample"
```

**Show:** the cycle 3 line.

**Say:**

- "Here are the first four cycles. In cycle 3 we ask for a write and a read
  at the same time while the FIFO is empty."
- "Before the edge, count is 0. After the edge, count is 1 and `rd_data` is
  165, which is the word we wrote. Only the write was accepted. That is what
  the spec says should happen for a read at empty."
- "In cycle 4 the read is accepted and the FIFO is empty again."

## 3. The environment checks itself (30 s)

**Show:** `evidence/driver-monitor/sabotage.log`.

**Say:**

- "To make sure the environment is not hiding bugs, we broke it on purpose
  three times."
- "If the monitor samples too early, or the driver drops `rd_en`, the run
  fails with a message that says what was driven and what was seen. If the
  driver stops waiting after the edge, the scoreboard catches the wrong count."
- "This works because the queue steps on what the monitor saw. A broken
  driver cannot fool the scoreboard."

## 4. Security and trust (50 s)

**Show:** `tb/fifo/fifo_trust.py`, then run the clean test:

```bash
make -C tb/fifo SIM=icarus RANDOM_SEED=4701 2>&1 | grep -E "S1:|TESTS="
```

**Say:**

- "The spec says `rd_data` only matters when the FIFO is not empty. So the
  normal checks never look at it while empty. We added a coverpoint there on
  purpose, vplan item S1."
- "It covers reads at empty right after a reset and after a drain, alone or
  racing a write. All four bins are hit."
- "Each time, it asks one question: is the FIFO showing a word that was
  written before the last reset? Point at the last `S1:` line. In the full run,
  2439 of 7058 empty reads did."
- "The reason is that reset clears the pointers but not the memory, and
  `rd_data` always shows the slot at the read pointer. The spec allows it, so
  the test still passes and just reports the count."

**Run:**

```bash
FIFO_TRUST_STRICT=1 make -C tb/fifo SIM=icarus RANDOM_SEED=4701 2>&1 | grep -E "AssertionError: S1|TESTS="
```

**Say:**

- "If we treat it as a bug, the clean RTL fails at 10,011 ns. A hardware fix
  would be to drive `rd_data` to zero while empty. We leave strict mode off
  for grading because the spec does not require it."

## 5. Result (20 s)

**Show:** `evidence/driver-monitor/coverage-diff.log`, then the last line of
`evidence/security/mutation.log`.

**Say:**

- "When we pulled the driver and monitor out of the test, the coverage file
  came out identical to the baseline, so the refactor changed nothing it
  should not have."
- "With the security check added, the suite still finds all 8 of 8 released
  mutants."

## Before you record

- Record from the final merged revision, not a branch. The S1 lines only
  appear once PR 4 is merged.
- Check that the numbers on screen match the ones above. If anything has
  changed, say the new numbers, not these.
- Do not leave `FIFO_TRUST_STRICT` set after part 4.
