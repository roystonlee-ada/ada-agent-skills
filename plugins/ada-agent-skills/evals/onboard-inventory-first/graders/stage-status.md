---
type: llm
criteria: Marks each stage with a status and evidence from the live agent
---
Pass only if ALL hold:
1. It reports setup stages with a status of Done, Partial or Not started (or the same idea in other words).
2. It marks the company description as done or partial, citing the text it found, rather than asking for it.
3. It marks handoff as not started, because no handoff exists.
4. It names the next stage to work on.
