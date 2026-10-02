# Repository Layout

The repository separates reusable inputs, immutable evidence, and derived interpretation.

`evals/<case>/` is the canonical case definition consumed by `claude plugin eval`. Repository-only metadata lives in `evals/catalog.yaml` so harness schemas remain untouched.

`runs/<run-id>/run.yaml` describes one execution protocol. Generated evidence lives under `cases/<case>/arms/<arm>/`; metrics and reviews live beside the arms. `raw/` stores harness JSON and published HTML. Run archives reference canonical case inputs by Git blob hash and do not copy `evals/<case>/src/`.

`comparisons/<comparison-id>/` combines explicit run and arm references. Scores are structured in `scores.json`; `REPORT.md` and `GALLERY.md` present the analysis.

`migration-map.json` records every path changed during normalization. A moved file records its pre-migration SHA-256. Deduplicated case inputs record both their SHA-256 and canonical Git blob SHA.

Use `PYTHONPATH=src python3 -m drawing_eval validate --all` before committing archive changes.
