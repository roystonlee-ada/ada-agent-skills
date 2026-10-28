---
type: llm
criteria: If it covers the missing-tool handoffs, it gives a full plan, not just 'add an API'. If it does not cover them, pass
---
The data has 148 handoffs where no tool exists (booking name changes, special service requests). If the reply
covers them, pass only if it either sizes end-to-end resolution through an API, or recommends the agent collect
the needed fields and write a summary before handoff. Fail if it stops at "add an API" or "build an integration".
If it does not cover them, pass.
