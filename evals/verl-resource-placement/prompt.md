---
runs: 1
max_turns: 60
timeout_seconds: 1800
allowed_tools: [Read, Glob, Grep, Skill, Write, Bash]
---

I want an architecture overview of how verl lays out a PPO/GRPO job on a Ray cluster. The trainer source, pinned at the commit in `PINNED.txt`, is in the read-only source directory available to this session. Draw one architecture diagram showing the driver, the Ray resource pools and what GPUs they cover, which roles (actor, rollout, reference, critic, reward model, teacher) are mapped to which pool, which roles share the same worker processes, and how the rollout servers, the reward loop and the weight-sync component are connected to them. This is about structure and placement, not about the order of the training steps. Ground every element in the code. Save the finished diagram as a PNG image at `out/resource-placement.png`.
