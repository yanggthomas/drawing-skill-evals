---
type: llm
focus: { source: file, path: out/ppo-step.png }
---

You are grading a diagram (the attached PNG) that is meant to explain one PPO/GRPO training step in verl's single controller (`RayPPOTrainer.fit`). Judge only what the picture shows. Do not credit anything you would have to infer from code that is not drawn. Exact identifiers are not required when the mechanism is drawn unambiguously.

Reference facts:

1. **Single controller, one step per batch.** `fit()` runs on the driver and loops over epochs and dataloader batches; each batch becomes one step. Each prompt is repeated `rollout.n` times before generation, so a prompt gets n responses.
2. **Rollout, then the rollout engine sleeps.** The driver calls `async_rollout_manager.generate_sequences(...)`, which generates on the rollout replicas (LLM servers). Right after, `checkpoint_manager.sleep_replicas()` frees the replicas' weights and KV-cache memory so training can use the GPUs.
3. **Batch accumulation.** The prompts (repeated n times) are unioned with the generated responses into one `DataProto` batch. Every later stage adds fields to that same batch with `batch.union(...)`: rewards, `old_log_probs`, `ref_log_prob`, values, advantages.
4. **Reward.** Token-level scores come from the reward loop (streamed during rollout) or a reward-model pass, and are extracted into `token_level_scores`.
5. **Old log-probs by the actor worker group.** Unless bypass mode reuses `rollout_log_probs`, the actor worker group recomputes `old_log_probs` (and entropy) for the generated tokens via `actor_rollout_wg.compute_log_prob`.
6. **Optional reference and critic passes.** If a reference policy is used, the ref worker group computes `ref_log_prob`. If a critic is used, the critic worker group computes `values`.
7. **Advantage on the driver.** On the driver: an optional KL penalty is folded into the reward (`token_level_rewards`), then `compute_advantage` runs. The estimator is GAE for PPO with a critic, or group-normalized outcome advantage over each prompt's n responses for GRPO.
8. **Updates on worker groups.** The critic is updated first if present. The actor is then updated with the PPO loss, except during critic warm-up steps.
9. **Weight sync trainer → rollout.** After the actor update, `checkpoint_manager.update_weights` moves the new weights to the rollout engine. With colocated (naive) sync, each actor worker resumes the rollout's weight memory and pushes its per-tensor parameters into the rollout in the same process (`get_per_tensor_param`). With other backends (NCCL/NIXL), it aborts in-flight requests, frees the KV cache, sends the weights over a process group, then resumes.

For each fact, decide: SHOWN (drawn correctly), ABSENT (not drawn), or CONTRADICTED (drawn in a way that conflicts with the fact). Examples of a contradiction: the actor is updated before rewards or advantages exist; the advantage is computed on the rollout replicas; the weights are synced to the rollout before the actor update.

PASS if at least 7 of the 9 facts are SHOWN and none is CONTRADICTED.
FAIL otherwise. Begin your explanation by listing the SHOWN / ABSENT / CONTRADICTED verdict for each fact number.
