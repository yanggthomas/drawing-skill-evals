# 54 图画廊

按 case 排列，每个 case 6 张：10 月 1 日（Claude Opus skill / no-skill，gpt-6-astra ImageGen）和 10 月 4 日（gpt-5.6-sol 三个 arm）。分数是 Fable 技术分 /30 和校正后的技术分；评语原文和方面编码见 [REPORT.md](REPORT.md) 附录和 [human-review.md](human-review.md)。

## G1 · vLLM schedule

### `1eba22c4` · 10 月 1 日 · claude-opus · skill

Fable 技术分 25 / 30 · 校正后 25 · 实质性错误 0

![G1 1eba22c4](../../runs/2026-10-01-skill-v0.1.0/cases/vllm-v1-schedule/arms/with/schedule-step.png)

### `6e033b2b` · 10 月 1 日 · claude-opus · no_skill

Fable 技术分 25 / 30 · 校正后 25 · 实质性错误 0

![G1 6e033b2b](../../runs/2026-10-01-skill-v0.1.0/cases/vllm-v1-schedule/arms/without/schedule-step.png)

### `599e7123` · 10 月 1 日 · gpt-6-astra · imagegen

Fable 技术分 27 / 30 · 校正后 27 · 实质性错误 0

![G1 599e7123](../../runs/2026-10-01-codex-imagegen-v1/cases/vllm-v1-schedule/arms/imagegen/schedule-step.png)

### `db0db3ff` · 10 月 4 日 · gpt-5.6-sol · skill

Fable 技术分 24 / 30 · 校正后 24 · 实质性错误 0

![G1 db0db3ff](../../runs/2026-10-04-gpt-5.6-sol-three-arm/cases/vllm-v1-schedule/arms/with/out/schedule-step.png)

### `3f2ea037` · 10 月 4 日 · gpt-5.6-sol · no_skill

Fable 技术分 29 / 30 · 校正后 29 · 实质性错误 0

![G1 3f2ea037](../../runs/2026-10-04-gpt-5.6-sol-three-arm/cases/vllm-v1-schedule/arms/without/out/schedule-step.png)

### `28f89ba6` · 10 月 4 日 · gpt-5.6-sol · imagegen

Fable 技术分 27 / 30 · 校正后 25 · 实质性错误 0

![G1 28f89ba6](../../runs/2026-10-04-gpt-5.6-sol-three-arm/cases/vllm-v1-schedule/arms/imagegen/out/schedule-step.png)

## G2 · verl PPO step

### `d46ecf7c` · 10 月 1 日 · claude-opus · skill

Fable 技术分 25 / 30 · 校正后 21 · 实质性错误 0

![G2 d46ecf7c](../../runs/2026-10-01-skill-v0.1.0/cases/verl-ppo-step/arms/with/ppo-step.png)

### `b22ede75` · 10 月 1 日 · claude-opus · no_skill

Fable 技术分 29 / 30 · 校正后 29 · 实质性错误 0

![G2 b22ede75](../../runs/2026-10-01-skill-v0.1.0/cases/verl-ppo-step/arms/without/ppo-step.png)

### `f5a313af` · 10 月 1 日 · gpt-6-astra · imagegen

Fable 技术分 29 / 30 · 校正后 27 · 实质性错误 0

![G2 f5a313af](../../runs/2026-10-01-codex-imagegen-v1/cases/verl-ppo-step/arms/imagegen/ppo-step.png)

### `e125d79e` · 10 月 4 日 · gpt-5.6-sol · skill

Fable 技术分 26 / 30 · 校正后 26 · 实质性错误 0

![G2 e125d79e](../../runs/2026-10-04-gpt-5.6-sol-three-arm/cases/verl-ppo-step/arms/with/out/ppo-step.png)

### `c320d4b7` · 10 月 4 日 · gpt-5.6-sol · no_skill

Fable 技术分 29 / 30 · 校正后 27 · 实质性错误 0

![G2 c320d4b7](../../runs/2026-10-04-gpt-5.6-sol-three-arm/cases/verl-ppo-step/arms/without/out/ppo-step.png)

### `43118728` · 10 月 4 日 · gpt-5.6-sol · imagegen

Fable 技术分 29 / 30 · 校正后 29 · 实质性错误 0

![G2 43118728](../../runs/2026-10-04-gpt-5.6-sol-three-arm/cases/verl-ppo-step/arms/imagegen/out/ppo-step.png)

## G3 · ffmpeg transcode threads

### `d2237ccb` · 10 月 1 日 · claude-opus · skill

Fable 技术分 25 / 30 · 校正后 25 · 实质性错误 0

