# Drawing-skill A/B eval — plan

> **Status (2026-10-01):** G1, G2–G4, M1–M2 and A1–A3 were run against drawing-skills 0.1.0 (one run per arm) and archived in [`runs/2026-10-01-skill-v0.1.0/`](../../runs/2026-10-01-skill-v0.1.0/README.md). That run's design does not measure the skill's claimed value (see its [LIMITATIONS.md](../../runs/2026-10-01-skill-v0.1.0/reviews/LIMITATIONS.md)); treat its scores as invalid for judging the skill. Case definitions stay in `evals/`; run outputs go under `runs/<date>-skill-v<version>/`.

This file is the task spec for the cloud session. Execute it step by step and obey every **STOP** gate: at a gate, report and wait for the user; do not continue on your own and do not invent workarounds.

## 1. Goal

Measure whether the two diagram skills in `skills/` (`graphviz`, `model-architecture`) make Claude produce better diagrams than Claude without them, on small, real questions taken from codebases the user works with daily (AI infra: vLLM, verl, Megatron-Core; classic systems: FFmpeg, Redis).

## 2. Fixed decisions

| Decision | Value | Reason |
|---|---|---|
| Harness | `claude plugin eval` | Built-in with/without-plugin ablation, isolated runs, image-capable LLM judge |
| Agent model | `opus` | The user's daily model; the delta should reflect daily use |
| Judge model | `opus` | User's choice. Self-preference bias inflates both arms roughly equally; read the delta, not the absolute score |
| Runs per arm | `1` | User's choice (cost). Results are one sample per arm: report them as such, not as a stable Δ |
| Scope | Round 1: G1. Round 2: G2, G3, G4, M1, M2 (tag `round2`) | User's choice; Q1 stays in reserve |
| Plugin contents | Both skills | Also tests that the agent routes a scheduling-flow question to `graphviz`, not `model-architecture` |
| Budget | Cloud session credit ($100, expires 2026-11-05); `--max-cost-usd 10` on the full run (one run per arm, about $2.5 incl. judges) | Leaves margin for authoring work in the same session |
| Branch | `g1-vllm-schedule` | Never push to `main` |

## 3. Harness facts the design depends on

Source: https://code.claude.com/docs/en/plugin-evals (checked 2026-10-01).

- Each run is a fresh `claude -p` child with a temporary home and an **empty** working directory. No user/project `CLAUDE.md`, memory, settings or other skills load, so the without-arm is a clean no-skill baseline.
- Source code reaches a run only through `context.add_dirs` in `case.yaml`: directories **inside the case directory**, read-only. Hence vendored excerpts under `evals/<case>/src/`, not a full clone.
- Write and Bash are removed unless granted with `--allow-tools`. Granting Bash requires the OS sandbox (`bubblewrap` + `socat` on Linux, installed by `cloud-setup.sh`).
- An `llm` grader whose `focus` is `{ source: file, path: <x>.png }` sees the PNG as an image. `file_exists` counts only files created during the run.
- `tool_used: Skill` graders are a plugin-fired indicator under two-arm runs and are excluded from the score.
- Workspaces are deleted after each run unless `--keep-temp` is passed.

## 4. Case catalog

