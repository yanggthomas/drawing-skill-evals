# Grounding

Only this case's prompt.md and src files were read, plus imagegen SKILL.md. Built-in image generation; one call; no reference image.

Commit: 4c2d277643e217344056e1d2c42115d5f005912f (src/PINNED.txt).

- src/vllm/v1/worker/gpu_model_runner.py:1971 copies block table to GPU; :1975 repeats request indices by scheduled count; :1979–1987 computes cumulative counts, per-request query positions, and absolute positions; :1998–2011 gathers flattened input token IDs.
- gpu_model_runner.py:2060–2066 builds cumulative query_start_loc with initial zero and GPU copy. :2072–2076 adds computed and scheduled counts on CPU; :2175–2182 constructs GPU positions and seq_lens. :2184–2188 computes slot mapping.
- src/vllm/v1/worker/block_table.py:173 stores appended physical IDs, :175–177 initializes a row; :231–232 commits rows to GPU. :445–478 obtains per-request token range and calculates physical slot. With CP world size one and equal kernel/cache block sizes, simplifies to block_table[r,p//B]*B+p%B.
- src/vllm/v1/attention/backends/flash_attn.py:355–363 generally supports block sizes multiple of 16. :365 declares forward_includes_kv_cache_update=False. :1511–1545 separate update scatters K/V through reshape_and_cache_flash and slot_mapping. Cache split is at :1527.
- flash_attn.py:1331–1337 aliases query_start_loc, seq_lens and block_table. :1454–1468 calls paged attention with Q, cached K/V, cumulative query boundaries, used KV lengths, causal flag and block table. :114–116 wrapper invokes flash_attn_varlen_func. gpu_model_runner.py:2438 sets causal=True.

## Concrete example and assumptions

Illustrative current request order A,B; one GPU, CP=1, ordinary causal decoder, no cascade, no speculative decoding, no sliding window or hybrid block conversion. Block size 16; A decode computed=5 scheduled=1, physical row [7]; B chunked prefill computed=14 scheduled=3, physical row [2,9]. No allocation algorithm is claimed; these are example pre-existing/appended block IDs. Only valid rows/tokens shown, no padding.

Flattened symbols A5,B14,B15,B16 represent tokens by request and absolute position, not literal vocabulary IDs. req_indices=[0,1,1,1], query_pos=[0,0,1,2], positions=[5,14,15,16], query_start_loc=[0,1,4], seq_lens=[6,17]. Slot arithmetic: 7*16+5=117; 2*16+14=46; 2*16+15=47; 9*16+0=144. Old K/V holds A0..A4 and B0..B13. Causal decoder contract yields visible sets A0..A5; B0..B14; B0..B15; B0..B16. Projection implementation is not included in supplied sources: layer-produces-QKV is a conceptual boundary, grounded only in backend Q,K,V arguments. Full kernel internals are not vendored, so causal visibility is inferred from passed causal contract, not inspected kernel implementation.
