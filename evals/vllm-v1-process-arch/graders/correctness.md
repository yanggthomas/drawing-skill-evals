---
type: llm
focus: { source: file, path: out/process-arch.png }
---

You are grading a diagram (the attached PNG) that is meant to explain the process and component architecture of vLLM V1 serving (single node, tensor parallel, multiprocess executor). Judge only what the picture shows. Do not credit anything you would have to infer from code that is not drawn. Exact identifiers are not required when the mechanism is drawn unambiguously.

Reference facts:

1. **Frontend process holds AsyncLLM.** The serving frontend (the API server's process) holds `AsyncLLM`, the `EngineClient` that the HTTP layer calls.
2. **Pre- and post-processing stay in the frontend.** Inside `AsyncLLM` sit the `InputProcessor` (tokenization / multimodal preprocessing) and the `OutputProcessor` (per-request incremental detokenizer and per-request output queues), so tokenization and detokenization run in the frontend process, not in the engine.
3. **Engine-core client.** `AsyncLLM` reaches the engine through an `AsyncMPClient` (data-parallel variants exist) created by `EngineCoreClient.make_async_mp_client`.
4. **ZMQ between frontend and engine core.** The client and the engine-core process are connected by ZMQ: requests go client ROUTER → engine DEALER, outputs come back engine PUSH → client PULL.
5. **EngineCore is its own process with I/O threads.** `EngineCoreProc` runs in a separate process: an input thread moves socket messages into an input queue, an output thread moves the output queue onto the socket, and the main thread runs the busy loop.
6. **EngineCore owns scheduler and executor.** The engine-core process owns the `Scheduler` (which holds the KV-cache manager), the structured-output manager, and the model executor; each step it schedules, calls the executor, and updates from the model output.
7. **Multiprocess executor spawns one worker per GPU.** `MultiprocExecutor` starts one `WorkerProc` process per local GPU rank.
8. **Shared-memory message queues to workers.** The executor broadcasts each `SchedulerOutput` / RPC to all workers over one shared-memory `MessageQueue` (`rpc_broadcast_mq`); each worker answers on its own `worker_response_mq`.
9. **Worker → GPUModelRunner.** Each worker process holds a GPU `Worker` whose `GPUModelRunner` owns that rank's model shard and KV-cache tensors on its GPU.

For each fact, decide: SHOWN (drawn correctly), ABSENT (not drawn), or CONTRADICTED (drawn in a way that conflicts with the fact). Examples of a contradiction: tokenization or detokenization drawn inside the engine-core or worker processes; the scheduler drawn inside a GPU worker; workers talking to the frontend directly.

PASS if at least 7 of the 9 facts are SHOWN and none is CONTRADICTED.
FAIL otherwise. Begin your explanation by listing the SHOWN / ABSENT / CONTRADICTED verdict for each fact number.
