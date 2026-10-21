---
type: llm
criteria: Every ranked cause carries a count, and a window with no handoffs ranks nothing
---
Fail if it ranks a cause with no conversation count or share next to it.
Fail if it says there were no handoffs and still ranks causes.
Pass otherwise, including when it reports zero handoffs and ranks nothing.
