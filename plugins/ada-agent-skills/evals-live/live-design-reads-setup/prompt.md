---
tags: ["live", "design-conversation"]
runs: 3
max_turns: 30
timeout_seconds: 600
allowed_tools: ["Read", "Glob", "Grep", "Skill", "ToolSearch"]
plugins: ["./plugin-under-test"]
---

I want the agent to handle questions about credit card application status. Right now it hands those to a person.
