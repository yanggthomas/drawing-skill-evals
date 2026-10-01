---
runs: 1
max_turns: 60
timeout_seconds: 1800
allowed_tools: [Read, Glob, Grep, Skill, Write, Bash]
---

I'm trying to understand how verl runs one PPO/GRPO training step with its single-controller design. The trainer source, pinned at the commit in `PINNED.txt`, is in the read-only source directory available to this session. Draw one diagram that explains what one step of the training loop does: the order of rollout, reward, old and reference log-probs, values, advantage, critic and actor updates; which work runs on the driver and which on Ray worker groups; what accumulates in the batch along the way; and where the weights move between the trainer and the rollout engine. Ground every element in the code. Save the finished diagram as a PNG image at `out/ppo-step.png`.
