# Source grounding

Source: src/PINNED.txt identifies NVIDIA/Megatron-LM commit e998be072d22ff57b4b49899819a1a153f4f3dc9. All line references below are to src/megatron/core/parallel_state.py.

- Default order is tp-cp-ep-dp-pp (638), with CP, EP, GTP rematerialization defaults 1 (628–633), rank offset 0 (644).
- DP size is world_size divided by TP×PP×CP×GTP_remat (849–859), yielding 2.
- RankGenerator creates ordered sizes (513–537), masks named axes (539–565), and mixed-radix prefix-product strides enumerate ranks (268–375). With singleton axes suppressed this yields r=t+2d+4p.
- Decoder generator uses EP=1 and the computed DP (891–902). GTP insertion is singleton in this example.
- TP groups vary t (1226–1235): {0,1}, {2,3}, {4,5}, {6,7}, {8,9}, {10,11}, {12,13}, {14,15}.
- PP groups vary p (1302–1323): {0,4,8,12}, {1,5,9,13}, {2,6,10,14}, {3,7,11,15}.
- DP groups vary d (1115–1131): {0,2}, {1,3}, {4,6}, {5,7}, {8,10}, {9,11}, {12,14}, {13,15}.
- MP groups vary TP, GTP_remat, PP, reducing to TP×PP here (1204–1218): {0,1,4,5,8,9,12,13}, {2,3,6,7,10,11,14,15}.
- Default word-embedding membership selects first and last PP ranks (580–586); group creation occurs for each PP group (1331–1340): {0,12}, {1,13}, {2,14}, {3,15}. Ranks 4–11 have no such membership.

## Explicit assumptions and presentation choices

User specifies 16 GPUs on two nodes, eight per node. The diagram assumes launcher ranks are contiguous by node: Node 0=0–7, Node 1=8–15. The cited process-group code does not guarantee host placement. Assume default rank order, default embedding callback, GTP_remat=1, rank_offset=0, and no overrides. Group names TP0 etc. are diagram identifiers enumerated from the derived groups. Position-embedding and other additional groups are outside the requested families. No reference image, prior diagram, grader, or answer key was consulted.
