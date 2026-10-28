---
tags: ["routing", "named"]
runs: 3
max_turns: 4
timeout_seconds: 240
allowed_tools: ["Read", "Glob", "Grep", "Skill", "ToolSearch"]
plugins: ["./plugin-under-test"]
---

Use onboard-agent to show which setup stages our agent has finished.
