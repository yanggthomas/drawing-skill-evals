# Blind Diagram Review

Nine cases, six anonymized diagrams each. Image names are random tokens. Write your comments under each image; a case-level note slot follows each case.

## G1-vllm-v1-schedule

> I'm trying to understand how vLLM V1 does continuous batching. The scheduler source, pinned at the commit in `PINNED.txt`, is in the read-only source directory available to this session. Draw one diagram that explains what happens in a single scheduler step: how the per-step token budget is shared between already-running requests and waiting requests, how chunked prefill splits a long prompt across steps, where KV cache blocks are allocated, when and how preemption happens, and what the step outputs to the model runner. Ground every element in the code. Save the finished diagram as a PNG image at `out/schedule-step.png`.

Reference: [answer key](../../evals/vllm-v1-schedule/answer-key.md) · [source](../../evals/vllm-v1-schedule/src/)

### G1 · 1eba22c4

![G1 1eba22c4](../../runs/2026-10-01-skill-v0.1.0/cases/vllm-v1-schedule/arms/with/schedule-step.png)

**Comment:**  generally ok, just to many works in each box. 整体几个阶段是比较清楚，kv-cache池也有表达。

### G1 · 28f89ba6

![G1 28f89ba6](../../runs/2026-10-04-gpt-5.6-sol-three-arm/cases/vllm-v1-schedule/arms/imagegen/out/schedule-step.png)

**Comment:** 这一幅比上一幅更清楚，但颜色比较鲜艳，而且左下角绿色的kv-block pool好像不太对应。

### G1 · 3f2ea037

![G1 3f2ea037](../../runs/2026-10-04-gpt-5.6-sol-three-arm/cases/vllm-v1-schedule/arms/without/out/schedule-step.png)

**Comment:**  这一幅配色很清晰，也很素雅，但是箭头太大了。

### G1 · 599e7123

![G1 599e7123](../../runs/2026-10-01-codex-imagegen-v1/cases/vllm-v1-schedule/arms/imagegen/schedule-step.png)

**Comment:** 应该说这一幅除了配色是最好的，内容也很清楚。只是整体有点卡通风。

### G1 · 6e033b2b

![G1 6e033b2b](../../runs/2026-10-01-skill-v0.1.0/cases/vllm-v1-schedule/arms/without/schedule-step.png)

**Comment:** 这一幅也是内容太多了，配色一般吧，进一步加剧杂乱。

### G1 · db0db3ff

![G1 db0db3ff](../../runs/2026-10-04-gpt-5.6-sol-three-arm/cases/vllm-v1-schedule/arms/with/out/schedule-step.png)

**Comment:** 应该说这个是排版最遭的一个，内容也还ok，但是横竖混排确实不太清楚。

### G1 · case notes

**Comment:** 

---

## G2-verl-ppo-step

> I'm trying to understand how verl runs one PPO/GRPO training step with its single-controller design. The trainer source, pinned at the commit in `PINNED.txt`, is in the read-only source directory available to this session. Draw one diagram that explains what one step of the training loop does: the order of rollout, reward, old and reference log-probs, values, advantage, critic and actor updates; which work runs on the driver and which on Ray worker groups; what accumulates in the batch along the way; and where the weights move between the trainer and the rollout engine. Ground every element in the code. Save the finished diagram as a PNG image at `out/ppo-step.png`.

Reference: [answer key](../../evals/verl-ppo-step/answer-key.md) · [source](../../evals/verl-ppo-step/src/)

### G2 · 43118728

![G2 43118728](../../runs/2026-10-04-gpt-5.6-sol-three-arm/cases/verl-ppo-step/arms/imagegen/out/ppo-step.png)

**Comment:** this brings the question, is A,B,C dataproto perfectly in between 1-2, 2-3 and others.

### G2 · b22ede75

![G2 b22ede75](../../runs/2026-10-01-skill-v0.1.0/cases/verl-ppo-step/arms/without/ppo-step.png)

**Comment:** I like this 时序图-like scheme best. This would be best in this case.

### G2 · c320d4b7

![G2 c320d4b7](../../runs/2026-10-04-gpt-5.6-sol-three-arm/cases/verl-ppo-step/arms/without/out/ppo-step.png)

**Comment:** don’t lie the dark scheme. Also error to big.

### G2 · d46ecf7c

![G2 d46ecf7c](../../runs/2026-10-01-skill-v0.1.0/cases/verl-ppo-step/arms/with/ppo-step.png)

**Comment:** the major problem of this picture is direction of the arrow, for example, sleep replica is gen pointing to ckpt engine.

### G2 · e125d79e

