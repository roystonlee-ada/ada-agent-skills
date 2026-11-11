---
name: prevent-handoffs
description: >
  Find the handoffs an Ada AI Agent could have prevented, fix the biggest
  causes on a changeset, and prove each fix by replaying the real handed-off
  conversations. Gives every handed-off conversation in a window a verdict
  (preventable, or not: the customer asked for a person, policy needs a
  person, or the agent lacks system access) with the reason and evidence,
  groups the preventable ones by root cause, drafts a knowledge, playbook or
  action fix for the top causes, replays them, and drops fixes that do not
  help. Use it for "prevent handoffs", "which handoffs could the bot have
  handled", "cut escalations and prove it", "how many handoffs are
  avoidable", "reduce handoffs", or "fix the top handoff causes", even if they
  never say "preventable". For counts by reason alone use review-handoffs. To
  rank every signal, not only handoffs, use improve-agent. For one
  conversation use diagnose-conversation.
---

# Prevent handoffs, and prove it with replays

A handoff count says how often the agent gave up. Only some of those
handoffs were the agent's to keep: a customer who wants a person, a refund
that needs approval, and a lookup in a system the agent cannot reach all
belong to people. Sort the handoffs first, fix only the preventable causes,
and keep a fix only when the real conversations it targets now stay with the
agent.

This skill chains others. It does not copy them:
- `review-handoffs` counts handoffs by reason (step 2)
- `mine-human-agent-conversations` reads what the humans did (step 3)
- `diagnose-conversation` names the surface that owns a cause (step 5)
- `author-playbook/references/test-cases.md` section 8 seeds cases (step 6)
- `test-and-fix` runs the replay loop (step 7)
- `ada-promote-changeset` promotes, only on the person's yes (step 9)

## 0. Pick the runtime

Each step below names what to do, not a command. Read one file for how:
- Ada MCP tools present (`get_conversations`, `draft_test_case_from_conversation`)
  → `references/runtime-mcp.md`
- `adacli` on the path → `references/runtime-cli.md`

Then check what the instance allows. Steps 1 to 4 only read. Steps 5 to 7
stage a changeset, save test cases and run them. None of those touch live
customers, but they are writes to the instance. If the instance is
read-only, or the person wants no writes there, stop after step 5 with the
proposed fix list and say why. A sandbox copy of the agent is the other way
through: replay there, and say that the result is from the copy.

## 1. Fix the window and the baseline

- Window: 14 days by default, never before 07/10/2026, the first day handoff
  reasons were recorded. Use whole days and say the time zone.
- Test users excluded, so numbers match the dashboard. Chats started from a
  command-line or test-chat session can count as real ones. Look for a burst
  on one channel on one day with no handoffs, and take it out of N.
- Baseline for the window: conversations N, handed-off conversations H,
  containment, and automated resolution. `improve-agent` step 1 says what
  each counts and how to check containment against real handoffs.

## 2. Pull every handed-off conversation

Count by reason with `review-handoffs` step 1 and keep its caveats (`null`
codes, `unclassified`, attempts against escalations). Then pull every
handed-off conversation in the window, not a sample, with what the runtime
returns for each: id, channel, intent or topic, opening message, summary,
and the reason code. Note any reason that holds most of the handoffs. A
playbook that hands off by design records `handoff_configured` for every
conversation it routes, so the code then says little and the verdict must
come from the conversation.

## 3. Give every conversation a verdict

Open `references/verdicts.md`. It holds the categories, the order to test
them, and the output line. Each conversation gets one verdict
(preventable, not preventable, unclear), one category, a cause label and
evidence.

Do it in two passes:
1. **Record pass, every conversation.** Judge from the conversation's own
   record: summary, intent, opening message, reason code and reasoning. Up
   to about 300 handoffs, read every transcript instead.
2. **Read pass, a sample per cause.** For each of the ten largest causes,
   read at least 8 full transcripts, with the human agent's replies. Use
   `mine-human-agent-conversations` steps 2 and 3 for where replies live
   and how to read them. What the human did decides the hard calls: a
   human who looked up a record means system access; a human who only
   repeated a fact or a procedure means the agent could have said it.

Read a sample of the not-preventable verdicts too, about 30 across the three
reasons. A summary hides a human who only repeated a fact, so the record pass
errs in both directions.

Report how often the read pass agreed with the record pass, per cause and for
the not-preventable sample. Then:
- Scale each cause's count by its agreement rate ("188 x 4/8 = 94") and rank
  on the scaled count. Show both.
- Give the preventable total as a range: the record-pass count, and the count
  adjusted by both agreement rates.
- Where a cause's agreement is under 80%, say what the read pass found
  instead, and read more before you draft its fix.

Never move a conversation to preventable because a fix would be easy.

## 4. Group the preventable ones and rank

Group preventable conversations by cause: the task plus what stopped the
agent ("driver no-order troubleshooting, no article"). Merge labels that
name the same task. Count conversations per cause over the whole window,
each conversation once. Rank by count.

Show the not-preventable share too, split by its three reasons. That is the
floor this skill will not move, and it tells the person how much of the
handoff volume is theirs to decide (`improve-agent`
`references/situation-classes.md` covers policy and judgment clusters).