All candidate cases. Case directories: G1 `vllm-v1-schedule`, G2 `verl-ppo-step`, G3 `ffmpeg-transcode-threads`, G4 `redis-request-path`, M1 `megatron-tp-sp-mlp`, M2 `vllm-v1-mixed-batch-attn`. Since round 1 every prompt is tool-neutral and asks only for a PNG (the Output column's source files are no longer required). Each asks for one diagram that explains one mechanism, reading vendored source at a pinned commit. Prompts never name a skill; they fix the output path and format so both arms produce the same artifact type. File lists are starting points to be confirmed at the pinned commit.

| ID | Status | Skill | Codebase | Question | Vendored files (to confirm) | Output |
|---|---|---|---|---|---|---|
| G1 | **Round 1** | graphviz | vLLM V1 | What one `Scheduler.schedule()` step does under continuous batching with chunked prefill: per-step token budget, running requests before waiting requests, chunked prefill, KV block allocation, preemption, and what the step hands to the model runner | `vllm/v1/core/sched/scheduler.py`, `vllm/v1/core/sched/output.py`, `vllm/v1/core/kv_cache_manager.py`, `vllm/v1/request.py` | `out/schedule-step.dot` + `.png` |
| G2 | **Round 2** | graphviz | verl | Single-controller data flow of one PPO/GRPO training step: rollout → old/ref logprob → reward → advantage → actor (and critic) update, and where weights are resharded between trainer and rollout engine | `verl/trainer/ppo/ray_trainer.py`, FSDP/Megatron worker files | `out/ppo-step.dot` + `.png` |
| G3 | **Round 2** | graphviz | FFmpeg 7.x | Threaded transcoding pipeline in `fftools`: demux, decode, filter, encode and mux threads and the scheduler queues between them | `fftools/ffmpeg_sched.c`, `ffmpeg_demux.c`, `ffmpeg_dec.c`, `ffmpeg_filter.c`, `ffmpeg_enc.c`, `ffmpeg_mux.c` | `out/transcode-threads.dot` + `.png` |
| G4 | **Round 2** | graphviz | Redis 8 | Life of one request across the main thread and I/O threads: read, parse, execute, reply | `src/ae.c`, `src/networking.c`, `src/iothread.c`, `src/server.c` (excerpts) | `out/request-path.dot` + `.png` |
| M1 | **Round 2** | model-architecture | Megatron-Core | Tensor-parallel + sequence-parallel MLP: per-rank tensor shapes and where all-gather / reduce-scatter happen, forward and backward | `megatron/core/tensor_parallel/layers.py`, `mappings.py`, `megatron/core/transformer/mlp.py` | `out/tp-sp-mlp.tex` + `.png` |
| M2 | **Round 2** | model-architecture | vLLM V1 | How a mixed prefill+decode batch is flattened into attention metadata: `query_start_loc`, `seq_lens`, `block_table`, `slot_mapping`, and the paged-KV write/read they drive (companion to G1) | `vllm/v1/worker/gpu_model_runner.py`, `vllm/v1/attention/backends/` (one backend) | `out/mixed-batch-attn.tex` + `.png` |
| Q1 | Reserve | graphviz | Qt | Cross-thread signal/slot delivery via queued connection and the receiver's event loop | not sliced yet (codebase too large to vendor cleanly) | — |

Licenses to respect when vendoring into this private repo: vLLM and verl Apache-2.0, Megatron-LM BSD-3/Apache-2.0, FFmpeg LGPL-2.1+, Redis 8 tri-license (RSALv2 / SSPLv1 / AGPLv3). Keep the repo private.

## 5. G1 specification

### 5.1 Case layout

```text
evals/vllm-v1-schedule/
├── prompt.md          # frontmatter + prompt body
├── case.yaml          # context.add_dirs: [src]
├── src/               # vendored files, plus PINNED.txt (repo URL, commit SHA, date, file list)
├── answer-key.md      # facts with file:line, for human review; copied into the correctness grader
└── graders/
    ├── render.md          # file_exists out/schedule-step.png
    ├── correctness.md     # llm on the PNG against the answer key
    ├── readability.md     # llm on the PNG against the visual rubric
    ├── skill-fired.md     # tool_used Skill, input_match graphviz (indicator only)
    └── skill-misrouted.md # tool_used Skill model-architecture, max 0 (indicator only)
```

### 5.2 prompt.md frontmatter

```yaml
runs: 1
max_turns: 60
timeout_seconds: 1800
allowed_tools: [Read, Glob, Grep, Skill, Write, Bash]
```

`plugins: ["../.."]` only if the smoke run reports that no plugin resolved.

### 5.3 Prompt body (draft; adjust only what the vendored code forces)

> I'm trying to understand how vLLM V1 does continuous batching. The scheduler source, pinned at the commit in `PINNED.txt`, is in the read-only source directory available to this session. Draw one diagram that explains what happens in a single scheduler step: how the per-step token budget is shared between already-running requests and waiting requests, how chunked prefill splits a long prompt across steps, where KV cache blocks are allocated, when and how preemption happens, and what the step outputs to the model runner. Ground every element in the code. Save the finished diagram as a PNG image at `out/schedule-step.png`.

### 5.4 Graders

| Grader | Type | Looks at | Passes when |
|---|---|---|---|
| render | `file_exists` | `out/schedule-step.png` | The PNG was created in the run |
| correctness | `llm` | `{ source: file, path: out/schedule-step.png }` | At least 7 of the 9 answer-key facts shown, none contradicted |
| readability | `llm` | same PNG | Labels legible at 100% zoom; no overlapping nodes or labels; one clear reading direction; edges distinguishable; consistent visual grammar (shape/colour encodes role); no orphan or decorative nodes |
| skill-fired | `tool_used` | trace | `tool: Skill`, `input_match: graphviz` (with-only indicator) |
| skill-misrouted | `tool_used` | trace | `tool: Skill`, `input_match: model-architecture`, `max: 0` (with-only indicator) |

**Tool neutrality.** The prompt names no drawing tool and asks only for a PNG, so the without-arm picks its own route (Graphviz, Mermaid, matplotlib, SVG, an image model, ...). Graders therefore look only at the PNG; there are no regex graders over a tool-specific source file. Which route each run took, and whether any run read outside `src/` (skills, answer key, graders), is extracted post hoc by `scripts/collect.py`, not graded, so neither changes either arm's score.

### 5.5 Answer key requirements

6–10 facts about one scheduling step, each a single checkable sentence with `src/...:line`. Cover at least: the budget's source and how it is decremented; the order running → waiting; how chunked prefill limits `num_new_tokens`; where `allocate_slots` is called and what happens when it fails (preempt which request, put back where); the stop condition for admitting waiting requests; the shape of `SchedulerOutput` (new vs. cached requests, `num_scheduled_tokens`). Write facts as mechanism, not as code trivia a picture cannot show.

## 6. Cloud procedure

Work on branch `g1-vllm-schedule`. Commit after each step.

1. **Preflight.** Report `claude --version`, `claude plugin eval --help | head -3`, `dot -V`, `bwrap --version`. If `plugin eval` is missing or reports early access/unavailable → **STOP**.
2. **Pin and vendor.** Shallow-clone `https://github.com/vllm-project/vllm` (`main`) outside the repo, record the SHA and date in `src/PINNED.txt`, copy the files in §4/G1 (add any file the step logic needs to be understandable; keep the total small), delete the clone.
3. **Author.** Write `answer-key.md`, `prompt.md`, `case.yaml`, and all graders per §5.
4. **STOP — key review.** Show the user the answer key, the prompt, and the grader table. Wait for approval or edits.
5. **Smoke run** (one with-arm run, cheap):
   ```bash
   claude plugin eval . --case vllm-v1-schedule --runs 1 --ablation none \
     --model opus --judge-model opus \
     --allow-tools Write Bash \
     --trust-plugin --keep-temp --max-cost-usd 10 --publish-report
   ```
   Check: the child authenticated; Bash ran under the sandbox; the PNG rendered; every grader produced a verdict; report the cost estimate. If auth, sandbox, or render fails → **STOP** and report the exact error; no workarounds.
6. **STOP — credit check.** Ask the user to look at the cloud session credit bar and confirm it moved (i.e. eval child runs are billed to the credit). Wait for go.
7. **Full run:**
   ```bash
   claude plugin eval . --case vllm-v1-schedule \
     --model opus --judge-model opus \
     --allow-tools Write Bash \
     --trust-plugin --keep-temp --max-cost-usd 10 --threshold 0 \
     --json evals/vllm-v1-schedule/results.json --publish-report
   ```
7b. **Round 2 run** (after the round-2 key review): all five round-2 cases, one run per arm:
   ```bash
   claude plugin eval . --tag round2 \
     --model opus --judge-model opus \
     --allow-tools Write Bash \
     --trust-plugin --keep-temp --max-cost-usd 25 --threshold 0 \
     --json evals/results.json --publish-report
   ```
8. **Collect.** Run `python3 scripts/collect.py` (set `RUN_DIR` and `RESULTS_JSON` at the top): it copies each run's `out/` into `<RUN_DIR>/cases/<case>/artifacts/{with,without}-<n>/` and writes `artifacts/runs.json` (route taken, programs run, leaks). Commit `results.json` and `artifacts/`, push the branch, then delete the kept temp dirs.
9. **Human aesthetics rating.** Aesthetics (palette, contrast, polish) is not an automated grader; the user rates it by hand. Present the PNGs from `artifacts/` blind: shuffled, with arm labels hidden, and reveal the arm mapping only after the ratings are recorded.
10. **Report.** Give: suite score per arm and Δ; per-grader pass rates per arm; whether the skill fired in each with-arm run; which drawing route each run took; any leak flagged by `collect.py`; the judges' main reasons for failures; **agent-only** wall time, cost and turns per arm (mean / median / sd, from each trace's `result` record via `artifacts/summary.json`, judge calls excluded), with judge cost listed separately; total cost estimate; the published report URL. Then **STOP**.

## 7. Known unknowns (resolve in steps 1, 5, 6)

| Unknown | Resolved at | If it fails |
|---|---|---|
| `plugin eval` child sessions authenticate inside the cloud VM | Step 5 | Stop; fallback is running the eval locally |
| `bubblewrap` sandbox works inside the cloud VM | Step 5 | Stop; same fallback |
| Eval child runs are billed to the cloud session credit | Step 6 | Stop; user decides |
| The agent can locate `add_dirs` without being told the absolute path | Step 5 (read the trace) | Adjust the prompt wording, rerun smoke |
| The published HTML report embeds the PNGs | Step 5 | Rely on `artifacts/` in the repo |
