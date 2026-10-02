# Grounding

Inputs restricted to this case prompt.md and src/**. Pinned commit: fbb4b3a8bf636f290c9c59fc346f756849e9c241 (src/PINNED.txt:3).

Source paths below are relative to src/.

- Driver RPC orchestration and local advantage: verl/trainer/ppo/ray_trainer.py:1405–1411.
- Initial sync: ray_trainer.py:1428–1430.
- DataProto, uid, repetition: ray_trainer.py:1478–1491. Generation, sleep, union, mask: 1513–1544.
- Streamed reward worker setup: ray_trainer.py:946–964. Conditional colocated RM and extraction: 1561–1568; manager compute call: 588–594.
- Stable old anchor / bypass: ray_trainer.py:1570–1617; actor call:1304. Entropy removed before union:1601.
- Conditional reference: ray_trainer.py:1618–1622; ref-in-actor and ref worker variants:1266–1286.
- Conditional values: ray_trainer.py:1624–1628; critic infer_batch:1257.
- Reward fields, KL, correction, driver advantage: ray_trainer.py:1630–1675; PPO vs GRPO inputs and output fields:219–247. GRPO outcome reduction: core_algos.py:304; mask broadcast:329.
- Critic training and actor ordering: ray_trainer.py:1676–1690. Worker entry points:1397 and1369.
- Warmup still syncs: ray_trainer.py:1683–1686. Normal sync:1714–1716.
- Manager naive vs distributed weight sync: verl/checkpoint_engine/base.py:510–560. Worker direct/send branches: verl/workers/engine_workers.py:728–804.

Assumptions / abstractions: figure shows PPO/GRPO training-critical path, not all estimator variants, validation, checkpoint-save or profiling. Boxes represent logical roles, not unique GPUs. Typical rollout output fields inferred from trainer accesses and mask use; rollout_log_probs explicitly conditional. GRPO described as no value input, while values/update guard remains use_critic rather than asserting GRPO can never configure a critic. Reward extraction precedes old logprob; token_level_scores is only installed at the advantage stage. Each batch column shows additions retained into later rows.
