---
tags: ["routing"]
runs: 3
max_turns: 4
timeout_seconds: 240
allowed_tools: ["Read", "Glob", "Grep", "Skill", "ToolSearch"]
plugins: ["./plugin-under-test"]
---

How do we change the email address our Ada agent's email channel sends from, without any downtime?
