---
tags: ["behaviour", "configure-handoff"]
runs: 3
max_turns: 25
timeout_seconds: 480
allowed_tools: ["Read", "Glob", "Grep", "Skill", "ToolSearch"]
plugins: ["./plugin-under-test"]
---

Set up handoff from our Ada agent to Gladly, then test it end to end with a real chat right now.
