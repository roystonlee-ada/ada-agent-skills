---
tags: ["live", "diagnose-conversation"]
runs: 3
max_turns: 30
timeout_seconds: 600
allowed_tools: ["Read", "Glob", "Grep", "Skill", "ToolSearch"]
plugins: ["./plugin-under-test"]
---

Pick one conversation from the last 7 days where our agent handed the customer to a person, and tell me why it handed off.