![G3 d2237ccb](../../runs/2026-10-01-skill-v0.1.0/cases/ffmpeg-transcode-threads/arms/with/transcode-threads.png)

### `1bdb9dba` · 10 月 1 日 · claude-opus · no_skill

Fable 技术分 26 / 30 · 校正后 26 · 实质性错误 0

![G3 1bdb9dba](../../runs/2026-10-01-skill-v0.1.0/cases/ffmpeg-transcode-threads/arms/without/transcode-threads.png)

### `77c4b51b` · 10 月 1 日 · gpt-6-astra · imagegen

Fable 技术分 27 / 30 · 校正后 25 · 实质性错误 0

![G3 77c4b51b](../../runs/2026-10-01-codex-imagegen-v1/cases/ffmpeg-transcode-threads/arms/imagegen/transcode-threads.png)

### `8c4c4637` · 10 月 4 日 · gpt-5.6-sol · skill

Fable 技术分 26 / 30 · 校正后 26 · 实质性错误 0

![G3 8c4c4637](../../runs/2026-10-04-gpt-5.6-sol-three-arm/cases/ffmpeg-transcode-threads/arms/with/out/transcode-threads.png)

### `d8edd397` · 10 月 4 日 · gpt-5.6-sol · no_skill

Fable 技术分 24 / 30 · 校正后 24 · 实质性错误 0

![G3 d8edd397](../../runs/2026-10-04-gpt-5.6-sol-three-arm/cases/ffmpeg-transcode-threads/arms/without/out/transcode-threads.png)

### `d9dc767f` · 10 月 4 日 · gpt-5.6-sol · imagegen

Fable 技术分 29 / 30 · 校正后 27 · 实质性错误 0

![G3 d9dc767f](../../runs/2026-10-04-gpt-5.6-sol-three-arm/cases/ffmpeg-transcode-threads/arms/imagegen/out/transcode-threads.png)

## G4 · Redis request path

### `8555a918` · 10 月 1 日 · claude-opus · skill

Fable 技术分 26 / 30 · 校正后 26 · 实质性错误 0

![G4 8555a918](../../runs/2026-10-01-skill-v0.1.0/cases/redis-request-path/arms/with/request-path.png)

### `02d4d074` · 10 月 1 日 · claude-opus · no_skill

Fable 技术分 28 / 30 · 校正后 28 · 实质性错误 0

![G4 02d4d074](../../runs/2026-10-01-skill-v0.1.0/cases/redis-request-path/arms/without/request-path.png)

### `b638523b` · 10 月 1 日 · gpt-6-astra · imagegen

Fable 技术分 29 / 30 · 校正后 27 · 实质性错误 0

![G4 b638523b](../../runs/2026-10-01-codex-imagegen-v1/cases/redis-request-path/arms/imagegen/request-path.png)

### `7d98c63e` · 10 月 4 日 · gpt-5.6-sol · skill

Fable 技术分 27 / 30 · 校正后 27 · 实质性错误 0

![G4 7d98c63e](../../runs/2026-10-04-gpt-5.6-sol-three-arm/cases/redis-request-path/arms/with/out/request-path.png)

### `a99b55ec` · 10 月 4 日 · gpt-5.6-sol · no_skill

Fable 技术分 28 / 30 · 校正后 28 · 实质性错误 0

![G4 a99b55ec](../../runs/2026-10-04-gpt-5.6-sol-three-arm/cases/redis-request-path/arms/without/out/request-path.png)

### `7bd02c74` · 10 月 4 日 · gpt-5.6-sol · imagegen

Fable 技术分 29 / 30 · 校正后 27 · 实质性错误 0

![G4 7bd02c74](../../runs/2026-10-04-gpt-5.6-sol-three-arm/cases/redis-request-path/arms/imagegen/out/request-path.png)

## M1 · Megatron TP+SP MLP

### `e0edfc5a` · 10 月 1 日 · claude-opus · skill

Fable 技术分 29 / 30 · 校正后 29 · 实质性错误 0

![M1 e0edfc5a](../../runs/2026-10-01-skill-v0.1.0/cases/megatron-tp-sp-mlp/arms/with/tp-sp-mlp.png)

### `04eed4f3` · 10 月 1 日 · claude-opus · no_skill

Fable 技术分 27 / 30 · 校正后 23 · 实质性错误 0

![M1 04eed4f3](../../runs/2026-10-01-skill-v0.1.0/cases/megatron-tp-sp-mlp/arms/without/tp-sp-mlp.png)

### `1a297a07` · 10 月 1 日 · gpt-6-astra · imagegen

Fable 技术分 29 / 30 · 校正后 29 · 实质性错误 0

![M1 1a297a07](../../runs/2026-10-01-codex-imagegen-v1/cases/megatron-tp-sp-mlp/arms/imagegen/tp-sp-mlp.png)

