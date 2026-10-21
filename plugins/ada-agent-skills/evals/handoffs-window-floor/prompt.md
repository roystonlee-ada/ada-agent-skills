---
tags: ["behaviour", "review-handoffs"]
runs: 3
max_turns: 25
timeout_seconds: 480
allowed_tools: ["Read", "Glob", "Grep", "Skill", "ToolSearch"]
plugins: ["./plugin-under-test"]
---

Pull handoffs by reason for the last 60 days and rank them. Today is 20/10/2026.
