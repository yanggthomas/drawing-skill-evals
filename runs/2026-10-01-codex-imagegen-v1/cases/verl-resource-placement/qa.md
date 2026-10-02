# QA — one-shot generated output

Inspected the tool-returned raster visually at full displayed resolution. Built-in imagegen was called exactly once; no references, regeneration, or image editing. Saved the original output bytes by copying to out/resource-placement.png. Exact submitted text is generation-prompt.md.

## Present and legible

The image includes TaskRunner / RayPPOTrainer, three named resource pools with symbolic GPU dimensions, actor/rollout/reference fusion, conditional critic inside the shared process box, separate rollout server box sharing global GPUs, optional shared versus dedicated reward model placement, teacher service, and checkpoint synchronization labels. Sources and pinned commit are visible. Typography is generally readable; no clipped title or footer was observed.

## Errors and ambiguities — output not semantically clean

- A green dashed line from MultiTeacherModelManager is labelled teacher_client but terminates at reward_pool. This is wrong: teacher_client must connect to AgentLoopManager; teacher manager uses teacher_pool.
- A second green dashed teacher_client line originates from CheckpointEngineManager and terminates at teacher_pool. This is wrong: checkpoint manager has no teacher_client connection in the supplied code.
- An orange line from CheckpointEngineManager terminates at reward_pool. This is a false synchronization connection; correct endpoints are actor worker group and rollout replicas. Another orange path reaches the GPU allocation strip rather than clearly terminating at the actor object.
- llm_client arrow ends on the global_pool border rather than directly at the rollout server endpoint, reducing precision.
- rm_resource_pool arrow ends at global_pool and does not clearly represent the dedicated reward_pool alternative. Text accurately states the choice, but connectors do not fully encode it.
- WorkerDict process nesting is visually ambiguous: its left/top outline extends toward rollout servers without an equally clear closed outer process boundary. The inner actor/critic rectangle and separate-process captions communicate the intended distinction, but stricter process containment would be preferable.
- LLMServerManager is placed inside the rollout-servers box. The code shows driver ownership of the manager; this visual nesting can imply incorrect process placement despite the intended logical relation.
- Reference is labelled when needed but drawn solid; the optionality is textual. Dashed GPU-strip borders also overload the stated dashed-means-conditional legend.
- The reward_pool caption says not created when no RM, while allocation creation in main_ppo_v0.py is controlled directly by enable_resource_pool. The RM service is conditional on enable; the diagram conflates allocation and service existence in that sentence.

These issues are retained honestly under the no-regeneration/no-edit constraint. Source files were left unchanged.
