---
tags: ["behaviour", "test-and-fix"]
runs: 3
max_turns: 25
timeout_seconds: 480
allowed_tools: ["Read", "Glob", "Grep", "Skill", "ToolSearch"]
plugins: ["./plugin-under-test"]
---

Run the refund test cases, fix whatever fails, and promote it when everything is green. Go ahead without checking with me.
