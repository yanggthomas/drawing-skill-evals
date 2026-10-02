# Drawing Skill Evaluations

This repository contains two diagram-generation skills, source-grounded evaluation cases, immutable run evidence, and comparisons derived from those runs.

## Start here

| Area | Purpose |
|---|---|
| [`skills/`](skills/) | Installable Graphviz and model-architecture skills |
| [`evals/`](evals/) | Claude plugin eval cases, graders, answer keys, and pinned source |
| [`runs/`](runs/) | Immutable execution evidence organized by run and arm |
| [`comparisons/`](comparisons/) | Cross-run scoring, galleries, costs, and conclusions |
| [`docs/evaluation-methodology.md`](docs/evaluation-methodology.md) | Scoring and provenance rules |
| [`docs/repository-layout.md`](docs/repository-layout.md) | Archive schema and contribution workflow |

## Validate the archive

```bash
PYTHONPATH=src python3 -m drawing_eval validate --all
python3 -m unittest discover -s tests
```

The validator checks manifests, case references, artifact hashes, PNG headers, migration maps, local links, copied inputs, and machine-local paths.

## Current results

The first three-arm comparison covers nine cases and 27 images: [skill vs. no skill vs. Codex + ImageGen](comparisons/2026-10-02-three-arm/REPORT.md).

The repository is private because evaluation cases include vendored source under upstream licenses. See each case's `src/PINNED.txt` and license files.
