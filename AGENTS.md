# Instructions for coding agents

This is a graded team project (EEE5703 Project 1, FIFO verification, due
November 8, 2026). The grade depends on whether every claim can be traced to
evidence. Read `README.md` and `TASKS.md` before changing anything.

## Ground rules

- Never invent a result. Every number, pass/fail claim, or found/total in a
  doc or the report must come from a file in this repo: `evidence/`,
  `artifacts/`, `grad/results/`, `FINDINGS.md`, `closure.md`, or a command you
  ran and saved the output of. Name that file in the text. If the evidence
  does not exist yet, leave a TODO and say what run would produce it.
- Do not modify `dut/fifo.sv` or `dut/specs/fifo.md`. The suite tests the spec,
  not the RTL.
- Do not mark someone else's work as done in `CONTRIBUTIONS.md`, `TASKS.md`, or
  the review checkboxes. Each person fills in their own.
- Work on your own branch (`<name>-<topic>`) and open a PR. Do not push to
  `main`.
- Stop and ask the person you are working for before you delete evidence,
  rewrite history that is already pushed, or push anywhere.

## Running things

Setup and run commands are in `README.md`. The clean run is:

```bash
make -C tb/fifo SIM=icarus RANDOM_SEED=4701
```

Mutation runs overwrite `artifacts/`. Rerun the clean command before copying
coverage into `evidence/`. The graded runs are on Eustis (Icarus 12.0). A
`sim_build/` copied from a Mac will not run there, so use a fresh clone.

## The report

The report is LaTeX in `report/latex/`. That folder is a `git subtree` of the
team's Overleaf project, so it can be edited both here and on Overleaf.
`report/README.md` has the one-time setup and sync commands.

- Each section is a separate file in `report/latex/sections/`. Edit only the
  section(s) your person owns. Owners are in the red `\todo{...}` notes and in
  `TASKS.md`.
- Before editing, pull from Overleaf:
  `git subtree pull --prefix=report/latex overleaf main --squash`.
  After committing, push to Overleaf:
  `git subtree push --prefix=report/latex overleaf main`.
  Do not edit or squash the `Squashed 'report/latex/' ...` commits. Merge
  report PRs with a merge commit.
- Build from `report/latex` and fix every warning before you commit:
  `latexmk -pdf -interaction=nonstopmode -halt-on-error -jobname=REPORT main.tex`,
  then `latexmk -C -jobname=REPORT main.tex` to clean up. Do not commit build
  output. Only the final `REPORT.pdf` at the repo root is committed.
- The whole report must be 4 to 6 pages, so a section gets about half a page to
  a page. Use tables for numbers instead of long prose.
- Replace a `\todo{...}` when you write its content. Do not delete one you have
  not done. Cite repo files with `\path{...}` so long paths can break; use
  `\texttt{...}` for short names. Escape `_` as `\_` inside `\texttt`.
- Write like the existing environment section: plain, short sentences,
  specific numbers, and say what was not checked. No marketing words and no
  restating the same point.
- Every section must trace back to the vplan. When you describe a test, a
  coverpoint, or a survivor, name the `vplan.md` feature ID (F1, F2, ...) it
  covers.

## Recording AI use (required by the course)

The handout's "Check the Machine" rule requires every AI-drafted coverage
model, constraint block, or analysis to be logged in `ai_log.md`. Add or extend
your person's own section there:

- the tool and date, and the prompt (verbatim, may be abridged);
- what the agent drafted (file list);
- before running anything AI-drafted, a prediction of where it will be wrong;
  after running it, the evidence and the outcome, including predictions that
  turned out wrong;
- every fix made after review.

Leave the "Reviewed for functionality by ..." checkbox for the person to tick
after they have checked the work themselves. The report's AI section
(`report/latex/sections/ai.tex`) summarizes these entries.
