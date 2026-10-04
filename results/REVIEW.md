# Blind Scoring Review — 54 diagrams, 9 cases

Scored against [`RUBRIC-FINAL.md`](RUBRIC-FINAL.md). Full per-image scores, defects and evidence are in [`scores.json`](scores.json).
Ranking is by `technical_30` (= total + Fidelity). Ties are broken by Fidelity, then `total_25`.
Score columns: **F**idelity · **C**overage · F**l**ow · **L**egibility · **V**isual encoding.

**Headline:** 52 of 54 images have no material error. The two with material errors are **A2/cbd1fa32** (crossed manager-to-pool wiring) and **M1/c87e8342** (backward all-gather wired into dX instead of dW1). Six more images have only minor slips. Correctness is generally very high. In most cases the ranking is decided by layout and legibility, not by fidelity.

---

## A1 — vLLM V1 process architecture (TP, multiprocess executor)

| Rank | Image | F | C | Fl | L | V | total_25 | technical_30 |
|---|---|---|---|---|---|---|---|---|
| 1 | 2e3e34c4 | 5 | 5 | 5 | 4 | 5 | 24 | **29** |
| 2 | 9c82de56 | 5 | 5 | 4 | 3 | 5 | 22 | 27 |
| 3 | bba2c896 | 4 | 5 | 4 | 5 | 5 | 23 | 27 |
| 4 | 44dce42a | 5 | 5 | 4 | 3 | 3 | 20 | 25 |
| 5 | 0feeb41d | 4 | 5 | 4 | 4 | 4 | 21 | 25 |
| 6 | fd86cbc4 | 5 | 5 | 3 | 3 | 3 | 19 | 24 |

**What separates them.** All six have the right process count and transports: ZMQ ROUTER→DEALER and PUSH→PULL, a shared-memory broadcast MessageQueue plus a per-worker response queue, and one WorkerProc per GPU. 2e3e34c4 is the only one that is fully correct, laid out in reading order, *and* keyed. The others either lose fidelity to labelling slips (bba2c896, 0feeb41d) or lose legibility and flow to their canvas (a 2:1 banner, a 0.54 tall strip, an auto-laid-out graph).

**Material defects:** none.

- **2e3e34c4** — *Good:* N+2 processes, socket types and directions, engine I/O threads, file-store rendezvous, lifecycle pipes, and worker-owned weights/KV are all verified, with numbered code anchors and a legend. *Improve:* enlarge the grey footnote text.
- **9c82de56** — *Good:* the most exhaustively cited. It shows the driver-worker rule, the `output_rank` formula, the READY handshake and the monitor threads, with per-process colours and a full edge legend. *Improve:* the 2:1 banner forces tiny text. Reflow to about 1.5:1, or drop startup detail to buy font size.
- **bba2c896** — *Good:* clean three-tier layout, correct payloads, complete legend, comfortable to read. *Improve:* fix the three module paths under the titles. `AsyncLLM` lives in `vllm.v1.engine.async_llm`, `EngineCoreProc` in `vllm.v1.engine.core`, and `WorkerProc` in `vllm.v1.executor.multiproc_executor`.
- **44dce42a** — *Good:* complete and correct, including payload contents and the TP group. *Improve:* the 0.54 aspect ratio forces scrolling. Attach the IPC boxes to their edges with one-way arrows, and add a legend for the four node shapes.
- **0feeb41d** — *Good:* compact one-host view. "MultiprocExecutor is not a separate OS process" is called out, and both shared-memory queues are labelled with what they carry. *Improve:* the blue per-worker response-queue arrows also point *into* the workers. Make that link worker→executor only, and key the blue/orange colour split.
- **fd86cbc4** — *Good:* every node and edge cites the source and checks out, down to which side binds or connects. *Improve:* re-lay it out left-to-right (frontend → EngineCore → workers). Today the frontend sits far right, workers bottom-left, and long arcs cross empty space. Add a shape legend.

---

## A2 — verl resource placement on Ray

