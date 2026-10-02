# 2026-10-01 Drawing Skills A/B Run

This archive contains one Claude Opus run per arm for nine cases: with drawing-skills 0.1.0 and without the plugin. Claude Opus also judged both arms.

The machine-readable source of truth is [run.yaml](run.yaml). Final artifacts are stored under `cases/<case>/arms/{with,without}/`; run metrics and reviews are stored beside them. Harness JSON and published HTML are preserved under `raw/`. Smoke attempts remain archived and are labeled as historical attempts in the manifest.

The original evaluation design does not isolate the claimed value of each skill. Read [reviews/LIMITATIONS.md](reviews/LIMITATIONS.md) before interpreting the automated scores. The complete two-arm report is [REPORT.md](REPORT.md).

The later 27-image comparison with Codex + ImageGen is a separate derived artifact under [comparisons/2026-10-02-three-arm](../../comparisons/2026-10-02-three-arm/REPORT.md).
