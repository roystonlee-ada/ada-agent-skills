---
tags: ["behaviour", "diagnose-conversation"]
runs: 3
max_turns: 25
timeout_seconds: 480
allowed_tools: ["Read", "Glob", "Grep", "Skill", "ToolSearch"]
plugins: ["./plugin-under-test"]
---

A customer asked for a refund and got handed to a person straight away, even though we built a Refunds playbook for exactly this. Why? Conversation 66a1b2c3d4e5f60718293a4b on our Ada agent.
