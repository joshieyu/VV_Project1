# Independent FIFO review and reproduction evidence

Retained November 12, 2026 runs from Kyle's review work. Source hashes and
versions are in `environment.json`; `validation.json` records the checks on
JUnit, coverage totals and mutation outcomes. Raw simulation evidence is
unchanged from backup commit `162b51a`.

| Evidence | Tested source | Scope |
|----------|---------------|-------|
| `pr4/` | `04384c1eedcc85fd925c160392ccfe40f3e5c15b` | Exact PR 4 clean, strict and released-mutant checks |
| `fresh/` | `384eb1e24e7df6b460d174d249b004d9a4295d0c` | Fresh local clone combining PRs 3 and 4 |

The fresh clone had no copied simulation build products. It reused the
installed Python environment; it was not a fresh dependency installation.
This integration candidate predates the final team CRV implementation.

## Commands and outcomes

From the tested revision, with the project venv activated:

```bash
PYTHONPATH=lib RANDOM_SEED=4701 python -u -m craft_mutate.mutate \
  --tb tb/fifo --pool tb/fifo/mutants_released.yaml --sim icarus \
  --gate --json artifacts/mutation.json
make -C tb/fifo SIM=icarus RANDOM_SEED=4701
```

Each directory retains `mutation.log`, `mutation.json`, `clean.log`,
`results.xml`, and `coverage.yml`. Clean was rerun after mutation before
copying coverage. Both clean runs pass at 552,631 ns; both released
campaigns find 8/8 through `test-failed`, with no build or timeout outcomes.

| Cross | Each clean run |
|-------|---------------:|
| Directed X1 | 36/36 |
| Reset X2 | 36/36 |
| HW4 random X1, separately for seeds 4701-4704 | 36/36 each |
| Trust XS1 | 4/4 |

Associated coverpoints also close. The two retained YAML files are
byte-identical to each other and to `evidence/security/coverage.yml` at
PR 4's reviewed head. S1 reports 2,439 pre-reset exposures among 7,058
sampled empty-read requests. These counts describe this sequence and the
observer's value-history criterion, not a universal exposure rate.

The exact PR 4 strict check used:

```bash
FIFO_TRUST_STRICT=1 make -C tb/fifo SIM=icarus RANDOM_SEED=4701
```

`pr4/strict.log` records the expected failure at 10,011 ns on `0xaa`.
Make returned zero despite the cocotb failure, so review used the test
summary/JUnit rather than shell status alone.

## Review records and limits

- [PR 4 review](https://github.com/joshieyu/VV_Project1/pull/4#pullrequestreview-5885378932):
  raw monitor sample, observer timing, reset/drain contexts, S1 sequence,
  vplan traceability, and independent runs.
- [PR 3 review](https://github.com/joshieyu/VV_Project1/pull/3#pullrequestreview-5885379053):
  report structure, owned sections, evidence references and dependency on
  PR 4. The initial skeleton was checked with Tectonic. Current proposal
  report validation is recorded in `report/restructure-validation.md`.
- No new Eustis run, hidden-pool score, final team CRV result, or final
  submission reproduction is claimed. Joshua's `grad/` experiment is
  separate from the pending team `crv/` deliverable.
- Earlier report-preview build logs remain available in backup commit
  `162b51a`; they are omitted from this restructured proposal.
