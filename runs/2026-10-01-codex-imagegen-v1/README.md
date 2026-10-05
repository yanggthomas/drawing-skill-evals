# 2026-10-01 Codex + ImageGen Run

Nine existing cases were run once each. Every case used a fresh Codex subagent with no inherited conversation, one image-generation call, no reference images, and no best-of-N selection.

The machine-readable source of truth is [run.yaml](run.yaml). Canonical prompts and pinned source remain under [`evals/`](../../evals/); [raw/inputs-manifest.json](raw/inputs-manifest.json) records the 68 verified Git blobs used by this run. The migration removed duplicated input copies after verifying each one against its canonical blob.

Each `cases/<case>/arms/imagegen/` directory contains the generated PNG, generation prompt, source grounding, and self-QA. The original images are retained even when QA found a semantic error.

The independent cross-arm review, scores, cost estimate, and gallery live in [comparisons/2026-10-02-three-arm](../../comparisons/2026-10-02-three-arm/REPORT.md).

The built-in image tool did not expose its architecture, exact model version, or output quality tier. `run.yaml` therefore labels the image model as unknown and records API cost as an estimate range.

The blind 54-image review, which re-scores these images together with the Oct 4 `gpt-5.6-sol` run, is [comparisons/2026-10-04-blind-54](../../comparisons/2026-10-04-blind-54/REPORT.md).
