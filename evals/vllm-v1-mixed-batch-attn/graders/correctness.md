---
type: llm
focus: { source: file, path: out/mixed-batch-attn.png }
---

You are grading a diagram (the attached PNG) that is meant to explain how vLLM V1 flattens a mixed prefill + decode batch into attention metadata. Judge only what the picture shows. Do not credit anything you would have to infer from code that is not drawn. Exact identifiers are not required when the mechanism is drawn unambiguously.

Reference facts:

1. **One flat token array.** The scheduled tokens of all requests, prefill chunks and decode tokens alike, are concatenated into one 1-D token array. `req_indices` maps each flat token back to its request (`np.repeat`, e.g. `[2,5,3]` → `[0,0,1,1,1,1,1,2,2,2]`).
2. **Per-request offsets.** `cu_num_tokens = cumsum(num_scheduled_tokens)`, and `query_pos` is each token's index within its request's slice.
3. **Positions continue from computed tokens.** `positions = num_computed_tokens[req] + query_pos`. A prefill chunk's positions continue from what earlier steps already computed, and a decode token's position equals its request's computed length.
4. **Input ids gathered.** Input ids are gathered from the per-request token table with `token_indices = positions + req_idx * max_model_len`.
5. **query_start_loc.** `query_start_loc = [0, cu_num_tokens...]`, of length num_reqs+1 (padded to stay non-decreasing), marks where each request's queries start in the flat array. Logits are taken at each request's last token, `query_start_loc[1:] - 1`.
6. **seq_lens.** `seq_lens = num_computed_tokens + num_scheduled_tokens` per request: the full context length including this step's new tokens.
7. **block_table.** `block_table` holds one row of physical KV block ids per request. Each step it is extended with the `new_block_ids` from the `SchedulerOutput`, or replaced when a request resumes from preemption.
8. **slot_mapping.** Each token's KV-cache slot is `block_table[req][pos // block_size] * block_size + pos % block_size`, computed on the GPU per flat token.
9. **Write then read in one kernel call.** The attention backend first scatters the new K/V into the paged cache at `slot_mapping` (`reshape_and_cache_flash`). It then runs one varlen attention call with `cu_seqlens_q = query_start_loc`, `seqused_k = seq_lens` and `block_table`, so prefill chunks and decode tokens are processed together in one kernel.

For each fact, decide: SHOWN (drawn correctly), ABSENT (not drawn), or CONTRADICTED (drawn in a way that conflicts with the fact). Examples of a contradiction: prefill and decode tokens run as separate batches or kernels; slot_mapping is per request rather than per token; seq_lens counts only the new tokens.

PASS if at least 7 of the 9 facts are SHOWN and none is CONTRADICTED.
FAIL otherwise. Begin your explanation by listing the SHOWN / ABSENT / CONTRADICTED verdict for each fact number.
