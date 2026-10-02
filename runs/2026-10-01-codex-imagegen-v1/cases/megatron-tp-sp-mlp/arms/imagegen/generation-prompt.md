Use case: scientific-educational
Create one original, high-resolution landscape raster technical diagram on a white background, readable scientific typography. Title: "Megatron-Core MLP: tensor + sequence parallelism". Subtitle: "One TP rank r • p ranks • standard dense, non-gated MLP • sequence_parallel=True".
Use a carefully aligned two-row flow layout. Forward row flows left to right; backward row flows right to left directly beneath corresponding forward stages. Blue tensors, dark navy local operations, orange collective communication. Distinguish sequence shards, feature shards, and partial sums with precise labels. No decorative hardware or logos.

Define a compact legend: "s: full sequence length | b: batch | h: model width | f: FFN hidden size | p: TP size". "Tensor order [sequence, batch, feature]; weights use PyTorch [out, in]". Assume s and f divisible by p.

FORWARD, left to right, all elements and shapes mandatory:
1. X_r [s/p, b, h], label "sequence shard".
2. orange "All-gather (sequence)" arrow, resulting X [s, b, h], label "replicated".
3. fc1 "ColumnParallelLinear" with weight W1_r [f/p, h]. Output Z_r [s, b, f/p].
4. activation φ, output A_r [s, b, f/p]; label "feature shard; local activation".
5. fc2 "RowParallelLinear" with W2_r [h, f/p]. Output U_r [s, b, h], distinctly label "partial sum across TP".
6. orange "Reduce-scatter (SUM, sequence)" yielding Y_r [s/p, b, h], label "sequence shard".
Show formulas near operations: Z_r = X W1_rᵀ; A_r = φ(Z_r); U_r = A_r W2_rᵀ. Ignore biases in formulas.

BACKWARD, right to left:
Start under Y_r with dY_r [s/p, b, h].
orange "All-gather (sequence)" yields dY [s, b, h], replicated.
Local "fc2 backward" yields dA_r = dY W2_r, shape [s, b, f/p]. A small branch gives dW2_r [h, f/p], computed locally from dY and saved A_r.
"activation backward" gives dZ_r [s, b, f/p].
"fc1 backward" gives dX_partial_r = dZ_r W1_r, shape [s, b, h], partial sum.
orange "Reduce-scatter (SUM, sequence)" gives dX_r [s/p, b, h].
Near fc1 backward include a separate clearly dashed side branch, not on the dX main path: "Saved X_r [s/p,b,h] → All-gather (sequence) → X [s,b,h] → fc1 weight gradient". Endpoint dW1_r [f/p,h], also receiving dZ_r. This is an additional backward collective for weight-gradient computation. Label "Re-gather saved input for dW1; may overlap dgrad". No all-reduce anywhere on these standard SP paths.

Small bottom notes:
"Main path assumes trainable weights, immediate weight gradients, no expert or weight-rematerialization path."
"Bias omitted for clarity; fc2 bias is returned separately by MLP."
"Gated variant: fc1 weight [2f/p,h], pre-activation [s,b,2f/p]; gate reduces to [s,b,f/p]."
"Collectives use the TP group and sequence dimension 0; no feature all-gather between fc1 and fc2."
Compact source footer:
"Source: Megatron-LM e998be0 | mlp.py:221–254,265–377 | layers.py:724–734,768–811,1150–1161,1545–1555,1681–1701 | mappings.py:359–383"
Prioritize exact shapes and arrow directions. Ensure no arrows mistakenly attach the weight gradient branch to the main activation derivative chain. Leave whitespace and keep small notes legible. Draw a technical diagram, not a screenshot or mockup.
