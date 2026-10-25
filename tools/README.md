# Tools (staging only)

`release.py` checks the course material and copies it from this staging repository
(`course-testing`) to the release repository (`ntqc`). Settings are in `release.toml`.
This directory is not copied to the release.

## How the two repositories relate

- **course-testing** (this repository) is the staging area and a full mock-up of the
  release. Unfinished notes and tutorials can live here. Its site is shared only for
  review, and it carries a `noindex` tag (`notes/_quarto-staging.yml`).
- **ntqc** is the student-facing release. It receives clean snapshots, never this
  repository's history, so this repository can later be made private or deleted.
- The two are independent. Some drift is fine, for example a test change on a lecture
  that is already published; `diff` shows it.
- **Never in either repository:** anything exam-related (written test, SDK test,
  answer keys). Tutorial solutions are fine. `check` and `copy` refuse exam-like paths.

## Commands

Run from the repository root with any Python 3.11 or newer:

```sh
python3 tools/release.py check                      # this repository (TODOs are warnings)
python3 tools/release.py diff ../ntqc               # drift: what differs, file by file
python3 tools/release.py diff ../ntqc --show notes/L2-noise.qmd
python3 tools/release.py copy ../ntqc notes/L2-noise.qmd notes/figures --dry-run
python3 tools/release.py copy ../ntqc notes/L2-noise.qmd notes/figures
python3 tools/release.py check ../ntqc --release    # release rules: errors, not warnings
```

`copy` rewrites the repository name (`StefanoPolla/course-testing` →
`StefanoPolla/ntqc`, also in the Pages URL) and writes files only. It never commits.

What `check` covers:

- exam-related file names;
- the LaTeX macros in `notes/macros.tex` and `notes/_macros.qmd` are identical;
- every glossary key used in the text exists, and no definition contains maths;
- chapters listed in `notes/_quarto.yml` exist and contain no `TODO`;
- with `--release`: no "course-testing" left anywhere.

## Releasing a lecture

1. In course-testing: finish the chapter, then `check` (no errors). Accept any pending
   review highlights (`.chg`) first. **References to chapters that are not released**
   become plain text ("the next chapter"), with the original kept in a comment
   (`<!-- L2-LINK: @sec-... -->`), here in staging too (Stefano, 2026-10-25: always).
   Restore them when that chapter is released.
2. `copy` the chapter and its figures into a local clone of ntqc (add new glossary
   entries, bibliography entries or macros too: copy those files).
3. In ntqc: add the chapter to `notes/_quarto.yml` by hand. That file is copied only
   when named, so each repository controls which chapters it publishes. (First
   release: copy it once by name, then trim the chapter list.)
4. `check ../ntqc --release`, then build and look at it (`quarto preview` in
   `ntqc/notes`).
5. Commit in ntqc with a release message (e.g. "Release lecture 2 notes") and publish
   (`quarto publish gh-pages`).

Also at each release, in ntqc:

- **Glossary**: `notes/glossary.yml` holds only the terms used in the released pages
  (Stefano, 2026-10-25: no terms of later lectures). Copy the staging file, then trim it
  to the `.gloss key="..."` values found in `notes/*.qmd`.
- **PDF date**: `book: date` in `notes/_quarto.yml` is the release date.
- **Build after committing**: the page dates (`page-dates.lua`) come from git.

First release (L1, 2026-10-25), for reference: `_quarto.yml` was copied once and trimmed
to the released chapters, without `changes.lua` and the staging profile; ntqc has its
own `noindex` tag in `_quarto.yml` until Stefano decides otherwise (probably after the
course). Quarto needs a `gh-pages` branch on the remote before the first publish
(an empty commit pushed as `refs/heads/gh-pages`), and GitHub Pages must be switched on
once (Settings, Pages, deploy from the `gh-pages` branch, root). The repository name is
lowercase: Pages paths are case-sensitive.
