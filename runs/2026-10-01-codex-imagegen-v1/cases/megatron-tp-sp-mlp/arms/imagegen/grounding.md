# Source grounding

Source pin: src/PINNED.txt identifies Megatron-LM commit e998be072d22ff57b4b49899819a1a153f4f3dc9. Only the case prompt and vendored src files were inspected.

- src/megatron/core/transformer/mlp.py:221-254 configures fc1 with gather_output=False and fc2 with input_is_parallel=True, skip_bias_add=True.
- src/megatron/core/transformer/mlp.py:265-272,324-366,375-379 establishes fc1 → activation → fc2. Ordinary activation preserves per-rank feature width.
- src/megatron/core/tensor_parallel/layers.py:1150-1161 stores column-parallel weights as [output_size/p,input_size], giving W1_r [f/p,h].
- src/megatron/core/tensor_parallel/layers.py:1545-1555 stores row-parallel weights as [output_size,input_size/p], giving W2_r [h,f/p].
- src/megatron/core/tensor_parallel/layers.py:724-734 gathers dimension 0 of fc1 input, taking [s/p,b,h] to [s,b,h] before linear.
- src/megatron/core/tensor_parallel/layers.py:1681-1701 performs fc2 local linear with sequence_parallel=False internally, then reduce_scatter_to_sequence_parallel_region. Its local [s,b,h] is a partial sum; the result has [s/p,b,h].
- src/megatron/core/tensor_parallel/mappings.py:359-383 defines forward reduce-scatter and backward all-gather, grounding dY_r [s/p,b,h] → dY [s,b,h].
- src/megatron/core/tensor_parallel/layers.py:784 computes grad_input=grad_output.matmul(weight), grounding fc2 dA [s,b,f/p] and fc1 dX partial [s,b,h].
- src/megatron/core/tensor_parallel/layers.py:768-781 re-gathers saved input for fc1 weight gradients; :786-793 waits and prepares weight-gradient inputs; :801-811 reduce-scatters fc1 input gradient.
- src/megatron/core/tensor_parallel/layers.py:894 computes grad_weight=grad_output.t().matmul(total_input), after preparation; contractions over flattened sequence×batch produce each weight's shape.
- src/megatron/core/tensor_parallel/layers.py:1705-1711 returns fc2 bias separately when skip_bias_add=True.
- src/megatron/core/transformer/mlp.py:203-209 doubles fc1 width for GLU; :338-349 chunks its last dimension and multiplies activation by the second part, returning width f/p.

Assumptions explicitly represented: ordinary dense non-expert MLP using supplied ColumnParallelLinear/RowParallelLinear implementation, trainable weights, immediate weight gradients, no GTP weight rematerialization, no per-token scaling, non-gated main path, biases omitted. s and f divisible by p, p>1. f denotes config.ffn_hidden_size. MLP submodules are injectable, so this is the standard tensor-parallel linear instantiation rather than a claim about every possible builder. Tensor shapes are derived from the code's partition sizes and GEMMs. The linear equations are compact matrix notation for per-token GEMMs.
