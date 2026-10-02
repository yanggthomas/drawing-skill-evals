Use case: infographic-diagram
Create ONE original high-resolution landscape raster technical diagram, clean white background, precise flat academic diagram, generous spacing, readable typography. Title: "vLLM V1: one mixed batch → paged attention". Subtitle: "Concrete example • block size 16 • causal decoder • one GPU • no speculative decoding or cascade". Use a coherent flow with 4 numbered panels; teal for request A, amber for request B; purple for metadata; grey for cached history. Draw data structures, short formulas, labelled arrows, and a cache schematic, not a text essay.

Panel 1 "Schedule → flatten" upper left. Table:
request | work | computed | scheduled | physical blocks
A | decode | 5 | 1 | [7]
B | chunked prefill | 14 | 3 | [2, 9]
Explain "Illustrative values; rows in current batch order."
Below draw 4 adjacent token cells grouped A then B: "A5 | B14 | B15 | B16".
Aligned rows: "req_indices [0, 1, 1, 1]"; "query_pos [0, 0, 1, 2]"; "positions [5, 14, 15, 16]".
Small formula "positions = computed[req_indices] + query_pos".
Caption "Gather input_ids from token_ids[request, position]". Cite "gpu_model_runner.py:1975–2011".

Panel 2 "Build attention metadata" upper right.
Draw "query_start_loc = [0, 1, 4]" with boundary pointers to groups A:[0:1], B:[1:4] in flattened tokens. Caption "0 + cumulative scheduled counts".
Draw "seq_lens = [6, 17]" caption "computed + scheduled = full KV lengths".
Draw block table as 2 rows and 2 logical block columns: A row "7 | —"; B row "2 | 9". Caption "Logical block index → physical block ID; — unused".
Note "Block IDs appended to rows, then copied to GPU".
Draw slot formula "slot = block_table[request, position // 16] × 16 + position % 16".
Aligned slot row "slot_mapping = [117, 46, 47, 144]".
Small highlighted example "B16 → logical block 1 → physical block 9 → slot 144".
Cite "gpu_model_runner.py:2060–2076, 2175–2188" and "block_table.py:173–177, 231–232, 445–478".

Panel 3 "Write new K/V" lower left, fed by flattened tokens and slot_mapping.
A small conceptual box "Layer produces Q, K, V in flattened order" branches Q to Panel 4 and K,V to "do_kv_cache_update → reshape_and_cache_flash".
Arrow labelled "scatter by slot_mapping" to a paged KV cache schematic showing separate physical blocks 7, 2, 9 with exact summaries:
"block 7: A0…A4 cached | A5 NEW at offset 5"
"block 2: B0…B13 cached | B14, B15 NEW at offsets 14, 15"
"block 9: B16 NEW at offset 0"
Each item means a K/V pair; unused slots pale. Do NOT draw 16 individual cells; compressed strips with ellipses are clearer. Label "K and V cache views; both receive the same slot addresses".
Caption "Cache update is separate from forward in this revision".
Cite "flash_attn.py:365, 1511–1545".

Panel 4 "Read paged K/V + attend" lower right, fed by Q, cache, and three metadata arrows. Clearly label arrow inputs:
"query_start_loc → cu_seqlens_q"
"seq_lens → seqused_k"
"block_table → page lookup"
Kernel box "FlashAttention varlen" with secondary text "_FA4_DENSE_ATTENTION_KERNEL → flash_attn_varlen_func".
Q input labelled "Q [4, Hq, D]"; cache inputs labelled "paged K, V".
Show a small causal visibility table:
query | visible positions
A5 | A0…A5
B14 | B0…B14
B15 | B0…B15
B16 | B0…B16
Output 4 cells "O(A5) | O(B14) | O(B15) | O(B16)" caption "Output keeps flattened query order".
Cite "flash_attn.py:114–116, 1331–1337, 1454–1468".
Bottom takeaway: "slot_mapping writes new tokens; block_table + seq_lens locate readable history; query_start_loc separates requests."
Small footer "Source: vLLM 4c2d277643e2 • numeric batch is illustrative".
Accuracy constraints: query_start_loc has 3 entries, not 4. seq_lens are 6 and 17, not scheduled counts. Never cross-attend A and B. B14 cannot see B15 or B16 even though all new K/V are written first. Physical block IDs are not contiguous logical sequence positions. Do not depict slot_mapping as the read lookup or claim forward itself updates cache. One PNG, no references, no decorative mascots, no fake logos.