# A2 answer key — how verl places its roles onto Ray resource pools and GPUs (single-controller PPO)

Paths are relative to `src/verl/`; `TR` = `trainer/main_ppo_v0.py`, `T` = `trainer/ppo/ray_trainer.py`, `B` = `single_controller/ray/base.py`, `CE` = `checkpoint_engine/base.py`. Each fact describes a mechanism a diagram can show; the correctness grader's rubric includes the same 9 facts without the line references.

1. **Single controller on the driver.** The driver (`TaskRunner` → `RayPPOTrainer`) holds handles to all worker groups and managers and does no GPU work itself (`TR:132`, `T:772-982`).
2. **Resource pools.** `global_pool` spans `n_gpus_per_node × nnodes` GPUs; optional `reward_pool` and `teacher_pool` give the reward model and the distillation teacher their own GPUs (`TR:67-99`).
3. **Pools are Ray placement groups.** Each `RayResourcePool` is built from Ray placement groups, one per node, with one bundle per GPU (strategy `STRICT_PACK`) (`B:113-166`).
4. **Role → pool mapping.** ActorRollout(Ref) and Critic map to `global_pool`; RewardModel maps to `reward_pool` if it has its own pool, else `global_pool`; TeacherModel maps to `teacher_pool` (`TR:35-65`, `TR:102-121`).
5. **Colocation: one process per GPU, several roles.** All roles mapped to the same pool are fused by `create_colocated_worker_cls` into one Ray actor class, spawned once per GPU bundle, and then split into separately named worker groups that share those processes (`T:873-879`, `B:1008`, `B:426`).
6. **Hybrid engine worker.** `ActorRolloutRefWorker` combines the actor's training engine (FSDP/Megatron), the rollout adapter and the reference policy in one worker group; the reference gets its own group only in the LoRA case (`TR:41-53`, `T:903-907`).
7. **Rollout servers on the actor's GPUs.** The rollout replicas (vLLM / SGLang servers via `LLMServerManager`) are created on the actor-rollout worker group's resource pool, i.e. the same GPUs as training; `AgentLoopManager` drives them (`T:951-962`).
8. **Reward loop.** A `RewardLoopManager` runs reward workers that can score samples while rollout streams; with a reward model and its own pool it uses `reward_pool` (`T:916`, `T:940-949`).
9. **Weight-sync component.** `CheckpointEngineManager` connects the actor worker group to the rollout replicas and is the only path weights take from training to rollout (`T:974-980`, `CE:380-405`).
