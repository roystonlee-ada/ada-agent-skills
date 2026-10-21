---
tags: ["live", "review-handoffs"]
runs: 3
max_turns: 30
timeout_seconds: 600
allowed_tools: ["Read", "Glob", "Grep", "Skill", "ToolSearch"]
plugins: ["./plugin-under-test"]
---

Why does our agent hand off so much? Look at the last 7 days and tell me what to fix first.
