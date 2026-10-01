---
type: llm
focus: { source: file, path: out/tp-sp-mlp.png }
---

You are grading a diagram (the attached PNG) that is meant to explain a tensor-parallel + sequence-parallel MLP block in Megatron-Core. Judge only what the picture shows. Do not credit anything you would have to infer from code that is not drawn. Exact identifiers are not required when the mechanism is drawn unambiguously.

Reference facts:

1. **Sequence-sharded input.** With sequence parallelism, the MLP input on each rank is sequence-sharded: `[s/p, b, h]`. The full `[s, b, h]` exists only after an all-gather along the first (sequence) dimension.
2. **fc1 is column-parallel.** `linear_fc1` is a `ColumnParallelLinear` whose weight is split along its output dimension: each rank holds `F/p` output columns (`F` doubled for gated units such as SwiGLU). It is built with `gather_output=False`.
3. **Forward all-gather before fc1.** In the forward pass, fc1 all-gathers the sequence-sharded input to `[s, b, h]` and then runs the GEMM, giving `[s, b, F/p]` per rank. With sequence parallelism no copy-to-TP region is used.
4. **Local activation.** The activation (e.g. GeLU/SwiGLU) runs locally on `[s, b, F/p]` with no communication.
5. **fc2 is row-parallel.** `linear_fc2` is a `RowParallelLinear` with `input_is_parallel=True`: its weight is split along the input dimension (`F/p` per rank), and each rank produces a partial `[s, b, h]`.
6. **Forward reduce-scatter after fc2.** fc2's partial outputs are reduce-scattered along the sequence dimension: summed across ranks and re-sharded to `[s/p, b, h]`. Without sequence parallelism this would be an all-reduce instead.
7. **Backward of fc2's reduce-scatter.** The backward of that reduce-scatter is an all-gather of the output gradient along the sequence dimension, back to `[s, b, h]`.
8. **Backward of fc1.** In fc1's backward, the saved sequence-sharded input is all-gathered again (asynchronously) to compute the weight gradient. The input gradient `grad_output @ W` is reduce-scattered along the sequence dimension back to `[s/p, b, h]`.

For each fact, decide: SHOWN (drawn correctly), ABSENT (not drawn), or CONTRADICTED (drawn in a way that conflicts with the fact). Examples of a contradiction: the full [s, b, h] activation is kept between blocks; fc1 is row-parallel or fc2 column-parallel; an all-reduce is used in the forward pass with sequence parallelism.

PASS if at least 6 of the 8 facts are SHOWN and none is CONTRADICTED.
FAIL otherwise. Begin your explanation by listing the SHOWN / ABSENT / CONTRADICTED verdict for each fact number.
