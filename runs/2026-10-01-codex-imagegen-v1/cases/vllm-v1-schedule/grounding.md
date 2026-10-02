# Source grounding
Pinned source: src/PINNED.txt, vLLM commit 4c2d277643e217344056e1d2c42115d5f005912f.
- src/vllm/v1/core/sched/scheduler.py:565-574: unified token progress, no distinct prefill/decode scheduler phases.
- scheduler.py:583-586: token_budget and input_budget are separate.
- scheduler.py:629-690: running-first scheduling, token gap, cap, budget and model-length limits.
- scheduler.py:745-827: KV allocation before recording work; failed running allocation can preempt, retry, restore already scheduled victim budgets; pending connector frees and immediate-free safety can stop.
- scheduler.py:873-938: waiting only without preemptions and unpaused, KV-holding first, active request limit, blocked request handling and prefix lookup.
- scheduler.py:1074-1125: waiting gap and chunking budget; disabled chunking prevents oversized work.
- scheduler.py:1211-1232: waiting allocation failure stops admission.
- scheduler.py:1292-1318: admitted request enters running and consumes budgets.
- scheduler.py:1379-1409: V2 resumed request encoding as new data, cached updates for running.
- scheduler.py:1463-1479: SchedulerOutput fields.
- scheduler.py:1558-1583: preempt clears caches, resets computed progress, prepends waiting.
- scheduler.py:1585-1605: optimistic computed advancement, next prefill chunk, later correction possible.
- src/vllm/v1/core/kv_cache_manager.py:558-614: needed/free/reserved/watermark capacity, adopt computed blocks, allocate new blocks, return block handles.
- src/vllm/v1/core/sched/output.py:41-54,138-152,232-272: new vs cached metadata, block IDs, token map, ancillary fields.

# Assumptions and scope
Example uses B=I=8, A decode needs 1, B already-running prefill needs 3, C waiting prompt needs 10; C receives 4 and remains running with 6 prompt tokens pending. Assumes sufficient KV capacity, no prefix hits, no spec or placeholders, optional cap disabled, chunking enabled, no specialized gates. These values are illustrative, not source defaults.
Main diagram summarizes text scheduling; multimodal, Mamba, distributed throttling, connectors, spec and asynchronous details appear only as constraints/ancillary metadata. Allocation success may return no newly needed blocks when existing capacity suffices. Freeing ownership does not imply erasing reusable prefix-cache content. Subsequent step does not promise C all 6 tokens.
