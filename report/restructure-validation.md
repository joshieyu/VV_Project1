# Kyle's local replacement validation

Validated November 12, 2026 (America/Chicago; November 13 UTC).

This replacement starts at the existing report/security integration
`384eb1e24e7df6b460d174d249b004d9a4295d0c`. It preserves teammates' commits
and separates Kyle's additions into coverage-model validation, review evidence,
and report/contribution documentation. The source backup is local branch
`kyle-report-backup-20261112-162b51a` at `162b51a`.

Retained simulation evidence matches the backup byte-for-byte. Superseded PDF
build logs remain in that backup. The original model-check prediction wording
remains at `ed2b5cc`; a later attribution correction records Kyle as its author.

## Checks on the replacement

Using the existing project Python environment and Icarus 13.0:

```sh
make -C tb/fifo SIM=icarus RANDOM_SEED=4701 MODULE=test_coverage_probe
make -C tb/fifo SIM=icarus RANDOM_SEED=4701
cd report/latex
latexmk -pdf -interaction=nonstopmode -halt-on-error -jobname=REPORT main.tex
```

| Check | Result |
|---|---|
| Opt-in probe | One JUnit test, zero failures; compact 12/12, exact sparse 12/36, exact full matrix 36/36 |
| Default suite | One JUnit test, zero failures; coverage byte-identical to `evidence/security/coverage.yml` |
| Retained simulation records | Compared with the backup; all retained raw files identical |
| Report build | Six pages; no final-pass warnings or overfull/underfull boxes |
| PDF inspection | All six rendered pages inspected; tables, text and page numbers readable without clipping |

Logs, JUnit results, probe counts and validation hashes are in
`evidence/kyle-restructure/`. Shell exit status alone was not used to judge
simulation success. The retained 8/8 mutation result is the earlier integration
run; the mutation campaign was not rerun during this documentation restructure.

## Remaining work

- Jackal's team `crv/` implementation and final regression are still pending.
  Baseline and graduate-extension results do not replace them.
- Final coverage convergence, final-suite mutation analysis, demo and each
  member's fresh-clone reproduction depend on the completed team revision.
- Kyle confirmed his functionality review; his `ai_log.md` checkbox is checked.
  The team agreement checkbox remains unchecked.
- The inherited title says EEE5703; confirm the shared title with Joshua before
  final submission if the mixed EEE4701/EEE5703 team should use both course IDs.

This is a local review candidate. It does not publish PR changes or sync shared
Overleaf content.
