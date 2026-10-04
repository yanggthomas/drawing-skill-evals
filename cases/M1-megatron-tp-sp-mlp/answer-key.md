# M1 answer key — a tensor-parallel + sequence-parallel MLP block in Megatron-Core

Paths are relative to `src/megatron/core/`; `L` = `tensor_parallel/layers.py`, `MP` = `tensor_parallel/mappings.py`, `MLP` = `transformer/mlp.py`. Shapes use s = sequence, b = micro-batch, h = hidden, F = ffn hidden size (2× for gated units), p = tensor-parallel size. Each fact describes a mechanism a diagram can show; the correctness grader's rubric includes the same 8 facts without the line references.

1. **Sequence-sharded input.** With sequence parallelism, the MLP input on each rank is sequence-sharded: `[s/p, b, h]`. The full `[s, b, h]` exists only after an all-gather along the first (sequence) dimension (`L:724-730`).
2. **fc1 is column-parallel.** `linear_fc1` is a `ColumnParallelLinear` whose weight is split along its output dimension: each rank holds `F/p` output columns (`F` doubled for gated units such as SwiGLU). It is built with `gather_output=False` (`L:1150`, `MLP:207-226`).
3. **Forward all-gather before fc1.** In the forward pass, fc1 all-gathers the sequence-sharded input to `[s, b, h]` and then runs the GEMM, giving `[s, b, F/p]` per rank. With sequence parallelism no copy-to-TP region is used (`L:724-734`, `L:1340-1348`, `MLP:263-265`).
4. **Local activation.** The activation (e.g. GeLU/SwiGLU) runs locally on `[s, b, F/p]` with no communication (`MLP:268-372`).
5. **fc2 is row-parallel.** `linear_fc2` is a `RowParallelLinear` with `input_is_parallel=True`: its weight is split along the input dimension (`F/p` per rank), and each rank produces a partial `[s, b, h]` (`L:1545`, `MLP:242-250`, `L:1680-1690`).
6. **Forward reduce-scatter after fc2.** fc2's partial outputs are reduce-scattered along the sequence dimension: summed across ranks and re-sharded to `[s/p, b, h]`. Without sequence parallelism this would be an all-reduce instead (`L:1698-1703`, `MP:359-374`).
7. **Backward of fc2's reduce-scatter.** The backward of that reduce-scatter is an all-gather of the output gradient along the sequence dimension, back to `[s, b, h]` (`MP:376-386`).
8. **Backward of fc1.** In fc1's backward, the saved sequence-sharded input is all-gathered again (asynchronously) to compute the weight gradient. The input gradient `grad_output @ W` is reduce-scattered along the sequence dimension back to `[s/p, b, h]` (`L:767-781`, `L:800-810`, `L:901-903`).
