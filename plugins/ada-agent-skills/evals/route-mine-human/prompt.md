---
tags: ["routing", "vague"]
runs: 3
max_turns: 8
timeout_seconds: 300
allowed_tools: ["Read", "Glob", "Grep", "Skill", "ToolSearch"]
plugins: ["./plugin-under-test"]
---

After the bot hands off, our human agents answer the same refund-status questions all day. What are they doing that a playbook could take over?
