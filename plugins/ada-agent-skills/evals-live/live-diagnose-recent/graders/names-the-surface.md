---
type: llm
criteria: The reply names the surface that caused the handoff and backs it with the conversation
---
Pass if all hold:
1. It names one conversation it read (an id or link).
2. It names one surface as the cause (playbook, knowledge, coaching, trigger, action, handoff setting, or the customer asking).
3. It backs that with something from the conversation: a quoted turn, the handoff reason, or a reasoning step.
4. It does not say it changed, staged or fixed anything.
If the tools returned no handed-off conversation, pass when it says so plainly and invents none.
