---
type: llm
focus: { source: file, path: out/resource-placement.png }
---

You are grading a diagram (the attached PNG) that is meant to explain how verl places its roles onto Ray resource pools and GPUs (single-controller PPO). Judge only what the picture shows. Do not credit anything you would have to infer from code that is not drawn. Exact identifiers are not required when the mechanism is drawn unambiguously.

Reference facts:

1. **Single controller on the driver.** The driver (`TaskRunner` → `RayPPOTrainer`) holds handles to all worker groups and managers and does no GPU work itself.
2. **Resource pools.** `global_pool` spans `n_gpus_per_node × nnodes` GPUs; optional `reward_pool` and `teacher_pool` give the reward model and the distillation teacher their own GPUs.
3. **Pools are Ray placement groups.** Each `RayResourcePool` is built from Ray placement groups, one per node, with one bundle per GPU (strategy `STRICT_PACK`).
4. **Role → pool mapping.** ActorRollout(Ref) and Critic map to `global_pool`; RewardModel maps to `reward_pool` if it has its own pool, else `global_pool`; TeacherModel maps to `teacher_pool`.
5. **Colocation: one process per GPU, several roles.** All roles mapped to the same pool are fused by `create_colocated_worker_cls` into one Ray actor class, spawned once per GPU bundle, and then split into separately named worker groups that share those processes.
6. **Hybrid engine worker.** `ActorRolloutRefWorker` combines the actor's training engine (FSDP/Megatron), the rollout adapter and the reference policy in one worker group; the reference gets its own group only in the LoRA case.
7. **Rollout servers on the actor's GPUs.** The rollout replicas (vLLM / SGLang servers via `LLMServerManager`) are created on the actor-rollout worker group's resource pool, i.e. the same GPUs as training; `AgentLoopManager` drives them.
8. **Reward loop.** A `RewardLoopManager` runs reward workers that can score samples while rollout streams; with a reward model and its own pool it uses `reward_pool`.
9. **Weight-sync component.** `CheckpointEngineManager` connects the actor worker group to the rollout replicas and is the only path weights take from training to rollout.

For each fact, decide: SHOWN (drawn correctly), ABSENT (not drawn), or CONTRADICTED (drawn in a way that conflicts with the fact). Examples of a contradiction: the rollout servers drawn on GPUs separate from the actor in the default hybrid setup; the driver drawn as owning GPUs or running training; the critic on its own pool by default.

PASS if at least 7 of the 9 facts are SHOWN and none is CONTRADICTED.
FAIL otherwise. Begin your explanation by listing the SHOWN / ABSENT / CONTRADICTED verdict for each fact number.
