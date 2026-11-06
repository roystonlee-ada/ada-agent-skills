---
tags: ["routing", "named"]
runs: 3
max_turns: 4
timeout_seconds: 240
allowed_tools: ["Read", "Glob", "Grep", "Skill", "ToolSearch"]
plugins: ["./plugin-under-test"]
---

Run mine-human-agent-conversations on the last 28 days of handoffs.
