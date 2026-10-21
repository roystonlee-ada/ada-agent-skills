---
type: llm
criteria: Asks at most two choice questions about the goal or rule, and builds nothing
---
The refund policy for damaged items is not in the agent's setup, so the reply may ask before drafting.
Pass only if ALL hold:
1. It asks at most two questions, or none if it drafts sample conversations instead.
2. Each question is about the customer's goal or a policy rule (a cut-off, who qualifies, proof needed), not about playbook steps, fields, variables or settings.
3. Each question offers choices.
4. It builds and stages nothing.
