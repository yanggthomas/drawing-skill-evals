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

The latest result is a blind review of 54 images: two runs of the nine cases × three arms (Oct 1 Claude Opus / gpt-6-astra, Oct 4 gpt-5.6-sol), scored by the reviewer and by Fable 5.1: [comparisons/2026-10-04-blind-54](comparisons/2026-10-04-blind-54/REPORT.md) (in Chinese). The earlier 27-image comparison is [2026-10-02-three-arm](comparisons/2026-10-02-three-arm/REPORT.md).

The plan for the next round (skill improvements, the seven-case benchmark v2 and its goldens) is [docs/benchmark-v2](docs/benchmark-v2/README.md).

The repository is private because evaluation cases include vendored source under upstream licenses. See each case's `src/PINNED.txt` and license files.
