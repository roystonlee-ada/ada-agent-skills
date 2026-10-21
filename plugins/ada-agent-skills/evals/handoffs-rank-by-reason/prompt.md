---
tags: ["behaviour", "review-handoffs"]
runs: 3
max_turns: 25
timeout_seconds: 480
allowed_tools: ["Read", "Glob", "Grep", "Skill", "ToolSearch"]
plugins: ["./plugin-under-test"]
---

Why does our agent hand off so much, and what should we fix first?
