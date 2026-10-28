---
tags: ["routing", "negative"]
runs: 3
max_turns: 4
timeout_seconds: 240
allowed_tools: ["Read", "Glob", "Grep", "Skill", "ToolSearch"]
plugins: ["./plugin-under-test"]
---

My Python script raises KeyError: 'user_id' on line 12. Help me troubleshoot it.
