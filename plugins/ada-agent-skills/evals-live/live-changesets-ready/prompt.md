---
tags: ["live", "ada-promote-changeset"]
runs: 3
max_turns: 30
timeout_seconds: 600
allowed_tools: ["Read", "Glob", "Grep", "Skill", "ToolSearch"]
plugins: ["./plugin-under-test"]
---

Which changes are waiting to go live on our agent, and is any of them ready to promote?