| Rank | Image | F | C | Fl | L | V | total_25 | technical_30 |
|---|---|---|---|---|---|---|---|---|
| 1 | 89ec0612 | 5 | 5 | 4 | 4 | 4 | 22 | **27** |
| 2 | 49f8027c | 5 | 5 | 4 | 3 | 4 | 21 | 26 |
| 3 | 6eed9fef | 5 | 5 | 4 | 3 | 4 | 21 | 26 |
| 4 | 3223b16a | 5 | 5 | 3 | 3 | 4 | 20 | 25 |
| 5 | 208d31f6 | 5 | 5 | 3 | 3 | 3 | 19 | 24 |
| 6 | cbd1fa32 | 2 | 5 | 3 | 4 | 3 | 17 | 19 |

**What separates them.** Five of six correctly show global, reward and teacher pools as placement groups. They also show the fused WorkerDict (actor + rollout + ref, plus critic) spawned once per GPU bundle, rollout replicas on the actor's pool, the conditional reward loop, and CheckpointEngineManager as the only weight path. The compact 89ec0612 reads best. The wide vector versions are equally correct but need zooming. cbd1fa32 is the one image whose wiring is wrong.

**Material defects**
- **cbd1fa32** — the solid weight-sync arrow from CheckpointEngineManager ends in `reward_pool` (`key#9`). A "teacher_client" arrow from MultiTeacherModelManager ends in `reward_pool`, and another leaves CheckpointEngineManager into `teacher_pool` (`src/verl/trainer/ppo/ray_trainer.py:925-934`).

- **89ec0612** — *Good:* fits pools with GPU formulas, fused roles in one process, rollout on the same GPUs with CUDA-IPC weight updates, and the conditional reward loop into one readable frame. *Improve:* text is small at native size, and the per-pool colours have no key.
- **49f8027c** — *Good:* the "one GPU slot" panel shows exactly what shares a Ray process and what runs beside it, and the weight-path row names every hop. *Improve:* the 2.35:1 banner leaves the driver column half empty. Rebalance it and raise the font size.
- **6eed9fef** — *Good:* driver handles, the per-bundle WorkerDict, a rollout replica with its separate CheckpointEngineWorker and CUDA-IPC hop, and both naive and NCCL/NIXL sync paths. *Improve:* 2.3:1 aspect, thin dotted edges, no legend.
- **3223b16a** — *Good:* role→pool table, "one OS process per rank", the 1/max_colocate_count GPU share, and a legend for box semantics. *Improve:* several long edges run through other boxes, and the "worker-group RPCs" label overprints placement-group text. Reroute the edges around boxes.
- **208d31f6** — *Good:* every element is correct and cited, including the sender/receiver checkpoint-engine pair. *Improve:* long crossing arcs, an empty top-right quadrant, and four unexplained node shapes.
- **cbd1fa32** — *Good:* pools, roles, the shared WorkerDict process and the rollout/checkpoint worker pair are drawn correctly and legibly. *Improve:* untangle the three manager→pool arrows. The checkpoint manager should connect the actor worker group to the rollout replicas, the teacher manager to `teacher_pool`, and the reward loop to `reward_pool`.

---

## A3 — Megatron-Core parallel groups (16 GPUs, TP=2, PP=4, DP=2)

| Rank | Image | F | C | Fl | L | V | total_25 | technical_30 |
|---|---|---|---|---|---|---|---|---|
| 1 | cabeeecb | 5 | 5 | 5 | 4 | 5 | 24 | **29** |
| 2 | cca705dc | 5 | 5 | 5 | 4 | 5 | 24 | **29** |
| 3 | 1daf798b | 5 | 5 | 4 | 4 | 5 | 23 | 28 |
| 4 | a00afc4a | 5 | 5 | 4 | 4 | 5 | 23 | 28 |
| 5 | c8fcd33b | 5 | 5 | 4 | 4 | 4 | 22 | 27 |
| 6 | 73c5e8d6 | 4 | 5 | 5 | 5 | 4 | 23 | 27 |

**What separates them.** All six get the rank formula `r = t + 2d + 4p` and every group roster right: TP [0,1]…, DP [0,2]…, PP [0,4,8,12]…, MP [0,1,4,5,8,9,12,13] / [2,3,…], and embedding [0,12]…. The top two *draw* the groups as a topology (pills or outlines on a node-by-stage grid) and explain the stride rule. The table-style images (a00afc4a, c8fcd33b) are complete but make the reader assemble the picture. 73c5e8d6 has the clearest grid but marks only half the embedding ranks.

