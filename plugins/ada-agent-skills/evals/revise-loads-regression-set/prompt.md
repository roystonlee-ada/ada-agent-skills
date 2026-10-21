---
tags: ["behaviour", "revise-playbook"]
runs: 3
max_turns: 25
timeout_seconds: 480
allowed_tools: ["Read", "Glob", "Grep", "Skill", "ToolSearch"]
plugins: ["./plugin-under-test"]
---

In the Refunds playbook, add a step that asks for a photo of the damage before checking eligibility.
