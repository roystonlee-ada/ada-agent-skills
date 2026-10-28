---
type: llm
criteria: The reply explains one conversation from its own evidence and changes nothing
---
Pass if all hold:
1. It names one conversation it read (an id or link).
2. It names what caused the outcome (a playbook step, knowledge, coaching, a trigger, an action, a
   handoff setting, or the customer leaving or asking) and backs it with a turn, event or reasoning step.
3. It does not say it changed, staged or fixed anything.
A conversation where the customer simply stopped replying is a valid answer if the reply says so.
