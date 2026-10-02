Use case: infographic-diagram
Create one original high-resolution landscape raster technical architecture diagram, crisp readable typography, white background, restrained group colors, generous spacing, no decorative imagery. Title: "Megatron-Core process groups · 16 GPUs". Subtitle: "TP = 2 · PP = 4 · DP = 2 · CP = EP = GTP_remat = 1".
Build the main left portion as an exact four-column by four-row rank lattice. Columns, left to right, are "(d=0, t=0)", "(d=0, t=1)", "(d=1, t=0)", "(d=1, t=1)". Rows top to bottom labeled "p=0", "p=1", "p=2", "p=3". Rank labels in each row are exactly:
p=0: 0, 1, 2, 3
p=1: 4, 5, 6, 7
p=2: 8, 9, 10, 11
p=3: 12, 13, 14, 15.
Every rank is a clear GPU tile labeled "rank N". Enclose top two rows in a broad horizontal enclosure "Node 0 · ranks 0–7"; enclose bottom two rows separately "Node 1 · ranks 8–15". State clearly under lattice: "Node placement assumes contiguous launcher ranks; process-group code does not assign hosts."
Use two pale vertical background bands to encode model-parallel replicas: left two columns MP0, right two columns MP1. Use small horizontal brackets below each adjacent tile pair for TP0 through TP7 in row-major order. Four thin vertical lines linking ranks in each column show PP0 through PP3. Embedding endpoints in first and last rows have a small gold ring; an unobtrusive key explains first/last PP ranks. Avoid arrows implying compute direction: these are group memberships.
On right, provide a beautifully aligned compact group directory, exact text with each set on its own line and clear family headers. The directory is essential and must remain readable:
"Tensor parallel · vary t"
"TP0 {0,1}    TP1 {2,3}"
"TP2 {4,5}    TP3 {6,7}"
"TP4 {8,9}    TP5 {10,11}"
"TP6 {12,13}  TP7 {14,15}"
"Pipeline parallel · vary p"
"PP0 {0,4,8,12}"
"PP1 {1,5,9,13}"
"PP2 {2,6,10,14}"
"PP3 {3,7,11,15}"
"Data parallel · vary d"
"DP0 {0,2}    DP1 {1,3}"
"DP2 {4,6}    DP3 {5,7}"
"DP4 {8,10}   DP5 {9,11}"
"DP6 {12,14}  DP7 {13,15}"
"Model parallel · vary t and p"
"MP0 {0,1,4,5,8,9,12,13}"
"MP1 {2,3,6,7,10,11,14,15}"
"Embedding · first and last in each PP group"
"E0 {0,12}   E1 {1,13}"
"E2 {2,14}   E3 {3,15}"
"Ranks 4–11 have no embedding-group membership."
Bottom rule strip: "Default order: tp-cp-ep-dp-pp → effective tp-dp-pp" and large equation "r = t + 2d + 4p". Define "t ∈ {0,1}, d ∈ {0,1}, p ∈ {0,1,2,3}". Explain "A group's named axes vary; all other coordinates stay fixed. TP changes fastest. DP = 16/(2×4) = 2."
Tiny but legible source footer: "Source: megatron/core/parallel_state.py @ e998be072d22 | rank rule 268–375, 539–565; defaults 628–644; DP 849–859; TP 1226; PP 1302; MP 1204–1218; embedding 580–586, 1331–1340."
Constraints: exact ranks and group sets; do not imply MP is contiguous ranks 0–7; MP spans nodes. No singleton context/expert groups or position-embedding groups are needed. Group labels TP0/PP0/DP0/MP0/E0 are diagram identifiers. Render this as one clean comprehensive image, with no clipping, tiny illegible body labels, extra ranks, or invented edges.