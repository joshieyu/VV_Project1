# Starter source

Imported from `craft-vv-student-fall2026.zip`, supplied with EEE4701.
The FIFO RTL, spec, reference model, mutation harness, and initial testbench
are unchanged packet files. The `code/` prefix was removed so `dut/`, `lib/`,
and `tb/` live at the repository root. Original licenses and version are included.

The initial commit preserves the supplied smoke test. Later commits identify
reused HW4 work and new Project 1 work separately.

Commit `7d77943` copies Kyle Coutray's existing `HW4/test_fifo.py` without
changes. Its driver, monitor, queue scoreboard, directed sequences, and Python
random campaigns predate this project. Later coverage instrumentation is new
Project 1 work. The original smoke test remains available at `17ae090`.
