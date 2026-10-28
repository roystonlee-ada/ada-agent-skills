---
tags: ["behaviour", "onboard-agent"]
runs: 3
max_turns: 25
timeout_seconds: 480
allowed_tools: ["Read", "Glob", "Grep", "Skill", "ToolSearch"]
plugins: ["./plugin-under-test"]
---

Help me set up our new Ada agent so it's ready to launch.
