---
tags: ["behaviour", "design-conversation"]
runs: 3
max_turns: 25
timeout_seconds: 480
allowed_tools: ["Read", "Glob", "Grep", "Skill", "ToolSearch"]
plugins: ["./plugin-under-test"]
---

I want the agent to handle refunds for damaged items. Today it hands every one to a person. Policy: the customer gives the order number and a photo of the damage. If the order is 30 days old or less, refund in full. Older than 30 days, offer store credit. No photo, hand to a person.
