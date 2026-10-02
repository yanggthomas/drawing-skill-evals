# Codex + image generation — existing cases

Status: all nine images generated and self-reviewed. A 27-image human comparison is complete; independent automated grading has not run for this arm.

[Open the image gallery](GALLERY.md) or [read the manual scores and API-equivalent cost estimate](MANUAL-SCORES.md).

Inputs: `claude/fervent-mayer-ud3awi` at `5e6d1451c8c15bdd1a168bb6efcf988c33d397bb`. Every original prompt and vendored source was verified against its Git blob SHA; see `inputs-manifest.json`.

## Protocol

- One fresh Codex subagent per case, with no inherited conversation (`fork_turns: none`). Agents receive only their own case path and a common execution instruction.
- Inputs are the original prompt and pinned source, including licenses. No existing diagrams, answer keys, graders, reports, or other case outputs are supplied to generation agents.
- Agents independently read the source, record file-and-line grounding, and author a generation prompt. Layout is not specified by the coordinator.
- Use the built-in image-generation tool once per case, without reference images or previous-image inclusion. No Graphviz/TikZ/Pillow substitute and no best-of-N selection.
- Inspect the generated image and record issues in `qa.md`; retain the original result even if it contains mistakes. Do not silently correct a generated diagram with code.
- The requested raster-generation arm is called **Codex + image generation**: the built-in tool does not expose its underlying architecture or exact model version, so diffusion architecture is not claimed. `MANUAL-SCORES.md` gives an API-equivalent cost estimate from recorded agent tokens and published image-generation prices, with its assumptions stated explicitly.
- The original prompt frontmatter belongs to the Claude harness and is preserved as provenance; this is a separately orchestrated Codex arm, not a `claude plugin eval` run.

Isolation is at the agent-context and permitted-input level, not an OS access-control boundary: subagents share a filesystem and higher-priority runtime instructions. Prior evaluation content is excluded from their assigned inputs and conversation. This arm changes both agent and renderer, so it does not alone estimate the effect of a drawing skill.

## Case artifacts

Each `cases/<case>/` contains its unchanged `prompt.md` and `src/`, plus newly generated `generation-prompt.md`, `grounding.md`, `qa.md`, and `out/<original-output-name>.png` when successful. Failures must be recorded rather than replaced with another rendering tool. Existing evaluation results and skills remain unchanged.

## Results

| Case | Image | Generation prompt | Source evidence | Review |
|---|---|---|---|---|
| G1 vllm-v1-schedule | [PNG](cases/vllm-v1-schedule/out/schedule-step.png) | [Prompt](cases/vllm-v1-schedule/generation-prompt.md) | [Grounding](cases/vllm-v1-schedule/grounding.md) | [Self-QA](cases/vllm-v1-schedule/qa.md) |
| G2 verl-ppo-step | [PNG](cases/verl-ppo-step/out/ppo-step.png) | [Prompt](cases/verl-ppo-step/generation-prompt.md) | [Grounding](cases/verl-ppo-step/grounding.md) | [Self-QA](cases/verl-ppo-step/qa.md) |
| G3 ffmpeg-transcode-threads | [PNG](cases/ffmpeg-transcode-threads/out/transcode-threads.png) | [Prompt](cases/ffmpeg-transcode-threads/generation-prompt.md) | [Grounding](cases/ffmpeg-transcode-threads/grounding.md) | [Self-QA](cases/ffmpeg-transcode-threads/qa.md) |
| G4 redis-request-path | [PNG](cases/redis-request-path/out/request-path.png) | [Prompt](cases/redis-request-path/generation-prompt.md) | [Grounding](cases/redis-request-path/grounding.md) | [Self-QA](cases/redis-request-path/qa.md) |
| M1 megatron-tp-sp-mlp | [PNG](cases/megatron-tp-sp-mlp/out/tp-sp-mlp.png) | [Prompt](cases/megatron-tp-sp-mlp/generation-prompt.md) | [Grounding](cases/megatron-tp-sp-mlp/grounding.md) | [Self-QA](cases/megatron-tp-sp-mlp/qa.md) |
| M2 vllm-v1-mixed-batch-attn | [PNG](cases/vllm-v1-mixed-batch-attn/out/mixed-batch-attn.png) | [Prompt](cases/vllm-v1-mixed-batch-attn/generation-prompt.md) | [Grounding](cases/vllm-v1-mixed-batch-attn/grounding.md) | [Self-QA](cases/vllm-v1-mixed-batch-attn/qa.md) |
| A1 vllm-v1-process-arch | [PNG](cases/vllm-v1-process-arch/out/process-arch.png) | [Prompt](cases/vllm-v1-process-arch/generation-prompt.md) | [Grounding](cases/vllm-v1-process-arch/grounding.md) | [Self-QA](cases/vllm-v1-process-arch/qa.md) |
| A2 verl-resource-placement | [PNG](cases/verl-resource-placement/out/resource-placement.png) | [Prompt](cases/verl-resource-placement/generation-prompt.md) | [Grounding](cases/verl-resource-placement/grounding.md) | [Self-QA](cases/verl-resource-placement/qa.md) |
| A3 megatron-parallel-groups | [PNG](cases/megatron-parallel-groups/out/parallel-groups.png) | [Prompt](cases/megatron-parallel-groups/generation-prompt.md) | [Grounding](cases/megatron-parallel-groups/grounding.md) | [Self-QA](cases/megatron-parallel-groups/qa.md) |

## Checkout and validation

The requested remote branch was checked again and remained at the input commit. Normal Git HTTPS timed out; the exact signed commit, every blob and every tree were recovered through the GitHub API, hash-verified, and imported as a shallow Git branch. `git fsck --full` passed. Existing tracked evaluation files were unchanged before adding the new run to the archive index. The 68 copied prompt/source files still match their remote Git blob hashes; all nine PNGs passed chunk CRC and decompression checks. Each producing agent visually inspected its own output.

This is a separate Codex + image-generation arm, not a new score for either drawing skill. Reported semantic defects are preserved in the images and described in per-case QA. No previous generated image was supplied as a reference. The shared filesystem means the isolation is procedural and contextual, not a security sandbox.