Take the top five causes unless the person names another number.

## 5. Draft a fix for each top cause

First list the changesets promoted or in testing since the window started.
A promoted change that already targets a cause means the window predates the
fix: re-measure that cause (`review-handoffs` step 5) instead of fixing it
again. A testing changeset that touches the same playbook or articles is an
overlap: name it, and replay on both together before either is promoted.

For each cause, open two or more of its conversations and run
`diagnose-conversation` on them to name the surface that owns it. Check
whether an article the human agents linked already exists in the agent's
knowledge, and whether an inactive playbook already covers the task. Either
one changes the fix from "write" to "retrieve" or "reactivate". Then draft
the fix that surface needs:

| Surface | Fix | Route |
|---|---|---|
| Knowledge missing or wrong | Draft or correct the article. Take the facts from the human replies, never from guesswork | A knowledge edit on the changeset |
| Playbook step, exit or trigger | Name the step and the change | `revise-playbook`, which stages it |
| A handoff playbook fires on an answerable question | Narrow its trigger, or answer first and hand off only if the customer still needs a person | `revise-playbook` |
| Needs a system the agent cannot reach, and an API exists | End-to-end resolution with an action | `design-conversation`. This is no longer a quick fix: say so and size it |
| Coaching or custom instructions | Stage the edit | The changeset, as `test-and-fix` step 4.2 says |

Rules for every fix:
- Stage on a changeset, never live. Use one changeset per fix, so each
  replay measures one fix and a failed fix is dropped alone.
- Search knowledge for the fix's keywords first. List any article that says
  something different and leave it for the person.
- Glossary, variables and topics go live at once. They are not fixes for
  this skill unless the person says yes first.
- A fact a human agent applied is a policy guess until its owner confirms
  it. Mark it OPEN in the fix.

If the run stops here (read-only, no sandbox), write each fix as a draft the
person can stage, and go to step 8 with "not replayed" in the result column.

## 6. Seed the replay cases from the real handoffs

For each fix, draft cases from the conversations it targets, with the draft
tool and `author-playbook/references/test-cases.md` section 8. The draft
screens personal data. Never paste a transcript into a case.

- **Targets:** 5 handed-off conversations from the cause, picked across
  channels and weeks, never only the plainest ones. Each target's criteria:
  the customer gets what the human gave them (the fact, the step or the
  answer), and the conversation ends without a handoff. Agree the wording
  with the person.
- **Resolution control:** 2 conversations on the same topic that the agent
  resolved without a handoff. They must stay resolved.
- **Must-still-hand-off control:** 1 not-preventable conversation next to the
  cause (a policy or system-access case on the same topic). It must still
  reach a person. A fix that keeps it is a fix that hides a real need.

Read `test-and-fix` `references/safe-to-run.md` before any run. Hold any case
that could reach a live queue or a live tool that writes. Every target here
ended in a real handoff, so its replay can reach the same handoff block. The
draft's tool calls name the handoff integration: if that platform is not on
the safe list, hold the cases until the person confirms it is test-safe.

## 7. Replay, fix, replay (three rounds at most)

Run `test-and-fix` with these cases as the anchor and the fix's changeset as
the target. It runs the baseline on live, reruns on the changeset, sorts
each failure and stops at all-pass, three rounds, or a design change. Every
target must fail on live first. A target that passes on live is not a
preventable handoff today, so drop it from the count and say so.

Then score the fix:
- **Contained x of y:** targets that ended without a handoff and passed their
  resolution criteria, over targets run.
- **Resolution held:** every resolution control still passes.
- **Handoff kept:** the must-still-hand-off control still reaches a person.

Keep a fix only when x is at least half of y and both controls hold. Discard
the rest: withdraw the staged change, say why, and keep the case results as
evidence. Judge verdicts vary, so a borderline fix gets one rerun before you
discard it.

When two or more fixes are kept, stage them together on one changeset and
run every case once more. Report any case that changed.

## 8. Report the ranked fix list

Use `references/fix-list.md`. One row per fix, ranked by projected
containment gain: fix, cause, conversations affected, replay result
(contained x of y), projected gain with the arithmetic, and links to the
changeset, the cases and two or more conversations. Then the discarded
fixes with why, the not-preventable floor, and the caveats.

Projected gain uses `improve-agent` `references/sizing.md`, with the replay
rate x/y as the fix rate. Give it as a range, never a promise.

## 9. Promote only on a yes

Never promote. Hand each kept changeset to `ada-promote-changeset`, which
checks it again and offers a direct promote or a rollout, and only when the
person says yes. After promotion, re-measure the cause over a window of the
same length with `review-handoffs` step 5.

## Rules

- Steps 1 to 4 read only. Every write after that waits for the instance
  check in step 0, and every run and every staged fix for the person's yes,
  as `test-and-fix` says.
- Every number comes from the whole window. A sample confirms a mechanism; it
  never sets a size.
- Every cause in the list carries two or more conversation links you opened.
- Keep names, contact details, order numbers and credentials out of reports,
  cases and fixes.
- If the agent has custom metrics that judge resolution or handoff quality,
  read them on the replays and quote them beside the case results.
