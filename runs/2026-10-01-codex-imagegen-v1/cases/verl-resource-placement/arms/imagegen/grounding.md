# Grounding

Only this case prompt.md and src files, plus the imagegen skill, were consulted. No outside implementation, prior diagrams, graders, reports, or memory were read. One built-in image generation call was made, without reference images. Source was not changed.

Pinned source: src/PINNED.txt identifies fbb4b3a8bf636f290c9c59fc346f756849e9c241 (2026-09-30). Paths below are relative to src/.

| Fact used | Source |
| --- | --- |
| TaskRunner is a Ray actor and owns RayPPOTrainer, initializes workers and fits | verl/trainer/main_ppo_v0.py:136–140,217–234 |
| ActorRolloutRefWorker registered as ActorRolloutRef when reference needed and not ref_in_actor, otherwise ActorRollout; global_pool | verl/trainer/main_ppo_v0.py:35–54 |
| Critic TrainingWorker mapped to global_pool, actual creation conditional on use_critic | verl/trainer/main_ppo_v0.py:57–65; verl/trainer/ppo/ray_trainer.py:797–835 |
| Global allocation is trainer GPUs per node repeated trainer.nnodes times | verl/trainer/main_ppo_v0.py:70–73 |
| Optional reward_pool allocation uses reward model dimensions; otherwise inherits trainer dimensions | verl/trainer/main_ppo_v0.py:75–85 |
| Teacher pool exists for distillation and uses distillation dimensions | verl/trainer/main_ppo_v0.py:87–95 |
| RewardModel maps to reward_pool or global_pool; TeacherModel maps to teacher_pool; neither registered in role_worker_mapping | verl/trainer/main_ppo_v0.py:102–121 |
| Reference registration is no-op in supplied runner; reference fused into actor/rollout group | verl/trainer/main_ppo_v0.py:123–130; verl/trainer/ppo/ray_trainer.py:893–907 |
| Hybrid engine required; role predicates determine optional components | verl/trainer/ppo/ray_trainer.py:333–348 |
| WorkerDict built per pool, then role views spawned | verl/trainer/ppo/ray_trainer.py:870–880 |
| WorkerDict instantiates role objects directly in same process; spawn views retain same worker handles | verl/single_controller/ray/base.py:1028–1048,738–770 |
| Placement group bundle reserves one GPU; default STRICT_PACK and one bundle list per node-sized entry | verl/single_controller/ray/base.py:135–162 |
| ResourcePoolManager default max_colocate_count=3; pool resource sharing is distinct from process fusion | verl/single_controller/ray/base.py:194–222 |
| RewardLoopManager gets selected pool or None | verl/trainer/ppo/ray_trainer.py:909–919 |
| MultiTeacherModelManager gets teacher pool | verl/trainer/ppo/ray_trainer.py:925–937 |
| LLMServerManager receives actor worker group and actor rollout resource pool; AgentLoopManager receives llm_client, optional teacher_client, conditional reward handles | verl/trainer/ppo/ray_trainer.py:949–965 |
| Streaming reward handles only for no RM or dedicated pool | verl/trainer/ppo/ray_trainer.py:946–959 |
| Shared-pool RM uses trainer reward call | verl/trainer/ppo/ray_trainer.py:588–593,643–646 |
| CheckpointEngineManager binds actor worker group and rollout replicas | verl/trainer/ppo/ray_trainer.py:967–978 |
| Weight synchronization is actor to rollout; actor ME/CE same process and rollout CE/inference separate processes | verl/checkpoint_engine/base.py:380–406 |
| naive delegates actor update_weights; non-naive constructs replica WG and updates both sides | verl/checkpoint_engine/base.py:510–541 |

## Scope and assumptions

This is the supplied unified main_ppo_v0 path, not every possible subclass mapping. GPU slots and ellipses are schematic; no job configuration or literal GPU count was provided. Pool dimensions show GPU allocation, not proof that pools occupy disjoint physical nodes. Server and loop implementation files are absent, so their internals and exact rank topology are not asserted. Conditional critic uses need_critic rather than an unverified exact PPO/GRPO predicate. Separate reference-worker compatibility code exists in ray_trainer.py:837–845 but the supplied runner does not register it. Manager boxes are logical ownership, not claims that every manager is an independent remote process. All image imperfections are separately recorded in qa.md.