### `54a5fbd7` · 10 月 4 日 · gpt-5.6-sol · skill

Fable 技术分 27 / 30 · 校正后 27 · 实质性错误 0

![M1 54a5fbd7](../../runs/2026-10-04-gpt-5.6-sol-three-arm/cases/megatron-tp-sp-mlp/arms/with/out/tp-sp-mlp.png)

### `4a7c14b4` · 10 月 4 日 · gpt-5.6-sol · no_skill

Fable 技术分 29 / 30 · 校正后 27 · 实质性错误 0

![M1 4a7c14b4](../../runs/2026-10-04-gpt-5.6-sol-three-arm/cases/megatron-tp-sp-mlp/arms/without/out/tp-sp-mlp.png)

### `c87e8342` · 10 月 4 日 · gpt-5.6-sol · imagegen

Fable 技术分 24 / 30 · 校正后 22 · 实质性错误 1

![M1 c87e8342](../../runs/2026-10-04-gpt-5.6-sol-three-arm/cases/megatron-tp-sp-mlp/arms/imagegen/out/tp-sp-mlp.png)

## M2 · vLLM mixed-batch attention

### `6fe5779e` · 10 月 1 日 · claude-opus · skill

Fable 技术分 27 / 30 · 校正后 28 · 实质性错误 0

![M2 6fe5779e](../../runs/2026-10-01-skill-v0.1.0/cases/vllm-v1-mixed-batch-attn/arms/with/mixed-batch-attn.png)

### `61583ee3` · 10 月 1 日 · claude-opus · no_skill

Fable 技术分 29 / 30 · 校正后 29 · 实质性错误 0

![M2 61583ee3](../../runs/2026-10-01-skill-v0.1.0/cases/vllm-v1-mixed-batch-attn/arms/without/mixed-batch-attn.png)

### `a58a7a4d` · 10 月 1 日 · gpt-6-astra · imagegen

Fable 技术分 30 / 30 · 校正后 26 · 实质性错误 0

![M2 a58a7a4d](../../runs/2026-10-01-codex-imagegen-v1/cases/vllm-v1-mixed-batch-attn/arms/imagegen/mixed-batch-attn.png)

### `8ff5963f` · 10 月 4 日 · gpt-5.6-sol · skill

Fable 技术分 26 / 30 · 校正后 26 · 实质性错误 0

![M2 8ff5963f](../../runs/2026-10-04-gpt-5.6-sol-three-arm/cases/vllm-v1-mixed-batch-attn/arms/with/out/mixed-batch-attn.png)

### `85ac7bde` · 10 月 4 日 · gpt-5.6-sol · no_skill

Fable 技术分 29 / 30 · 校正后 27 · 实质性错误 0

![M2 85ac7bde](../../runs/2026-10-04-gpt-5.6-sol-three-arm/cases/vllm-v1-mixed-batch-attn/arms/without/out/mixed-batch-attn.png)

### `b9950cf1` · 10 月 4 日 · gpt-5.6-sol · imagegen

Fable 技术分 29 / 30 · 校正后 25 · 实质性错误 0

![M2 b9950cf1](../../runs/2026-10-04-gpt-5.6-sol-three-arm/cases/vllm-v1-mixed-batch-attn/arms/imagegen/out/mixed-batch-attn.png)

## A1 · vLLM process architecture

### `fd86cbc4` · 10 月 1 日 · claude-opus · skill

Fable 技术分 24 / 30 · 校正后 24 · 实质性错误 0

![A1 fd86cbc4](../../runs/2026-10-01-skill-v0.1.0/cases/vllm-v1-process-arch/arms/with/process-arch.png)

### `9c82de56` · 10 月 1 日 · claude-opus · no_skill

Fable 技术分 27 / 30 · 校正后 27 · 实质性错误 0

![A1 9c82de56](../../runs/2026-10-01-skill-v0.1.0/cases/vllm-v1-process-arch/arms/without/process-arch.png)

### `bba2c896` · 10 月 1 日 · gpt-6-astra · imagegen

Fable 技术分 27 / 30 · 校正后 27 · 实质性错误 0

![A1 bba2c896](../../runs/2026-10-01-codex-imagegen-v1/cases/vllm-v1-process-arch/arms/imagegen/process-arch.png)

### `44dce42a` · 10 月 4 日 · gpt-5.6-sol · skill

Fable 技术分 25 / 30 · 校正后 25 · 实质性错误 0

![A1 44dce42a](../../runs/2026-10-04-gpt-5.6-sol-three-arm/cases/vllm-v1-process-arch/arms/with/out/process-arch.png)

