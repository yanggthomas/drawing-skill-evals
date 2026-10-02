# Grounding

Only prompt.md, src/** and the authorized imagegen skill were read. No reference diagram or other case was used. One fresh built-in image generation call; no edits or regeneration.

Pinned source: src/PINNED.txt:3 gives commit 4c2d277643e217344056e1d2c42115d5f005912f. Paths below are relative to src/.

| Diagram fact | Source |
|---|---|
| AsyncLLM owns renderer, InputProcessor, OutputProcessor and asynchronous multiprocess engine client | vllm/v1/engine/async_llm.py:154–188 |
| Input conversion and output conversion contracts | vllm/v1/engine/async_llm.py:156–167 |
| Engine runs in background process; launch_core_engines | vllm/v1/engine/async_llm.py:175; vllm/v1/engine/core_client.py:674–684 |
| Frontend ROUTER request socket and PULL result socket | vllm/v1/engine/core_client.py:653–663 |
| Engine DEALER request socket and PUSH result socket | vllm/v1/engine/core.py:1771–1776,1875–1879 |
| Msgpack encoding / EngineCoreOutputs decoding | vllm/v1/engine/core_client.py:705–706 |
| ADD EngineCoreRequest, UTILITY, ABORT payloads | vllm/v1/engine/core.py:1822–1854 |
| Executor, scheduler and StructuredOutputManager live in EngineCore | vllm/v1/engine/core.py:139–176; EngineCoreProc inherits EngineCore at 1088 |
| Engine I/O threads and queues are not separate processes | vllm/v1/engine/core.py:1172–1195 |
| World size TP × PP × PCP; one WorkerProc per local rank | vllm/v1/executor/multiproc_executor.py:125–130,189–204 |
| Each worker is a separate process | vllm/v1/executor/multiproc_executor.py:602–603,739–750 |
| MessageQueue comes from shm_broadcast; broadcast handle to workers | vllm/v1/executor/multiproc_executor.py:31,164–170,200 |
| Single-node workers attach shared broadcast queue and each creates its own response queue | vllm/v1/executor/multiproc_executor.py:612–620 |
| Broadcast RPC tuple contains method, args, kwargs and reply rank; response is status/result | vllm/v1/executor/multiproc_executor.py:418–444 |
| execute_model carries SchedulerOutput; sample_tokens carries GrammarOutput; selected output rank | vllm/v1/executor/multiproc_executor.py:340–364 |
| WorkerProc constructs WorkerWrapperBase and initializes worker/device/model | vllm/v1/executor/multiproc_executor.py:652–682 |
| GPU worker maps local rank to CUDA device and constructs GPUModelRunner | vllm/v1/worker/gpu_worker.py:479–496,536–557 |
| Model load and KV cache initialization delegated to model runner | vllm/v1/worker/gpu_worker.py:572,842 |
| Distributed backend and TP group; custom all-reduce option | vllm/v1/worker/gpu_worker.py:1591,1602,1610–1624 |
| READY and parent-death pipes, readiness includes response queue handle | vllm/v1/executor/multiproc_executor.py:718–721,920–928 |

## Assumptions and source limits

Illustration chooses one frontend, DP=PP=PCP=1, CUDA serving and T tensor-parallel workers. Model shards are a semantic inference from tensor-parallel configuration; model implementation is outside this source slice. GPU memory tile is a resource owned by each worker, not a process. NCCL is the declared default backend, but actual platform backend is passed at gpu_worker.py:496; custom all-reduce is configurable and not every collective must use NCCL. Local IPC endpoints are explicitly an assumption: core_client.py:665–666 mentions both TCP and IPC, while get_engine_zmq_addresses is not vendored. MessageQueue implementation is not vendored, so SHM is grounded in its import and input_shm_handle usage; exact socket fallback internals are not asserted. Renderer/tokenizer implementation, scheduler internals, concrete model runner implementation and HTTP server implementation are not available; no HTTP transport is drawn. Optional DP, multimodal tensor IPC, fault tolerance, helper/resource-tracker processes and runtime-dependent threads are outside the chosen overview. Model result uses selected output rank; no numeric output rank is asserted because its inherited implementation is absent.
