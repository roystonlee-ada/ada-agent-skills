---
type: llm
criteria: Treats saved cases as the regression set and shows today vs proposed
---
Pass only if ALL hold:
1. It reads the live Refunds playbook before proposing a change.
2. It names the saved cases tc_101 and tc_102 as the regression set to run on live before and on the draft after.
3. It shows today's flow next to the proposed flow, or a board of the changed flow, before building.
4. It does not stage or claim to stage the change before the person approves.
