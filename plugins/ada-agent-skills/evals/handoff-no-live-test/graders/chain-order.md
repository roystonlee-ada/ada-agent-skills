---
type: llm
criteria: Covers the chain in order (trigger and Gladly connection first, test last), or stops early to ask; fails only if it jumps straight to a test chat
---
Pass if it works through the handoff in order, starting from what triggers it and the Gladly connection and
credentials, before routing, availability, what the customer sees and the return path. It may stop early to
ask a question. Fail if it jumps straight to a test chat.
