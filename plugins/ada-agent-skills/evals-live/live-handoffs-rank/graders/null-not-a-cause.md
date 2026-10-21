---
type: llm
criteria: Handoffs with no recorded reason are not ranked as a cause
---
Fail if a missing, empty or null handoff reason appears as a ranked cause or a fix.
Pass if it sets them aside, or if the data had none. Ignore everything else.
