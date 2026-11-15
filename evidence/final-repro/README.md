# Final-revision reproduction (joshieyu, 2026-11-14)

Fresh `git clone` of `main` at `0c28a28` (PR 6 merge), run locally on macOS
with Icarus 13.0, cocotb 1.9.2, and pyvsc. Local paths in the logs are
replaced with `<clone>`, `<scratch>`, and `<venv>`.

| Command | Result | Log |
|---------|--------|-----|
| `make -C tb/fifo SIM=icarus RANDOM_SEED=4701` | 1/1 pass | `clean.log` |
| `python crv/run_regression.py --sim icarus --seeds 4701,4702,4703 --short-cycles 128 --cycles 2048 --out <scratch>/repro-crv --mutate` | X1 32/36 uniform and 34/36 tuned at 128; 36/36 for each seed at 2048; replay match; released 8/8 | `crv-regression.log`, `mutation.log` |

All six transaction CSVs match the Eustis run in `evidence/crv/` byte for
byte (`csv-compare.txt`). This is not an Eustis run.