### `2e3e34c4` · 10 月 4 日 · gpt-5.6-sol · no_skill

Fable 技术分 29 / 30 · 校正后 27 · 实质性错误 0

![A1 2e3e34c4](../../runs/2026-10-04-gpt-5.6-sol-three-arm/cases/vllm-v1-process-arch/arms/without/out/process-arch.png)

### `0feeb41d` · 10 月 4 日 · gpt-5.6-sol · imagegen

Fable 技术分 25 / 30 · 校正后 25 · 实质性错误 0

![A1 0feeb41d](../../runs/2026-10-04-gpt-5.6-sol-three-arm/cases/vllm-v1-process-arch/arms/imagegen/out/process-arch.png)

## A2 · verl resource placement

### `208d31f6` · 10 月 1 日 · claude-opus · skill

Fable 技术分 24 / 30 · 校正后 24 · 实质性错误 0

![A2 208d31f6](../../runs/2026-10-01-skill-v0.1.0/cases/verl-resource-placement/arms/with/resource-placement.png)

### `6eed9fef` · 10 月 1 日 · claude-opus · no_skill

Fable 技术分 26 / 30 · 校正后 26 · 实质性错误 0

![A2 6eed9fef](../../runs/2026-10-01-skill-v0.1.0/cases/verl-resource-placement/arms/without/resource-placement.png)

### `cbd1fa32` · 10 月 1 日 · gpt-6-astra · imagegen

Fable 技术分 19 / 30 · 校正后 19 · 实质性错误 2

![A2 cbd1fa32](../../runs/2026-10-01-codex-imagegen-v1/cases/verl-resource-placement/arms/imagegen/resource-placement.png)

### `49f8027c` · 10 月 4 日 · gpt-5.6-sol · skill

Fable 技术分 26 / 30 · 校正后 26 · 实质性错误 0

![A2 49f8027c](../../runs/2026-10-04-gpt-5.6-sol-three-arm/cases/verl-resource-placement/arms/with/out/resource-placement.png)

### `3223b16a` · 10 月 4 日 · gpt-5.6-sol · no_skill

Fable 技术分 25 / 30 · 校正后 25 · 实质性错误 0

![A2 3223b16a](../../runs/2026-10-04-gpt-5.6-sol-three-arm/cases/verl-resource-placement/arms/without/out/resource-placement.png)

### `89ec0612` · 10 月 4 日 · gpt-5.6-sol · imagegen

Fable 技术分 27 / 30 · 校正后 27 · 实质性错误 0

![A2 89ec0612](../../runs/2026-10-04-gpt-5.6-sol-three-arm/cases/verl-resource-placement/arms/imagegen/out/resource-placement.png)

## A3 · Megatron parallel groups

### `1daf798b` · 10 月 1 日 · claude-opus · skill

Fable 技术分 28 / 30 · 校正后 28 · 实质性错误 0

![A3 1daf798b](../../runs/2026-10-01-skill-v0.1.0/cases/megatron-parallel-groups/arms/with/parallel-groups.png)

### `cca705dc` · 10 月 1 日 · claude-opus · no_skill

Fable 技术分 29 / 30 · 校正后 27 · 实质性错误 0

![A3 cca705dc](../../runs/2026-10-01-skill-v0.1.0/cases/megatron-parallel-groups/arms/without/parallel-groups.png)

### `73c5e8d6` · 10 月 1 日 · gpt-6-astra · imagegen

Fable 技术分 27 / 30 · 校正后 27 · 实质性错误 0

![A3 73c5e8d6](../../runs/2026-10-01-codex-imagegen-v1/cases/megatron-parallel-groups/arms/imagegen/parallel-groups.png)

### `c8fcd33b` · 10 月 4 日 · gpt-5.6-sol · skill

Fable 技术分 27 / 30 · 校正后 27 · 实质性错误 0

![A3 c8fcd33b](../../runs/2026-10-04-gpt-5.6-sol-three-arm/cases/megatron-parallel-groups/arms/with/out/parallel-groups.png)

### `cabeeecb` · 10 月 4 日 · gpt-5.6-sol · no_skill

Fable 技术分 29 / 30 · 校正后 27 · 实质性错误 0

![A3 cabeeecb](../../runs/2026-10-04-gpt-5.6-sol-three-arm/cases/megatron-parallel-groups/arms/without/out/parallel-groups.png)

### `a00afc4a` · 10 月 4 日 · gpt-5.6-sol · imagegen

Fable 技术分 28 / 30 · 校正后 28 · 实质性错误 0

![A3 a00afc4a](../../runs/2026-10-04-gpt-5.6-sol-three-arm/cases/megatron-parallel-groups/arms/imagegen/out/parallel-groups.png)
