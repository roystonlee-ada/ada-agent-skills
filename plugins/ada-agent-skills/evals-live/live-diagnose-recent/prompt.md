---
tags: ["live", "diagnose-conversation"]
runs: 3
max_turns: 30
timeout_seconds: 600
allowed_tools: ["Read", "Glob", "Grep", "Skill", "ToolSearch"]
plugins: ["./plugin-under-test"]
---

Some conversations from the last 30 days didn't end resolved. Pick one and tell me why it went wrong.
