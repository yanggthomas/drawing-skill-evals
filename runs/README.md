# Evaluation Runs

Each directory is immutable evidence from one execution protocol. Case definitions remain canonical under `evals/`; cross-run conclusions live under `comparisons/`.

| Run | Protocol | Arms | Evidence |
|---|---|---|---|
| [2026-10-01-skill-v0.1.0](2026-10-01-skill-v0.1.0/README.md) | Claude plugin eval | with skill, without skill | Nine final cases plus labeled smoke attempts |
| [2026-10-01-codex-imagegen-v1](2026-10-01-codex-imagegen-v1/README.md) | Isolated Codex + ImageGen | imagegen | Nine one-shot generated images and self-QA |

The combined 27-image evaluation is [2026-10-02-three-arm](../comparisons/2026-10-02-three-arm/REPORT.md).