**Material defects:** none.

- **cabeeecb** — *Good:* rank cards grouped by node and pipeline stage, with colour-coded pills for every group. A fastest-to-slowest stride panel and the derived group-index formulas make the rule explicit. *Improve:* the dark-theme text is small.
- **cca705dc** — *Good:* five group types, each with its own encoding (outline, bracket, arrow, band, border), a full legend, and a derivation panel with line references. *Improve:* the pills are small at normal size.
- **1daf798b** — *Good:* each rank card carries its (tp, dp, pp) coordinates and memberships. It states node = rank // 8 and the stage-1→2 inter-node hop. *Improve:* the dashed DP arcs cross each other. Route them inside each node.
- **a00afc4a** — *Good:* per-node tables with every membership, the formula, the DP derivation, and colour-matched rosters. *Improve:* it is a table, not a picture. Add a strip that shows PP groups crossing the node boundary.
- **c8fcd33b** — *Good:* the rule box (order collapse, formula, embedding = first + last stage), (t, d, p) coordinates, and complete rosters. *Improve:* the hexagon/cylinder framing is decorative. Plain boxes would free space for larger text.
- **73c5e8d6** — *Good:* the grid layout itself makes `r = t + 2d + 4p` visible, and it is very readable. *Improve:* circle ranks 1, 2, 13 and 14 as well. Only 0, 3, 12 and 15 are marked, although the legend says the circle means first/last PP rank.

---

## G1 — vLLM V1 one scheduler step

| Rank | Image | F | C | Fl | L | V | total_25 | technical_30 |
|---|---|---|---|---|---|---|---|---|
| 1 | 3f2ea037 | 5 | 5 | 5 | 4 | 5 | 24 | **29** |
| 2 | 599e7123 | 5 | 5 | 4 | 4 | 4 | 22 | 27 |
| 3 | 28f89ba6 | 4 | 5 | 5 | 4 | 5 | 23 | 27 |
| 4 | 1eba22c4 | 5 | 5 | 4 | 3 | 3 | 20 | 25 |
| 5 | 6e033b2b | 5 | 5 | 4 | 3 | 3 | 20 | 25 |
| 6 | db0db3ff | 5 | 5 | 4 | 2 | 3 | 19 | 24 |

**What separates them.** All six get the core mechanism right: one shared budget, the running list first, `allocate_slots` before commit, and preemption only on the running side, with the victim prepended to waiting. They also show that any preemption skips the waiting loop, that waiting admission never preempts, and the SchedulerOutput fields. 3f2ea037 shows this as a clean two-phase story with a chunking timeline. The three auto-laid-out graphs (1eba22c4, 6e033b2b, db0db3ff) are equally correct, and 6e033b2b is the most line-precise, but they waste canvas and leave line styles unexplained.

**Material defects:** none.

- **3f2ea037** — *Good:* state at start → Step 1 (compute delta, allocate, preempt-and-retry with budget restore) → Step 2 gated on "no preemption" → output → counter advance. Colours map to running / waiting / KV / preemption. *Improve:* only small text.
- **599e7123** — *Good:* the formula `n = min(need, B, I − draft_slots, cap)`, both allocate paths, and a correct 8-slot worked example. *Improve:* fix the garbled word "Sse". The shared `allocate_slots` box draws arrows from both phases, so split it in two.
- **28f89ba6** — *Good:* a compact three-panel layout with both budgets, the preemption gate, victim choice and a correct 6/13/18 chunk example. *Improve:* the example puts "req D (PREEMPTED, blocks held)" in the KV-holding queue. `_preempt_request` frees its blocks and *prepends it to `waiting`* (`scheduler.py:1558`).
- **1eba22c4** — *Good:* every stage and the 2048/2048/904 chunk arithmetic match the cited lines. *Improve:* a quarter of the canvas is empty, edges loop around the page, and the four node shapes have no legend.
- **6e033b2b** — *Good:* the most precise one. It catches the n==0 `continue` (not `break`), the "victim == current request" stop and `skip_request` re-queueing. *Improve:* a third of the square canvas is empty, edges cross it, and the solid/dashed/dotted styles are unexplained.
- **db0db3ff** — *Good:* complete and correct, including the optimistic state advance and the chunk timeline. *Improve:* the 8000-px canvas is mostly whitespace, so the labels are unreadable at normal size. Compress it to about 2500 px.

