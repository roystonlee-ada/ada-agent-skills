---
tags: ["routing"]
runs: 3
max_turns: 4
timeout_seconds: 240
allowed_tools: ["Read", "Glob", "Grep", "Skill", "ToolSearch"]
plugins: ["./plugin-under-test"]
---

The agent got stuck in a loop asking a customer for their email twice. Why did it do that?
