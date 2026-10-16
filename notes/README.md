# Lecture notes (test)

The Quarto lecture notes, built as a website with a PDF download. One chapter per
lecture (`lNN-<topic>.qmd`); so far Lecture 1. Releasing to the ntqc repository: see
[../tools/README.md](../tools/README.md). It was moved here from the format trial in the planning
repository (`agent-sandbox/lecture-notes-format-trial/`).

## Building locally

Requirements: [Quarto](https://quarto.org) (tested with 1.10.19) and a LaTeX
installation with LuaLaTeX (for the PDF).

```sh
cd notes
quarto preview        # live preview in the browser while editing
quarto render         # full build: website + PDF into _site/
```

The figures are drawn by `make_figures.py` (Qiskit for circuits, Matplotlib for diagrams) and committed as SVG (web) and
PDF (LaTeX) files in `figures/`. Rerun it only when a figure changes.

## Files

| File | Role |
|---|---|
| `_quarto.yml` | Book structure (the published chapters), web and PDF settings |
| `_quarto-staging.yml` | Staging-only settings (`noindex`); not copied to the release |
| `_variables.yml` | Repository name and Colab base URL, used as `{{< var colab >}}`; never write the repository name directly in the text |
| `index.qmd`, `l01-platforms-and-measurement.qmd`, `exercises.qmd`, `glossary.qmd` | Content |
| `exercises.lua` | Fills the Exercises appendix with the exercises (`exr-` boxes) of every `lNN-*.qmd` chapter listed in `_quarto.yml`, with links back; exercises must not contain labelled equations or figures |
| `tutorials.lua` | Builds the tutorial table on the index page from `../tutorials/tutorial-NN/` (`*_qiskit.ipynb`, `*_qiskit_solutions.ipynb`) and the dates in `index.qmd`; it updates itself when a notebook is added |
| `_prx-widget.qmd` | Interactive Bloch sphere for PRX (raw HTML and JavaScript, web only), included in L1 |
| `changes.lua` | Temporary: colours text marked `[...]{.chg}` or `::: {.chg}` during a review round; remove it and the markers once the changes are accepted |
| `glossary.yml` | Glossary entries, **plain text only** (the web tooltips cannot render maths) |
| `glossary.lua`, `glossary-tooltips.html` | Glossary filter: write `[term]{.gloss key="..."}` in the text |
| `macros.tex` + `_macros.qmd` | LaTeX macros, once for the PDF and once for the web; keep them in step |
| `references.bib` | Bibliography |

## Deploying to GitHub Pages

The site is published to the `gh-pages` branch, which GitHub Pages serves at
<https://stefanopolla.github.io/course-testing/>.

### 1. First publish, from the laptop

```sh
cd notes
quarto publish gh-pages
```

This renders the site, creates the `gh-pages` branch, pushes it, and writes a
`_publish.yml` (commit it). It uses the local LaTeX installation for the PDF.
Before Pages is turned on (step 2), the command waits for the site to come online; once
the branch is pushed it is safe to stop it with Ctrl-C.

### 2. Turn on Pages

On GitHub: **Settings → Pages → Build and deployment → Source: Deploy from a branch**,
branch `gh-pages`, folder `/ (root)`. After a minute or two the site is live. Pages
requires a public repository on a free account.

### 3. Later updates

Either run `quarto publish gh-pages` again from the laptop, or run the workflow
**Actions → Publish notes → Run workflow**, which builds everything on GitHub, PDF
included ([../.github/workflows/publish-notes.yml](../.github/workflows/publish-notes.yml)).

### 4. Custom domain (optional)

For example `notes.stefanopolla.com`:

1. At the DNS provider of stefanopolla.com: add a `CNAME` record `notes` →
   `stefanopolla.github.io`.
2. Create `notes/CNAME` containing the single line `notes.stefanopolla.com`, and add it
   to `_quarto.yml` under `project:` as `resources: [CNAME]`. Otherwise each publish
   replaces the `gh-pages` branch and deletes the domain setting.
3. Settings → Pages → Custom domain: `notes.stefanopolla.com`. Tick **Enforce HTTPS**
   once the certificate is ready.
4. Update `site-url` in `_quarto.yml`.

If stefanopolla.com is itself already served by GitHub Pages (a `stefanopolla.github.io`
repository with that domain), this site also appears automatically at
`stefanopolla.com/course-testing/`, with no DNS change.

## Checklist for the test

- [ ] Site loads; the navigation, search and dark mode toggle work.
- [ ] Glossary tooltips appear on hover and link to the glossary page.
- [ ] Equation, figure and theorem references link correctly.
- [ ] The PDF download button gives the LaTeX PDF, with working internal links.
- [ ] The Colab link opens T1, with the AI features hidden.
- [ ] (Optional) The workflow run succeeds and the PDF built on GitHub looks the same.
- [ ] (Optional) The custom domain works over HTTPS.