---

## G2 — verl one PPO/GRPO training step

| Rank | Image | F | C | Fl | L | V | total_25 | technical_30 |
|---|---|---|---|---|---|---|---|---|
| 1 | 43118728 | 5 | 5 | 5 | 4 | 5 | 24 | **29** |
| 2 | b22ede75 | 5 | 5 | 5 | 4 | 5 | 24 | **29** |
| 3 | c320d4b7 | 5 | 5 | 5 | 4 | 5 | 24 | **29** |
| 4 | f5a313af | 5 | 5 | 5 | 4 | 5 | 24 | **29** |
| 5 | e125d79e | 5 | 5 | 4 | 3 | 4 | 21 | 26 |
| 6 | d46ecf7c | 5 | 5 | 3 | 3 | 4 | 20 | 25 |

**What separates them.** All six get the order right: rollout → sleep replicas → reward → old log-probs → ref → values → advantage on the driver → critic update → actor update unless warming up → update_weights. They also get the driver / worker-group split and the naive vs NCCL/NIXL weight paths right. The four tied at 29 differ only in style:
- 43118728 has a growing DataProto strip.
- b22ede75 has the most detailed weight-sync breakdown.
- c320d4b7 has a cumulative batch ledger.
- f5a313af has a cited table.

The bottom two lose points to layout. d46ecf7c puts the driver sequence and its RPC targets at opposite ends of the canvas.

**Material defects:** none.

- **43118728** — *Good:* ten numbered driver stages, a DataProto strip growing A→F with exact keys, and a separate red weights arrow from actor to rollout. *Improve:* dense small text.
- **b22ede75** — *Good:* a twelve-step swim-lane table with a per-step batch ledger and the full naive and NCCL/NIXL weight-sync sequences. *Improve:* small text at normal size.
- **c320d4b7** — *Good:* columns for driver steps, the worker each step calls, and the cumulative DataProto ledger, plus a chip legend and "weights never stage on the driver". *Improve:* small text.
- **f5a313af** — *Good:* a cited nine-row table, the advantage row marked DRIVER, and a separate weight-transfer panel with a line-style legend. *Improve:* small text.
- **e125d79e** — *Good:* a numbered spine, conditional stages dashed, DataProto cylinders accumulating keys, and a critic-warmup branch. *Improve:* the 0.9 aspect ratio and sparse top-left keep the text small.
- **d46ecf7c** — *Good:* correct down to worker-method lines, and an accurate CheckpointEngineManager panel. *Improve:* place each RPC target next to its driver step. Today the edges sweep across the whole canvas.

---

## G3 — ffmpeg threaded transcode pipeline

| Rank | Image | F | C | Fl | L | V | total_25 | technical_30 |
|---|---|---|---|---|---|---|---|---|
| 1 | d9dc767f | 5 | 5 | 5 | 4 | 5 | 24 | **29** |
| 2 | 77c4b51b | 4 | 4 | 5 | 5 | 5 | 23 | 27 |
| 3 | 1bdb9dba | 5 | 5 | 4 | 3 | 4 | 21 | 26 |
| 4 | 8c4c4637 | 5 | 5 | 4 | 3 | 4 | 21 | 26 |
| 5 | d2237ccb | 5 | 5 | 3 | 3 | 4 | 20 | 25 |
| 6 | d8edd397 | 5 | 5 | 3 | 2 | 4 | 19 | 24 |

**What separates them.** All six have one thread per component, a queue at each consumer's input (decoder packets, filtergraph N+1 frames, encoder frames, muxer packets per stream), size-2 bounded queues, the stream-copy bypass, and muxer-DTS sync with a 100 ms tolerance. d9dc767f puts all of this in one readable data-plane row plus a control-plane row. 77c4b51b is the most readable but simplifies the queue set and the sync wording. The other four are correct but spread over too much canvas.

**Material defects:** none.

