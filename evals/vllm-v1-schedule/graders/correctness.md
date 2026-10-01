---
type: llm
focus: { source: file, path: out/schedule-step.png }
---

You are grading a diagram (the attached PNG) that is meant to explain one step of vLLM V1's `Scheduler.schedule()`. Judge only what the picture shows. Do not credit anything you would have to infer from code that is not drawn. Exact identifiers are not required when the mechanism is drawn unambiguously.

Reference facts:

1. **Budget source.** The step starts with one token budget, `token_budget = max_num_scheduled_tokens`. That value defaults to `max_num_batched_tokens` and is shared by every request scheduled in the step.
2. **Budget decrement.** Each scheduled request takes `num_new_tokens` off the budget, whether it came from running or waiting. Both loops stop once the budget reaches 0.
3. **Running before waiting.** The step first walks the `running` list in order. Only after that does it admit requests from the `waiting` queue.
4. **Chunked prefill.** A request's `num_new_tokens` is the gap between its tokens and its `num_computed_tokens`. The scheduler caps it by `long_prefill_token_threshold` and then by the remaining budget, so a long prompt gets only a chunk this step. After scheduling, `num_computed_tokens` is advanced by the scheduled count, so the next step continues the prompt where this chunk stopped. There is no separate prefill or decode phase: a decode is the same rule with a gap of 1.
5. **KV block allocation.** Before a request is committed to the step, `kv_cache_manager.allocate_slots(request, num_new_tokens, ...)` reserves KV-cache blocks for the new tokens. It returns `None` when there are not enough free blocks.
6. **Preemption (running side only).** When allocation fails for a running request, the scheduler preempts a victim and retries. The victim is the last request in `running` (FCFS), or the lowest-priority request under the priority policy. `_preempt_request` frees the victim's KV blocks, sets it to `PREEMPTED` with `num_computed_tokens = 0`, and puts it back at the **front** of the waiting queue. If the victim is the current request itself, that request is not scheduled this step.
7. **Preemption blocks admission.** If any request was preempted in this step, the waiting queue is skipped entirely: `if not preempted_reqs`.
8. **Admission stop conditions.** A waiting request is admitted only while all of these hold: the budget is > 0, the queue is non-empty, and `len(running) < max_num_active_reqs`. Its `allocate_slots` call must also succeed, and a failure there **stops** admission without preempting anyone. On admission the request first takes its prefix-cache hit as already-computed tokens, so only the uncached suffix is scheduled. The request then moves into `running` with status `RUNNING`.
9. **Output to the model runner.** The step returns a `SchedulerOutput` carrying:
   - `scheduled_new_reqs`: full `NewRequestData` (prompt tokens and block ids) for requests scheduled for the first time.
   - `scheduled_cached_reqs`: a `CachedRequestData` diff (new block ids, `num_computed_tokens`) for continuing running requests and resumed preempted requests.
   - `num_scheduled_tokens`: tokens per request, plus `total_num_scheduled_tokens`.
   - `finished_req_ids` and `preempted_req_ids`, so the workers can free their cached state.

For each fact, decide: SHOWN (drawn correctly), ABSENT (not drawn), or CONTRADICTED (drawn in a way that conflicts with the fact). Examples of a contradiction: waiting requests are scheduled before running ones; a failed waiting allocation triggers preemption; a preempted request goes to the back of the queue; there are separate prefill and decode phases.

PASS if at least 7 of the 9 facts are SHOWN and none is CONTRADICTED.
FAIL otherwise. Begin your explanation by listing the SHOWN / ABSENT / CONTRADICTED verdict for each fact number.
