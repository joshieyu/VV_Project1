# Kyle's independent review - November 12, 2026

PR 3: `0e691598a5564746410d039f83e145c973eabbac`.
PR 4: `04384c1eedcc85fd925c160392ccfe40f3e5c15b`.
Integration candidate: `384eb1e24e7df6b460d174d249b004d9a4295d0c`,
a local merge of those two heads on `kyle-report-review`.
This is not the final submission revision: team CRV is still missing.

## Runs

`pr4/` contains the independent run of PR 4's exact head. `fresh/` contains
a second run from a fresh local clone of the integration candidate:

```bash
git clone --no-hardlinks --branch kyle-report-review \
  /Users/kylecoutray/EEE4701/VV_Project1 \
  /Users/kylecoutray/EEE4701/tmp/project1-kyle-fresh-20261112
```

The clone had no copied simulation build products. It reused the installed
Python environment; this was source/build reproduction, not a new dependency
installation. Versions are recorded in `environment.json`.

From each checkout, with the venv activated:

```bash
PYTHONPATH=lib RANDOM_SEED=4701 python -u -m craft_mutate.mutate \
  --tb tb/fifo --pool tb/fifo/mutants_released.yaml --sim icarus \
  --gate --json <saved-output>/mutation.json
make -C tb/fifo SIM=icarus RANDOM_SEED=4701
```

Stdout/stderr were saved as `mutation.log` and `clean.log`. After mutation,
the clean run was repeated before retaining `artifacts/coverage.yml` and
`tb/fifo/results.xml`. Both runs pass one clean test at 552,631 ns and find
all eight released mutants through `test-failed`, with no build/timeout
outcomes. The two retained coverage files are byte-identical to each other
and to `evidence/security/coverage.yml` at PR 4's head.

| Cross | Each run |
|-------|---------:|
| Directed X1 | 36/36 |
| Reset X2 | 36/36 |
| HW4 random X1, separately for seeds 4701-4704 | 36/36 each |
| Trust XS1 | 4/4 |

All associated coverpoints also close. S1 reports 2,439 exposures among
7,058 sampled empty-read requests. These counts describe this sequence and
the observer's byte-value history criterion, not a universal exposure rate.

PR 4's strict check used:

```bash
FIFO_TRUST_STRICT=1 make -C tb/fifo SIM=icarus RANDOM_SEED=4701
```

`pr4/strict.log` records the expected test failure at 10,011 ns on `0xaa`.
The make process returned zero despite the cocotb failure; test summaries
and JUnit were checked instead of treating shell status as proof of a pass.
The strict run was followed by the retained clean rerun above.

## Reviews and limits

- [PR 4 review](https://github.com/joshieyu/VV_Project1/pull/4#pullrequestreview-5885378932):
  monitor/observer interface, reset/drain tracking, sequence, vplan and runs.
- [PR 3 review](https://github.com/joshieyu/VV_Project1/pull/3#pullrequestreview-5885379053):
  owned sections, evidence references, subtree history, and four-page draft
  build/visual inspection using Tectonic 0.17.0. This was not the prescribed
  latexmk/pdfLaTeX build. Security text depends on PR 4.
- No independent Eustis run, hidden pool, final team CRV regression, or
  final-submission reproduction is claimed here.
- Remote branch inspection found only `main`, `josh-driver-monitor`,
  `josh-mc-reseed`, `josh-report-skeleton`, and `josh-security-trust`.
  `crv/` contains only its README in those branches. Local/unpushed work is
  unknown. Joshua's implemented `grad/` experiment is separate.
- Overleaf initially denied project access. After access and Git
  authentication were enabled, the required subtree pull imported `75d523e`
  with no content differences. The subtree merge history was preserved.

## Kyle report draft build

Kyle's Markdown draft (commit `4e1e695`, `report/kyle.md`) was transferred
into a scratch copy of the report's owned
sections for layout review, preserving Joshua's and Jackal's content/TODOs.
The scratch source is locally retained at
`/Users/kylecoutray/EEE4701/tmp/project1-report-preview/`. This is a preview,
not a shared Overleaf edit or final submitted PDF.

After a Tectonic preview, the prescribed command was run using TinyTeX
2026.11 and latexmk 4.88 from the official rstudio/tinytex-releases package:

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error -jobname=REPORT main.tex
```

`report-preview/latexmk-build.log` records six pages. The initial pass's
unresolved references were resolved by latexmk's second pass;
`report-preview/final-tex.log` has no warnings or overfull/underfull boxes.
All six rendered pages were visually checked. Remaining TODOs are visible,
so later CRV content still needs a final page-count/layout check. Build
outputs were kept outside the repo; Joshua still owns the final REPORT.pdf.

After the Overleaf pull, the reviewed text was applied to the owned sections
in `report/latex/sections/`; the temporary Markdown draft was removed.
The same latexmk command passed on those actual report files before
commit. `report-preview/actual-latexmk-build.log` and `actual-final-tex.log`
record the build: six pages and no final-pass warnings. All six PNG renders
match the visually checked scratch preview byte-for-byte. The PDF preview
is retained outside the repo; build outputs were cleaned with latexmk -C.

The attribution clarification was rebuilt with the same latexmk command.
`report-preview/attribution-latexmk-build.log` and
`attribution-final-tex.log` record six pages with no final-pass warnings.
Rendered pages 1-4 are unchanged; the revised pages 5-6 were visually checked.
This edit clarifies project ownership, prior coursework reuse, and the scope
of assistance; it adds no new functional-validation or manual-review claim.
