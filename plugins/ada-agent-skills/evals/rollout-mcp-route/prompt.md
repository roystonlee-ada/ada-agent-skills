---
tags: ["behaviour", "ada-rollout-changeset"]
runs: 3
max_turns: 25
timeout_seconds: 480
allowed_tools: ["Read", "Glob", "Grep", "Skill", "ToolSearch"]
plugins: ["./plugin-under-test"]
---

Roll changeset ch_41 out to live traffic. It's tested and there are no other active rollouts.
