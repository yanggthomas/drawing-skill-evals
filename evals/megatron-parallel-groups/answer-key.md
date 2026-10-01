# A3 answer key — how Megatron-Core partitions 16 GPU ranks into tensor-, pipeline- and data-parallel groups (TP=2, PP=4, DP=2, 2 nodes × 8 GPUs)

Paths are relative to `src/megatron/core/`; `PS` = `parallel_state.py`. The scenario is the one in the `initialize_model_parallel` docstring: 16 ranks g0–g15, TP=2, PP=4, so DP=2, CP=EP=1, ranks 0–7 on node 0 and 8–15 on node 1. Each fact describes a mechanism a diagram can show; the correctness grader's rubric includes the same 8 facts without the line references.

1. **Rank order and DP size.** Ranks are laid out in the order `tp-cp-ep-dp-pp` (TP varies fastest), and DP = world / (TP·PP·CP) = 16 / 8 = 2 (`PS:638`, `PS:859`, `PS:893-901`).
2. **Rank formula.** With CP = EP = 1 a rank decomposes as `rank = tp_rank + dp_rank·2 + pp_rank·4` (orthogonal groups from `generate_masked_orthogonal_rank_groups`) (`PS:268-300`, `PS:487-578`).
3. **TP groups.** 8 tensor-parallel groups of adjacent pairs: [0,1], [2,3], …, [14,15] (`PS:796-797`, `PS:1226-1234`).
4. **DP groups.** 8 data-parallel groups: [0,2], [1,3], [4,6], [5,7], [8,10], [9,11], [12,14], [13,15] (`PS:794-795`, `PS:1115-1129`).
5. **PP groups.** 4 pipeline-parallel groups with stride 4: [0,4,8,12], [1,5,9,13], [2,6,10,14], [3,7,11,15]; each spans both nodes (`PS:798-799`, `PS:1302-1322`).
6. **Node placement.** Ranks 0–7 sit on node 0 and 8–15 on node 1, so every TP group and every DP group stays inside one node while PP groups cross the node boundary (`PS:800-803`).
7. **Model-parallel groups.** The model-parallel group is all TP×PP ranks that share a DP rank, e.g. [0,1,4,5,8,9,12,13] and [2,3,6,7,10,11,14,15] (`PS:1209-1217`).
8. **Embedding group.** The embedding group of each pipeline is its first and last stage, e.g. [0,12], [1,13], [2,14], [3,15] (`PS:580-587`, `PS:1330-1339`).
