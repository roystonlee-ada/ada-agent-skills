# Round log

Post one block per round in chat, so the person reads the state of the loop
without scrolling. Round 0 is the baseline on live. Keep earlier rounds in the
final message, newest last.

## Block

```
Round 2 of 3, changeset "<name>" (testing)
Runs used this round: 8. Quota left today: <n>.

| Case | Live | This round | Kind | Owning surface | Fix | Changeset |
|---|---|---|---|---|---|---|
| Refunds: damaged item | fail | pass | fixed | playbook step | Ask for the photo before the order number | <name> |
| Refunds: order not found | fail | fail | works in part | playbook exit | Exit rule rewritten, not reached in the run | <name> |
| Refunds: out of window (must not change) | pass | fail | got worse | playbook step | Withdrawn, reworked next round | <name> |
| Refunds: asks for a person | pass | pass | control | none | none | none |

Counts: targets fixed 1 of 2, controls worse 1 of 2, cases reworded 0.
Open for the person: <the decision, with a recommendation and why>
```

## Columns

- **Case**: the saved name. Add "(must not change)" for controls.
- **Live**: the baseline result from round 0. It does not change between
  rounds.
- **This round**: the result on the changeset, with a link to the conversation.
- **Kind**: fixed, still failing, got worse, same on live, case wrong, works in
  part, or not reached. Use the words of author-playbook's test-case rules.
- **Owning surface**: from the diagnosis (playbook step, playbook exit,
  trigger, knowledge, coaching, custom instructions, action, persona,
  platform). "none" for a pass.
- **Fix**: one line on what was staged for that case this round. "none" if the
  case passes or no fix is staged yet.
- **Changeset**: the changeset name holding the fix.

## Rules

- One row per anchored case, every round. A missing row hides a regression.
- Say how many runs the round used and what is left of the quota.
- Link conversations as `https://<instance>.ada.support/insights/conversations/<id>`.
- The last line is the decision the person owes, or "none, ready for
  ada-promote-changeset" when every case passes.
- After a stop without a pass, add a line: stopped at <reason>, what still
  fails, and the cause for each.