- **d9dc767f** — *Good:* five threads, queue cylinders with capacities, the optional SyncQueue, pre-mux AVFifo, stream-copy and subtitle bypasses, STOP/GO choke points, the scheduler loop and the start order, with a legend. *Improve:* small text.
- **77c4b51b** — *Good:* a very clean pipeline. The scheduler is drawn as shared state, not a thread, and backpressure and DTS alignment get separate panels. *Improve:* add the pre-mux queue, the sync queue and the filtergraph control stream. Choking also reaches downstream queues through `tq_choke`. Restate "unknown timestamps get priority" precisely (`ffmpeg_sched.c:1459-1462`).
- **1bdb9dba** — *Good:* each thread box carries its input queue with stream count and size, plus a correct six-step `schedule_update_locked`. *Improve:* the 2.5:1 banner needs zooming, and red control arrows cross the data path.
- **8c4c4637** — *Good:* separate data and control planes, every queue, the start order, and a backpressure box, all cited. *Improve:* the bottom third is white space. Crop it and enlarge the text.
- **d2237ccb** — *Good:* every queue and size, waiter hexagons, a main-thread box and an edge key. *Improve:* the scheduler sits far right, and stream-copy and choke edges loop around the page. Move the scheduler next to the queues.
- **d8edd397** — *Good:* correct and cited, with a useful "what sync does / does not mean" box. *Improve:* most of the canvas is empty, so the diagram is a thin band of ~10-px text. Shrink the canvas to the content.

---

## G4 — Redis 8 request path with I/O threads

| Rank | Image | F | C | Fl | L | V | total_25 | technical_30 |
|---|---|---|---|---|---|---|---|---|
| 1 | 7bd02c74 | 5 | 5 | 5 | 4 | 5 | 24 | **29** |
| 2 | b638523b | 5 | 5 | 5 | 4 | 5 | 24 | **29** |
| 3 | 02d4d074 | 5 | 5 | 5 | 4 | 4 | 23 | 28 |
| 4 | a99b55ec | 5 | 5 | 5 | 4 | 4 | 23 | 28 |
| 5 | 7d98c63e | 5 | 5 | 5 | 3 | 4 | 22 | 27 |
| 6 | 8555a918 | 5 | 5 | 4 | 3 | 4 | 21 | 26 |

**What separates them.** All six get the whole story right:
- the main thread accepts the connection and assigns the least-loaded I/O thread;
- the hand-off is a mutex list join plus an event notifier;
- the I/O thread binds the client with `readQueryFromClient`, reads, and parses;
- the I/O thread never executes; it sets `CLIENT_IO_PENDING_COMMAND` and hands the client back;
- the main thread executes the command;
- the I/O thread writes the reply.

The ranking is decided almost entirely by legibility and keying. 7d98c63e's 0.30 aspect ratio and 8555a918's 2:1 canvas push them down.

**Material defects:** none. (b638523b has a cosmetic line-number typo: 3355 for 3555.)

- **7bd02c74** — *Good:* eight steps alternating between the threads, and a bottom band that shows which thread owns each phase. *Improve:* fix the garbled raster glyphs ("conwriite", the commit hash).
- **b638523b** — *Good:* hand-off boxes name the lists, the mutex and the notifier. It covers the AOF `appendfsync=always` delay and the special-client scope. *Improve:* correct `networking.c:3355` → `3555`.
- **02d4d074** — *Good:* twelve numbered steps across three lanes. It catches the READ_ENABLED early-return and the batched notify-only-if-asleep hand-back. *Improve:* the hand-off lane is mostly empty, and the lane colours are not keyed.
- **a99b55ec** — *Good:* client / main / I/O lanes, explicit "not executed here" and "no socket write on this path" notes, and a "what hand-off means" box. *Improve:* hand-off labels brush the lane borders, and the step-number colours are not keyed.
- **7d98c63e** — *Good:* a strictly linear story with a precise ownership invariant (`tid` vs `running_tid`). *Improve:* the 0.30 aspect ratio needs scrolling, and the hexagons waste most of the width. Use two columns.
- **8555a918** — *Good:* the most line-precise, including the `keepClientInMainThread` exception path. *Improve:* the 2:1 canvas has tiny text and long looping edges, and the three edge colours are unexplained.

