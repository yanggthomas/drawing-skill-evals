# M2 answer key — how vLLM V1 flattens a mixed prefill + decode batch into attention metadata

Paths are relative to `src/vllm/v1/`; `R` = `worker/gpu_model_runner.py`, `BT` = `worker/block_table.py`, `FA` = `attention/backends/flash_attn.py`. Each fact describes a mechanism a diagram can show; the correctness grader's rubric includes the same 9 facts without the line references.

1. **One flat token array.** The scheduled tokens of all requests, prefill chunks and decode tokens alike, are concatenated into one 1-D token array. `req_indices` maps each flat token back to its request (`np.repeat`, e.g. `[2,5,3]` → `[0,0,1,1,1,1,1,2,2,2]`) (`R:1973-1975`).
2. **Per-request offsets.** `cu_num_tokens = cumsum(num_scheduled_tokens)`, and `query_pos` is each token's index within its request's slice (`R:1977-1981`, `R:1735-1750`).
3. **Positions continue from computed tokens.** `positions = num_computed_tokens[req] + query_pos`. A prefill chunk's positions continue from what earlier steps already computed, and a decode token's position equals its request's computed length (`R:1984-1987`).
4. **Input ids gathered.** Input ids are gathered from the per-request token table with `token_indices = positions + req_idx * max_model_len` (`R:1998-2011`).
5. **query_start_loc.** `query_start_loc = [0, cu_num_tokens...]`, of length num_reqs+1 (padded to stay non-decreasing), marks where each request's queries start in the flat array. Logits are taken at each request's last token, `query_start_loc[1:] - 1` (`R:2060-2066`, `R:2231`).
6. **seq_lens.** `seq_lens = num_computed_tokens + num_scheduled_tokens` per request: the full context length including this step's new tokens (`R:2180-2183`).
7. **block_table.** `block_table` holds one row of physical KV block ids per request. Each step it is extended with the `new_block_ids` from the `SchedulerOutput`, or replaced when a request resumes from preemption (`R:1436-1447`, `BT:157-177`).
8. **slot_mapping.** Each token's KV-cache slot is `block_table[req][pos // block_size] * block_size + pos % block_size`, computed on the GPU per flat token (`R:2184-2188`, `BT:201-229`, `BT:465-478`).
9. **Write then read in one kernel call.** The attention backend first scatters the new K/V into the paged cache at `slot_mapping` (`reshape_and_cache_flash`). It then runs one varlen attention call with `cu_seqlens_q = query_start_loc`, `seqused_k = seq_lens` and `block_table`, so prefill chunks and decode tokens are processed together in one kernel (`FA:1511-1545`, `FA:1330-1335`, `FA:1454-1479`).
