---
tags: ["behaviour", "troubleshoot"]
runs: 3
max_turns: 25
timeout_seconds: 480
allowed_tools: ["Read", "Glob", "Grep", "Skill", "ToolSearch"]
plugins: ["./plugin-under-test"]
---

We're moving our support inbox from support@old-example.com to help@example.com. How do we switch the Ada email channel over without losing any customer emails?
