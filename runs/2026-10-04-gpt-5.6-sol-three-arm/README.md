# 2026-10-04 gpt-5.6-sol Three-Arm Run

This archive contains one Codex `gpt-5.6-sol` run (reasoning effort high) per arm for the nine cases: with the drawing skills (`with`), without them (`without`), and with image generation (`imagegen`). Claude orchestrated the runs; each case × arm was an isolated `codex exec` session whose only prompt was the case requirement, plus the single sentence "Produce the diagram with image generation." for the imagegen arm. There was no automated judge in the run; the images were reviewed later, blind, together with the Oct 1 images.

The machine-readable source of truth is [run.yaml](run.yaml). Final artifacts (the PNG and any editable source the agent left) are under `cases/<case>/arms/<arm>/out/`. Per-arm process evidence (audit, JSONL trace, stderr, prompt input, last message as `.txt`, image-tool files and archived attempts) is under `raw/<case>/<arm>/`; [raw/migration-map.json](raw/migration-map.json) records the move from the arm directories. The runner is [scripts/run-codex-arm.mjs](../../scripts/run-codex-arm.mjs).

## Protocol

- Isolation: `codex exec --json --ephemeral --ignore-user-config --ignore-rules --skip-git-repo-check --strict-config --sandbox workspace-write`, with `HOME` and `CODEX_HOME` pointing to a fresh temporary directory. Bundled skills, plugins and apps were disabled; the image-generation tool was disabled except in the imagegen arm. Case source was copied read-only.
- Skill arms: the `with` arm saw only the drawing skills; the `without` arm saw none. Skill reads and renderer commands are recorded in each audit.
- ImageGen detection: the image tool emits no event in `exec --json`, so a run counts as image-generated only when the output PNG's SHA-256 matches a file the tool wrote. Five imagegen audits were reconstructed after their temporary directories disappeared and carry an `audit_recovery` note. M2 (`vllm-v1-mixed-batch-attn`) was re-run after a usage limit; the earlier attempts are under `raw/vllm-v1-mixed-batch-attn/<arm>/attempts/`.
- Cost: official API rates, $4 input / $0.40 cached / $20 output per 1M tokens. Image output is charged at $30 per 1M tokens, with the token count from the GPT Image 2 formula at high quality.

| Arm | Cost (9 cases) |
|---|---:|
| with skills | $12.25 |
| without skills | $8.74 |
| imagegen | $8.82 (agent $6.74 + 15 image calls $2.08) |

## Results

The 27 images were scored blind together with the 27 Oct 1 images. Human comments, Fable 5.1 scores and the reconciled results are in [comparisons/2026-10-04-blind-54](../../comparisons/2026-10-04-blind-54/REPORT.md).
