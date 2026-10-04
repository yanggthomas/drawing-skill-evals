# Blind Diagram Scoring Set

This orphan branch holds 54 anonymized technical diagrams (9 cases × 6 images) together with each case's prompt, reference answer key, and pinned source. It exists only to be scored blind. Image names are random tokens, and the PNGs keep only their pixel data.

Scoring instructions are in [CLAUDE.md](CLAUDE.md), and the baseline rubric is in [RUBRIC.md](RUBRIC.md). Results go under `results/`, following [scores.template.json](scores.template.json).

Vendored source under `cases/*/src/` remains under its upstream license; see each case's `src/LICENSE` and `src/PINNED.txt`.
