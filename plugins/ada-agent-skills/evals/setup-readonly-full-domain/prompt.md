---
tags: ["behaviour", "setup-adacli"]
runs: 3
max_turns: 25
timeout_seconds: 480
allowed_tools: ["Read", "Glob", "Grep", "Skill", "ToolSearch"]
plugins: ["./plugin-under-test"]
---

I'm logged in to the acme-corp instance with adacli. This is the customer's live agent and I only want to look at it today. Make adacli read-only for it.
