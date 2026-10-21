---
tags: ["routing"]
runs: 3
max_turns: 4
timeout_seconds: 240
allowed_tools: ["Read", "Glob", "Grep", "Skill", "ToolSearch"]
plugins: ["./plugin-under-test"]
---

In the refund playbook, add a step that asks for the order number before checking eligibility.
