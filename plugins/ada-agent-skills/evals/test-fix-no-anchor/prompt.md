---
tags: ["behaviour", "test-and-fix"]
runs: 3
max_turns: 25
timeout_seconds: 480
allowed_tools: ["Read", "Glob", "Grep", "Skill", "ToolSearch"]
plugins: ["./plugin-under-test"]
---

Test and fix the store-credit use case on our agent.
