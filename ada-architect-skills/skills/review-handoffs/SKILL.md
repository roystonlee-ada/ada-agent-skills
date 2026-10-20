---
name: review-handoffs
description: >
  Find out why an Ada AI agent hands conversations to people, rank the causes,
  and send each one to the fix that removes it. Use it whenever someone asks
  "why does it hand off", "what's driving escalations", "what should we fix
  first", "which integration would help most", "where is knowledge missing", or
  "did that change cut handoffs", even if they never say "handoff reason". Also
  use it to re-measure a cause after a fix is promoted. Built on Ada's handoff
  reasons: every handoff since 07/10/2026 records one of eight causes and a
  short reasoning text.
---

# Review handoffs by reason

A handoff count says how often the agent gave up. A handoff reason says why,
and each why has a different owner: a broken integration, a missing article,
a routing rule nobody revisited. Rank the causes, read real conversations for
the top ones, and send each to the fix that removes it.

## 0. Pick the runtime

Each step below names what to do, not a command. Read one file for how:
- Ada MCP tools present (`get_conversations`, `get_available_filters`) →
  `references/runtime-mcp.md`
- `adacli` on the path → `references/runtime-cli.md`

## 1. Count handoffs by reason

Pull a recent window, 7 days by default and never before 07/10/2026. Exclude
test users so numbers match the dashboard. For each reason, get the number of
conversations, the number of failed attempts, and two sample conversations
with their reasoning text.

Three things change what the numbers mean. Say them when you report:
- A reason marks a handoff **attempt**, recorded when it starts, even if no
  person was reached. Escalations are still counted with `is_escalated`.
- `null` means no code was recorded (older handoffs, or an invalid code).
  Count it apart. Never rank it.
- `unclassified` is recorded but uncaused. Agents on Unified Reasoner v2 record
  it for every handoff outside a playbook, so their ranking covers playbook
  handoffs only. Say so if `unclassified` is large.

## 2. Check the top reasons against real conversations

The agent picks the reason itself, so treat it as a lead. For the top three
causes, read both sample conversations and confirm the code fits what
happened. A wrong code is a finding of its own (step 4). Quote the
conversation ids as evidence.

## 3. Send each reason to its fix

| Reason | What it means | What to do | Next skill |
|---|---|---|---|
| `tool_failed` | A Tool or integration failed (timeout, bad credential) | Name the Tool and what it returned. Config or platform? | diagnose-conversation |
| `tool_unavailable` | The agent could do it, but no Tool exists or access is blocked | List the tasks a Tool would remove, with counts. Each is a candidate integration | design-conversation, once a Tool exists |
| `knowledge_unavailable` | The facts were missing, or search found nothing useful | Name the questions. Draft or fix the articles | knowledge draft |
| `issue_unresolved` | A fix ran or the customer tried it, and the problem stayed | Check the troubleshooting path and what comes after it | revise-playbook |
| `handoff_configured` | A playbook or process sends it to a person by design | Ask whether it still should. Show the count, and automate where policy allows | revise-playbook |
| `end_user_requested` | The customer asked for a person before one was offered | Read how early they asked. Often a greeting, trust or wording problem | diagnose-conversation |
| `out_of_scope` | Policy needs a person, and a Tool would not change that | Leave it. Report it as the floor, not a target | none |
| `other` | None of the seven fit | Read the reasoning texts and group them | diagnose-conversation |
| `system_failed` | Fallback after an Ada error | Platform problem | provide-feedback |
| `unclassified` | No cause assigned | Don't rank. See step 1 | none |

Rank the fixes by how many conversations they would remove, not by how many
reasons there are. Push past deflection: a `tool_unavailable` cluster is the
case for an integration that resolves the task end to end, so size it that
way.

## 4. Report

Lead with the top three causes as a short table: reason in plain words,
conversations, share of all handoffs, the fix, and two conversation links.
Then the dates covered and the test-user basis. Then the caveats from step 1
that apply. Keep the codes in brackets after the plain words, for example
"Missing knowledge (`knowledge_unavailable`)".

If the agent keeps choosing a code that the conversations contradict, record
it with provide-feedback. That is a platform problem, not their config.

## 5. Re-measure after a fix

Before staging a fix, save the baseline: the reason's count and the window.
After the change is promoted and has run for the same length of window,
count again and show both. Compare like with like: the same days of the
week, and conversations, not attempts. If the count did not move, diagnose
again before adding another fix.
