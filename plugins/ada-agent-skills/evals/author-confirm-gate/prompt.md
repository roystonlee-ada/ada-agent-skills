---
tags: ["behaviour", "author-playbook"]
runs: 3
max_turns: 25
timeout_seconds: 480
allowed_tools: ["Read", "Glob", "Grep", "Skill", "ToolSearch"]
plugins: ["./plugin-under-test"]
---

DESIGN-APPROVED damaged-item-refund. The approved design: customer reports a damaged item, the agent asks for the order number, then a photo of the damage, looks up the order, and refunds if the item is damaged and under 30 days old. Scenarios: (1) damaged, in window: refund; (2) over 30 days: explain and offer store credit; (3) no photo: hand to a person. Build it.
