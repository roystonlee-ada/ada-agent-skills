---
tags: ["behaviour", "design-conversation"]
runs: 3
max_turns: 25
timeout_seconds: 480
allowed_tools: ["Read", "Glob", "Grep", "Skill", "ToolSearch"]
plugins: ["./plugin-under-test"]
---

I want the agent to handle refunds for damaged items. Right now it hands every one of those to a person.
