# Constrained-random work - pending

Proposed owner: Jackal, pending team agreement.

1. Add a pyvsc transaction with `wr_en`, `rd_en`, and `wr_data`.
2. Keep a non-random reference occupancy/phase field when shaping requests.
3. Include bursty fill/drain traffic and simultaneous requests. Do not prohibit
   full writes or empty reads: the spec defines their blocked behavior.
4. Reuse the driver/monitor/scoreboard interface agreed in `TASKS.md`.
5. Use `make_sampler("fifo.crv_seed_<seed>")` from `lib/fifo_coverage.py` and
   sample reference occupancy before the edge with the requested enables.
6. Record seeds, cycle budgets, generated transactions, observed distributions,
   and coverage. Replay a seed and compare transactions before claiming replay.
7. Save the first coverage report before tuning constraints, then record each
   hole and the change that closed it. The complete random regression must
   close all 36 occupancy x request bins without directed-test credit.

The packet pins `pyvsc==0.9.5.27214109393`. Install that in the active
environment when implementing this layer:

```bash
python -m pip install pyvsc==0.9.5.27214109393
```

The packet's Week 5 constraint demo documents a `vsc.dist`/`vsc.implies` issue
in that version. Measure actual rates and verify seed control; do not rely
only on the intended weights or Python's `random.seed` call.

No constrained-random implementation or pyvsc validation is claimed yet.