![G2 e125d79e](../../runs/2026-10-04-gpt-5.6-sol-three-arm/cases/verl-ppo-step/arms/with/out/ppo-step.png)

**Comment:**  we can see this pic is trying to mini the multi column scheme, it is better though. but not as good as b22ede75. It is good enough though.

### G2 · f5a313af

![G2 f5a313af](../../runs/2026-10-01-codex-imagegen-v1/cases/verl-ppo-step/arms/imagegen/ppo-step.png)

**Comment:** don’t like the color scheme. good enough though.

### G2 · case notes

**Comment:** 

---

## G3-ffmpeg-transcode-threads

> I'm trying to understand how the ffmpeg command-line tool runs a transcode with threads. The fftools source, pinned at the commit in `PINNED.txt`, is in the read-only source directory available to this session. Draw one diagram that explains the threaded transcoding pipeline: which threads exist, what queues sit between them, how packets and frames flow from demuxer to muxer (including stream copy), how backpressure works, and how the scheduler keeps the outputs in sync. Ground every element in the code. Save the finished diagram as a PNG image at `out/transcode-threads.png`.

Reference: [answer key](../../evals/ffmpeg-transcode-threads/answer-key.md) · [source](../../evals/ffmpeg-transcode-threads/src/)

### G3 · 1bdb9dba

![G3 1bdb9dba](../../runs/2026-10-01-skill-v0.1.0/cases/ffmpeg-transcode-threads/arms/without/transcode-threads.png)

**Comment:** too many words in each box. although it shows the main flow clearly.

### G3 · 77c4b51b

![G3 77c4b51b](../../runs/2026-10-01-codex-imagegen-v1/cases/ffmpeg-transcode-threads/arms/imagegen/transcode-threads.png)

**Comment:** this cartoon like style would be perfact for illustration, but not tech enough and lose too many detail and not serious enough, it seems. 

### G3 · 8c4c4637

![G3 8c4c4637](../../runs/2026-10-04-gpt-5.6-sol-three-arm/cases/ffmpeg-transcode-threads/arms/with/out/transcode-threads.png)

**Comment:** : I like the data plane in this case best, it clearly shows the function, data and interaction with different queues.  The only thing to wonder is the part stream copy send packet ref/eof to send_to_mux, I may have question about this part. 确实没懂那里是个信号好事什么。 control panel drawing is ok, but the blow part is very confusing. 那三个不同的框。而且没看出control panel和 data panel的交互。

### G3 · d2237ccb

![G3 d2237ccb](../../runs/2026-10-01-skill-v0.1.0/cases/ffmpeg-transcode-threads/arms/with/transcode-threads.png)

**Comment:** 这个也还行吧，虽然排版没有另一个好，而且内容也偏多，确实这里更容易看出来 scheduler是中心。线会有点杂乱，但感觉控制模型比8c4c4637清楚。

### G3 · d8edd397

![G3 d8edd397](../../runs/2026-10-04-gpt-5.6-sol-three-arm/cases/ffmpeg-transcode-threads/arms/without/out/transcode-threads.png)

**Comment:** 这个就是线比较杂乱， 排版留白太多，不美观。

### G3 · d9dc767f

![G3 d9dc767f](../../runs/2026-10-04-gpt-5.6-sol-three-arm/cases/ffmpeg-transcode-threads/arms/imagegen/out/transcode-threads.png)

**Comment:** 从信息含量和整体布局排版上，这一幅应该最好，但我不喜欢这种字体和配色。

### G3 · case notes

**Comment:** 

---

## G4-redis-request-path

> I'm trying to understand how Redis 8 handles a client request when I/O threads are enabled (`io-threads` greater than 1). The Redis source, pinned at the tag and commit in `PINNED.txt`, is in the read-only source directory available to this session. Draw one diagram that explains the life of one request across the main thread and an I/O thread: which thread accepts the connection, which reads and parses the query, which executes the command, which writes the reply, and how the client is handed between threads. Ground every element in the code. Save the finished diagram as a PNG image at `out/request-path.png`.

Reference: [answer key](../../evals/redis-request-path/answer-key.md) · [source](../../evals/redis-request-path/src/)

### G4 · 02d4d074

![G4 02d4d074](../../runs/2026-10-01-skill-v0.1.0/cases/redis-request-path/arms/without/request-path.png)

**Comment:** 这个挺好，挺清楚的，就是每个box内容太多，字号偏小。

### G4 · 7bd02c74

![G4 7bd02c74](../../runs/2026-10-04-gpt-5.6-sol-three-arm/cases/redis-request-path/arms/imagegen/out/request-path.png)

**Comment:** 配色太鲜艳，其实内容是很清楚的。