---

## M1 — Megatron-Core TP + SP MLP block

| Rank | Image | F | C | Fl | L | V | total_25 | technical_30 |
|---|---|---|---|---|---|---|---|---|
| 1 | 1a297a07 | 5 | 5 | 5 | 4 | 5 | 24 | **29** |
| 2 | 4a7c14b4 | 5 | 5 | 5 | 4 | 5 | 24 | **29** |
| 3 | e0edfc5a | 5 | 5 | 5 | 4 | 5 | 24 | **29** |
| 4 | 54a5fbd7 | 5 | 5 | 4 | 4 | 4 | 22 | 27 |
| 5 | 04eed4f3 | 4 | 5 | 5 | 4 | 5 | 23 | 27 |
| 6 | c87e8342 | 3 | 5 | 4 | 5 | 4 | 21 | 24 |

**What separates them.** All six get the shapes right: [s/p,b,h] input, W1 [F/p,h], [s,b,F/p] inside, W2 [h,F/p], partial [s,b,h], and [s/p,b,h] output. They also get forward AG-before-fc1 and RS-after-fc2, and backward AG of dY plus RS of fc1 dgrad. The top three also draw the re-gather of the saved input for dW1 as a *side branch feeding the weight gradient*, which is the subtle part. c87e8342 wires that branch wrongly.

**Material defects**
- **c87e8342** — "ALL-GATHER saved X_r for dW1_r" is drawn downstream of fc1 backward (which already lists dW1_r), and its output joins the arrow into dX_r. In the source the gathered input feeds the dW1 GEMM inside fc1's backward (`src/megatron/core/tensor_parallel/layers.py:767-781`).

- **1a297a07** — *Good:* forward left-to-right and backward right-to-left, every shape, and a dashed wgrad branch with a clean legend. *Improve:* a few raster sub/superscripts render oddly ("dX partial^r_r", "W1,r").
- **4a7c14b4** — *Good:* hexagonal collectives with direction and concat/split dimension, and an async AG branch overlapping the dgrad GEMM. *Improve:* "REDUCE-SCATTER" and "async; overlaps…" overflow their hexagons, and one activation note overprints its line reference.
- **e0edfc5a** — *Good:* three aligned lanes (forward / dgrad / wgrad) inside shaded SP and TP regions, so the shard boundaries are visible, with a line-style key. *Improve:* the 2.2:1 canvas makes the line anchors tiny.
- **54a5fbd7** — *Good:* correct formulas, callouts for wgrad reconstruction and the local fc2 wgrad, and accurate bias and weight-orientation notes. *Improve:* both rows wrap back on themselves at the end, and the colours are not keyed.
- **04eed4f3** — *Good:* mirrored forward and backward columns with a colour legend and a collectives count ("2 AG + 1 RS backward, no all-reduce"). *Improve:* drop "db1 = dZ1.sum (layers.py:895)" from fc1 backward. fc1 uses `skip_bias_add`, so db1 comes from autograd through the activation's bias add (`layers.py:1338`).
- **c87e8342** — *Good:* the most readable raster, with numbered stages and rank strips on every collective. *Improve:* move the saved-X all-gather *into* fc1 backward as the input to dW1, and connect only the reduce-scatter to dX_r.

---

## M2 — vLLM V1 mixed batch → FlashAttention inputs

| Rank | Image | F | C | Fl | L | V | total_25 | technical_30 |
|---|---|---|---|---|---|---|---|---|
| 1 | a58a7a4d | 5 | 5 | 5 | 5 | 5 | 25 | **30** |
| 2 | 61583ee3 | 5 | 5 | 5 | 4 | 5 | 24 | 29 |
| 3 | 85ac7bde | 5 | 5 | 5 | 4 | 5 | 24 | 29 |
| 4 | b9950cf1 | 5 | 5 | 5 | 4 | 5 | 24 | 29 |
| 5 | 6fe5779e | 5 | 5 | 4 | 3 | 5 | 22 | 27 |
| 6 | 8ff5963f | 5 | 5 | 4 | 3 | 4 | 21 | 26 |

