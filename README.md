# course-testing

Staging repository for the 2026-2027 edition of the UvA MSc course *Near-term Quantum Computing* (5394NTQC3Y).

This repository is a full mock-up of the student-facing repository `ntqc`: lecture notes (published with GitHub Pages) and tutorial notebooks (opened in Colab from GitHub). Material is developed and reviewed here, and copied to `ntqc` when it is ready; see [tools/README.md](tools/README.md). Nothing here is final, and unfinished work is expected. Nothing exam-related goes here.

## Layout

- [tutorials/](tutorials/): test copies of the tutorial notebooks (student versions), with Open-in-Colab links.
- [notes/](notes/): lecture notes built with Quarto (website + PDF), with deployment instructions for GitHub Pages.
- [.github/workflows/publish-notes.yml](.github/workflows/publish-notes.yml): manual workflow that builds and publishes the notes.
- [tools/](tools/): `release.py`, which checks the material and copies it to the release repository `ntqc` (staging only, not released).