### G4 · 7d98c63e

![G4 7d98c63e](../../runs/2026-10-04-gpt-5.6-sol-three-arm/cases/redis-request-path/arms/with/out/request-path.png)

**Comment:** 这一个应该是我觉得skill里最糟糕的一张图，配色很有问题。特别是这些大的block

### G4 · 8555a918

![G4 8555a918](../../runs/2026-10-01-skill-v0.1.0/cases/redis-request-path/arms/with/request-path.png)

**Comment:** 内容是清楚的，但是一方面时排版的问题，另一方面是时序不是很清楚。

### G4 · a99b55ec

![G4 a99b55ec](../../runs/2026-10-04-gpt-5.6-sol-three-arm/cases/redis-request-path/arms/without/out/request-path.png)

**Comment:** 我觉得，除了黑色的背景和配色，应该说这一幅是我最喜欢，时序图本身就很适合吧。

### G4 · b638523b

![G4 b638523b](../../runs/2026-10-01-codex-imagegen-v1/cases/redis-request-path/arms/imagegen/request-path.png)

**Comment:** 我确实不喜欢这种卡通类型的配色。

### G4 · case notes

**Comment:** 

---

## M1-megatron-tp-sp-mlp

> I'm trying to understand tensor parallelism with sequence parallelism in Megatron-Core. The source, pinned at the commit in `PINNED.txt`, is in the read-only source directory available to this session. Draw one diagram of a single transformer MLP block (fc1 → activation → fc2) on one of p tensor-parallel ranks with sequence parallelism enabled. Show the per-rank tensor and weight shapes in terms of s, b, h, the FFN hidden size and p, and where all-gather and reduce-scatter happen, in both the forward and the backward pass. Ground every element in the code. Save the finished diagram as a PNG image at `out/tp-sp-mlp.png`.

Reference: [answer key](../../evals/megatron-tp-sp-mlp/answer-key.md) · [source](../../evals/megatron-tp-sp-mlp/src/)

### M1 · 04eed4f3

![M1 04eed4f3](../../runs/2026-10-01-skill-v0.1.0/cases/megatron-tp-sp-mlp/arms/without/tp-sp-mlp.png)

**Comment:** Not what is required. fail.

### M1 · 1a297a07

![M1 1a297a07](../../runs/2026-10-01-codex-imagegen-v1/cases/megatron-tp-sp-mlp/arms/imagegen/tp-sp-mlp.png)

**Comment:** good, nothing to comment.

### M1 · 4a7c14b4

![M1 4a7c14b4](../../runs/2026-10-04-gpt-5.6-sol-three-arm/cases/megatron-tp-sp-mlp/arms/without/out/tp-sp-mlp.png)

**Comment:** 箭头大小，每个block里文字的layout。以及不喜欢深色。

### M1 · 54a5fbd7

![M1 54a5fbd7](../../runs/2026-10-04-gpt-5.6-sol-three-arm/cases/megatron-tp-sp-mlp/arms/with/out/tp-sp-mlp.png)

**Comment:** 这一个主要还是有些box偏大，重叠了，而且一行没摆下，有拐弯不美观。

### M1 · c87e8342

![M1 c87e8342](../../runs/2026-10-04-gpt-5.6-sol-three-arm/cases/megatron-tp-sp-mlp/arms/imagegen/out/tp-sp-mlp.png)

**Comment:** image gen的图，配色比较卡通，也喜欢圆角字体。比较适合演示，但同样，信息量没有skill的更大，更全面。

### M1 · e0edfc5a

![M1 e0edfc5a](../../runs/2026-10-01-skill-v0.1.0/cases/megatron-tp-sp-mlp/arms/with/tp-sp-mlp.png)

**Comment:** 这一幅应该是最好的，应该是得满分。

### M1 · case notes

**Comment:** 

---

## M2-vllm-v1-mixed-batch-attn

> I'm trying to understand how vLLM V1's GPU model runner turns one mixed batch, where some requests prefill a chunk and others decode one token, into attention inputs. The source, pinned at the commit in `PINNED.txt`, is in the read-only source directory available to this session. Draw one diagram that uses a small concrete example batch to show how the scheduled tokens are flattened; how `query_start_loc`, `seq_lens`, `block_table` and `slot_mapping` are built; and how the FlashAttention backend uses them to write the new K/V into the paged KV cache and read it back. Ground every element in the code. Save the finished diagram as a PNG image at `out/mixed-batch-attn.png`.

Reference: [answer key](../../evals/vllm-v1-mixed-batch-attn/answer-key.md) · [source](../../evals/vllm-v1-mixed-batch-attn/src/)