**What separates them.** I recomputed every worked example by hand: `req_indices`, positions, `query_start_loc`, `seq_lens`, `block_table` rows and every `slot_mapping` value. All six are arithmetically correct. All six also show the write (`reshape_and_cache_flash` at `slot_mapping`) and the single varlen read (`cu_seqlens_q`, `seqused_k`, `block_table`). a58a7a4d is the only image in the whole set to score 30: four clear panels, crisp text, consistent per-request colours. 61583ee3 is the richest (four requests, with pad slots and discarded samples) but denser. 6fe5779e and 8ff5963f lose points to crossing write arrows and clipped labels.

**Material defects:** none.

- **a58a7a4d** — *Good:* a decode + chunked-prefill example, slot_mapping [117, 46, 47, 144], a cache view marking cached vs new slots, and a read panel tying each array to its kernel argument. *Improve:* nothing significant.
- **61583ee3** — *Good:* a four-request batch including pad −1 slots, `logits_indices`, `discard_request_mask` and a causal-mask grid for the chunked request. *Improve:* very dense, so split it in two or enlarge the text.
- **85ac7bde** — *Good:* five numbered panels and a closing "slot_mapping writes, block_table + seq_lens read" note. *Improve:* write arrows cover the physical-block-7 label.
- **b9950cf1** — *Good:* per-token block/offset derivation and a bottom cache strip marking old vs new per block. *Improve:* dense text at native size.
- **6fe5779e** — *Good:* per-token slot derivations, a block-by-block cache picture, per-request causal grids, and an honest "block_size 4 is illustrative" note. *Improve:* the curved write arrows criss-cross, and most annotations need zoom.
- **8ff5963f** — *Good:* mathematically careful, with bottom-right causal alignment and a numbered code ledger. *Improve:* labels are clipped or overprinted by the `[n]` markers ("pag", "cached before this st"), elbows cross panel borders, and request A changes colour between panels.

---

## Observations on the rubric

1. **Fidelity and Coverage hit the ceiling.** Fidelity is 5 on 46 of 54 images and Coverage on 53 of 54. In practice the ranking is decided by Flow, Legibility and Visual encoding (means 4.33 / 3.69 / 4.35). This reflects a strong image set more than a weak rubric: I checked dozens of line-level claims per case and found only two material errors. But it means `technical_30`'s double weight on Fidelity rarely changes a ranking. To separate correct diagrams, Coverage could grade *depth*: whether each ask is shown with its mechanism and a worked example, or just named.
2. **The schema has no "cosmetic" severity.** The rubric lets Fidelity 5 absorb cosmetic slips, but `defects[].severity` only allows `material | minor`. I recorded one line-number typo (G4/b638523b) as `minor`, prefixed it "Cosmetic:", and kept Fidelity 5. Every other minor defect got Fidelity 4. A third severity level would make this explicit.
3. **Minor-vs-cosmetic was the hardest boundary.** Six images fell exactly on it: wrong module paths, a misplaced example queue entry, a reversed arrowhead, incomplete embedding circles, loose sync wording, a misattributed bias-grad line. One minor slip costs a full Fidelity point, and therefore 2 points of `technical_30`. That outweighs a whole Legibility level, which feels heavy for a slip a reader would not act on.
4. **Many ties.** Seventeen images score exactly 29 (one scores 30), and G2 has a four-way tie at 29. Integer 1–5 scales with a 6-point spread at the top can't rank near-identical diagrams. Half-points, or a declared tie-break (I used Fidelity, then `total_25`), would help.
5. **Legibility conflated two failure modes.** These were (a) dense content on a reasonably sized canvas and (b) sparse content on a huge, mostly empty canvas (db0db3ff, d8edd397). The explicit "fit to a 1600-px screen" test and the aspect-ratio thresholds in `RUBRIC-FINAL.md` handled both consistently, so I'd keep them. The garbled-text rule was needed only for a few raster images (7bd02c74, 599e7123, 1a297a07), and only lightly.
6. **Wiring errors hide in polished diagrams.** Both material errors (A2/cbd1fa32, M1/c87e8342) were in otherwise legible, well-styled images. Their labels were all correct; only the arrow endpoints were wrong. A rubric note to check every connector's endpoints, not just its label, would make this check routine.
