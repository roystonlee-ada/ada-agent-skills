---
tags: ["routing"]
runs: 3
max_turns: 4
timeout_seconds: 240
allowed_tools: ["Read", "Glob", "Grep", "Skill", "ToolSearch"]
plugins: ["./plugin-under-test"]
---

How do we prove the refund use case still works after every change we make?