### M2 · 61583ee3

![M2 61583ee3](../../runs/2026-10-01-skill-v0.1.0/cases/vllm-v1-mixed-batch-attn/arms/without/mixed-batch-attn.png)

**Comment:** 其实我不是很喜欢这种poster-like的感觉。虽然这幅图实际没啥问题。其实这个case不是model architecture cover的范围，他不属于模型结构。当然也还ok。

### M2 · 6fe5779e

![M2 6fe5779e](../../runs/2026-10-01-skill-v0.1.0/cases/vllm-v1-mixed-batch-attn/arms/with/mixed-batch-attn.png)

**Comment:** 这个一样的，我觉得倒是不影响阅读。中间的线。本身也表达，kv cache的存储顺序是乱的。

### M2 · 85ac7bde

![M2 85ac7bde](../../runs/2026-10-04-gpt-5.6-sol-three-arm/cases/vllm-v1-mixed-batch-attn/arms/without/out/mixed-batch-attn.png)

**Comment:** 配色不好，橙色，深绿太高饱和了。

### M2 · 8ff5963f

![M2 8ff5963f](../../runs/2026-10-04-gpt-5.6-sol-three-arm/cases/vllm-v1-mixed-batch-attn/arms/with/out/mixed-batch-attn.png)

**Comment:** 其实就是我说的，这个图本身有连线遮挡的问题，但内容是全的，但我整体不喜欢这种poster风格。一个图，介绍所有步骤。而且这个case不适合m skill

### M2 · a58a7a4d

![M2 a58a7a4d](../../runs/2026-10-01-codex-imagegen-v1/cases/vllm-v1-mixed-batch-attn/arms/imagegen/mixed-batch-attn.png)

**Comment:** 配色太卡通了。且信息偏少

### M2 · b9950cf1

![M2 b9950cf1](../../runs/2026-10-04-gpt-5.6-sol-three-arm/cases/vllm-v1-mixed-batch-attn/arms/imagegen/out/mixed-batch-attn.png)

**Comment:** 配色太卡通了。且信息偏少

### M2 · case notes

**Comment:** 

---

## A1-vllm-v1-process-arch

> I want an architecture overview of how vLLM V1 is put together when it serves a model on one node with tensor parallelism and the multiprocess executor. The engine source, pinned at the commit in `PINNED.txt`, is in the read-only source directory available to this session. Draw one architecture diagram showing which OS processes exist, which components live in each process, and how the processes are connected (what transport, what travels over each link). This is about structure, not about the order of steps. Ground every element in the code. Save the finished diagram as a PNG image at `out/process-arch.png`.

Reference: [answer key](../../evals/vllm-v1-process-arch/answer-key.md) · [source](../../evals/vllm-v1-process-arch/src/)

### A1 · 0feeb41d

![A1 0feeb41d](../../runs/2026-10-04-gpt-5.6-sol-three-arm/cases/vllm-v1-process-arch/arms/imagegen/out/process-arch.png)

**Comment:** 配色太卡通了。但整体布局我很喜欢， 很清楚。

### A1 · 2e3e34c4

![A1 2e3e34c4](../../runs/2026-10-04-gpt-5.6-sol-three-arm/cases/vllm-v1-process-arch/arms/without/out/process-arch.png)

**Comment:** 这个也差不多，但主要问题还是配色。

### A1 · 44dce42a

![A1 44dce42a](../../runs/2026-10-04-gpt-5.6-sol-three-arm/cases/vllm-v1-process-arch/arms/with/out/process-arch.png)

**Comment:** 这个也没啥问题，挺好的。

### A1 · 9c82de56

![A1 9c82de56](../../runs/2026-10-01-skill-v0.1.0/cases/vllm-v1-process-arch/arms/without/process-arch.png)

**Comment:** 这个内容就太多了，而且排版问题很大。

### A1 · bba2c896

![A1 bba2c896](../../runs/2026-10-01-codex-imagegen-v1/cases/vllm-v1-process-arch/arms/imagegen/process-arch.png)

**Comment:** 这个也没啥大问题。就是最右边有两个箭头和左边不一致，容易引起误解。

### A1 · fd86cbc4

![A1 fd86cbc4](../../runs/2026-10-01-skill-v0.1.0/cases/vllm-v1-process-arch/arms/with/process-arch.png)

**Comment:** 排版不好，但其实内容是最全的。但是内容最清楚。

### A1 · case notes

**Comment:** 

---

## A2-verl-resource-placement

