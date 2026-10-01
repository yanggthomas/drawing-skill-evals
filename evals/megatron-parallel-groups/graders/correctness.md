---
type: llm
focus: { source: file, path: out/parallel-groups.png }
---

You are grading a diagram (the attached PNG) that is meant to explain how Megatron-Core partitions 16 GPU ranks into tensor-, pipeline- and data-parallel groups (TP=2, PP=4, DP=2, 2 nodes × 8 GPUs). Judge only what the picture shows. Do not credit anything you would have to infer from code that is not drawn. Exact identifiers are not required when the mechanism is drawn unambiguously.

Reference facts:

1. **Rank order and DP size.** Ranks are laid out in the order `tp-cp-ep-dp-pp` (TP varies fastest), and DP = world / (TP·PP·CP) = 16 / 8 = 2.
2. **Rank formula.** With CP = EP = 1 a rank decomposes as `rank = tp_rank + dp_rank·2 + pp_rank·4` (orthogonal groups from `generate_masked_orthogonal_rank_groups`).
3. **TP groups.** 8 tensor-parallel groups of adjacent pairs: [0,1], [2,3], …, [14,15].
4. **DP groups.** 8 data-parallel groups: [0,2], [1,3], [4,6], [5,7], [8,10], [9,11], [12,14], [13,15].
5. **PP groups.** 4 pipeline-parallel groups with stride 4: [0,4,8,12], [1,5,9,13], [2,6,10,14], [3,7,11,15]; each spans both nodes.
6. **Node placement.** Ranks 0–7 sit on node 0 and 8–15 on node 1, so every TP group and every DP group stays inside one node while PP groups cross the node boundary.
7. **Model-parallel groups.** The model-parallel group is all TP×PP ranks that share a DP rank, e.g. [0,1,4,5,8,9,12,13] and [2,3,6,7,10,11,14,15].
8. **Embedding group.** The embedding group of each pipeline is its first and last stage, e.g. [0,12], [1,13], [2,14], [3,15].

For each fact, decide: SHOWN (drawn correctly), ABSENT (not drawn), or CONTRADICTED (drawn in a way that conflicts with the fact). Examples of a contradiction: TP groups drawn across nodes; PP groups drawn as adjacent ranks; DP size other than 2.

PASS if at least 6 of the 8 facts are SHOWN and none is CONTRADICTED.
FAIL otherwise. Begin your explanation by listing the SHOWN / ABSENT / CONTRADICTED verdict for each fact number.
