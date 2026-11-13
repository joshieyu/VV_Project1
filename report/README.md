# Report

`latex/` is the team report. It is a `git subtree` of the Overleaf project, so
the files live in this repo and can also be edited on Overleaf. Each section is
a file in `latex/sections/`. Red `[TODO: ...]` notes name each section's owner.

The Markdown files here are earlier drafts and demo notes. They are not part of
the Overleaf project.

## Syncing with Overleaf

One-time setup, from the repo root. Ask joshieyu to share the Overleaf project
first. Overleaf asks for a username (`git`) and a Git token from Overleaf
account settings.

```bash
git remote add overleaf https://git@git.overleaf.com/6aecb868dc5d752dcadaddd5
```

Bring Overleaf edits into the repo:

```bash
git subtree pull --prefix=report/latex overleaf main --squash
```

Send repo edits to Overleaf:

```bash
git subtree push --prefix=report/latex overleaf main
```

Pull before you push. If two people edit the same section between syncs, the
pull is an ordinary merge and may conflict. Commit and open a PR as usual after
a pull.

## Building

Overleaf builds `main.tex` with pdfLaTeX. Locally:

```bash
cd report/latex && latexmk -pdf -jobname=REPORT main.tex
```

For the submitted copy, set `\draftfalse` in `main.tex` so the TODO notes are
hidden, build, and commit the result as `REPORT.pdf` at the repo root.