> I want an architecture overview of how verl lays out a PPO/GRPO job on a Ray cluster. The trainer source, pinned at the commit in `PINNED.txt`, is in the read-only source directory available to this session. Draw one architecture diagram showing the driver, the Ray resource pools and what GPUs they cover, which roles (actor, rollout, reference, critic, reward model, teacher) are mapped to which pool, which roles share the same worker processes, and how the rollout servers, the reward loop and the weight-sync component are connected to them. This is about structure and placement, not about the order of the training steps. Ground every element in the code. Save the finished diagram as a PNG image at `out/resource-placement.png`.

Reference: [answer key](../../evals/verl-resource-placement/answer-key.md) · [source](../../evals/verl-resource-placement/src/)

### A2 · 208d31f6

![A2 208d31f6](../../runs/2026-10-01-skill-v0.1.0/cases/verl-resource-placement/arms/with/resource-placement.png)

**Comment:** 这幅也是清楚的，就是连线太乱看不清，而且布局不太好。

### A2 · 3223b16a

![A2 3223b16a](../../runs/2026-10-04-gpt-5.6-sol-three-arm/cases/verl-resource-placement/arms/without/out/resource-placement.png)

**Comment:** 这个主要是连线遮挡内容。

### A2 · 49f8027c

![A2 49f8027c](../../runs/2026-10-04-gpt-5.6-sol-three-arm/cases/verl-resource-placement/arms/with/out/resource-placement.png)

**Comment:** 这个第一是连线很乱，同时右下角的global pool几个大的填色block，很丑。不美观。

### A2 · 6eed9fef

![A2 6eed9fef](../../runs/2026-10-01-skill-v0.1.0/cases/verl-resource-placement/arms/without/resource-placement.png)

**Comment:** 这个就比较乱了，当然layout 很不好。

### A2 · 89ec0612

![A2 89ec0612](../../runs/2026-10-04-gpt-5.6-sol-three-arm/cases/verl-resource-placement/arms/imagegen/out/resource-placement.png)

**Comment:** 配色太鲜艳了，我很喜欢左侧的control plane。

### A2 · cbd1fa32

![A2 cbd1fa32](../../runs/2026-10-01-codex-imagegen-v1/cases/verl-resource-placement/arms/imagegen/resource-placement.png)

**Comment:** 也应该说这幅图最清楚。除了配色和字体。

### A2 · case notes

**Comment:** 

---

## A3-megatron-parallel-groups

> I want an architecture view of how Megatron-Core lays out its process groups. The source, pinned at the commit in `PINNED.txt`, is in the read-only source directory available to this session. For 16 GPUs on 2 nodes (8 per node) with tensor-parallel size 2, pipeline-parallel size 4 and no context or expert parallelism, draw one diagram that shows every rank, which node it is on, and which tensor-parallel, pipeline-parallel, data-parallel and model-parallel group it belongs to, plus the embedding group. Make clear the rule that assigns ranks to groups. Ground every element in the code. Save the finished diagram as a PNG image at `out/parallel-groups.png`.

Reference: [answer key](../../evals/megatron-parallel-groups/answer-key.md) · [source](../../evals/megatron-parallel-groups/src/)

### A3 · 1daf798b

![A3 1daf798b](../../runs/2026-10-01-skill-v0.1.0/cases/megatron-parallel-groups/arms/with/parallel-groups.png)

**Comment:** 布局不太好。

### A3 · 73c5e8d6

![A3 73c5e8d6](../../runs/2026-10-01-codex-imagegen-v1/cases/megatron-parallel-groups/arms/imagegen/parallel-groups.png)

**Comment:** 这个可能整组最好吧。

### A3 · a00afc4a

![A3 a00afc4a](../../runs/2026-10-04-gpt-5.6-sol-three-arm/cases/megatron-parallel-groups/arms/imagegen/out/parallel-groups.png)

**Comment:** 同样的表格，排版好一些吧。

### A3 · c8fcd33b

![A3 c8fcd33b](../../runs/2026-10-04-gpt-5.6-sol-three-arm/cases/megatron-parallel-groups/arms/with/out/parallel-groups.png)

**Comment:** 表格形式就是差强人意吧。

### A3 · cabeeecb

![A3 cabeeecb](../../runs/2026-10-04-gpt-5.6-sol-three-arm/cases/megatron-parallel-groups/arms/without/out/parallel-groups.png)

**Comment:** 不喜欢黑色背景，但整体布局挺好。

### A3 · cca705dc

![A3 cca705dc](../../runs/2026-10-01-skill-v0.1.0/cases/megatron-parallel-groups/arms/without/parallel-groups.png)

**Comment:** 配色太丑了

### A3 · case notes

**Comment:** 这个case也很不合适，就不是架构的内容，纯粹是个部署的问题。这个case不应该计入计分。

---
