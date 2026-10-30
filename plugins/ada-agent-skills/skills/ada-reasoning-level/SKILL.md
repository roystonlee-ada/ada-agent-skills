---
name: ada-reasoning-level
description: >
  Decide which Playbook SET and ASK steps should run at Reasoning level High,
  prove it on real inputs, and stage the change. Finds the steps that extract
  a wrong value (dates, business days, anything computed), flips them to High,
  moves High steps that gain nothing back to Normal, and rewrites an instruction
  when the miss is about wording. Use for "reasoning level", "set this to
  high", "which steps need High", "the SET gets the date wrong", "this step is
  slow", or "audit my SET steps". Not for a wrong step order or a wrong route
  (diagnose-conversation) and not for a new playbook (author-playbook).
---

# Choose the Reasoning level for SET and ASK steps

High sends a step's extraction to a stronger, slower model. It is not a general
upgrade. In our runs it fixed date arithmetic and did nothing for most other
tasks, at a cost in time. You decide step by step, and a step changes only when
a test on its own inputs says so.

Read `references/findings.md` before you recommend anything. It has the numbers
and what High does at runtime.

## 0. Pick the runtime

Each step below says what to do, not a command. Read one file for how:
- Ada MCP tools present (`get_ada_configuration`, `edit_agent_behavior`) →
  `references/runtime-mcp.md`
- `adacli` on the path, or you are inside Ada Architect →
  `references/runtime-cli.md`

## 1. Scope

Ask which agent, and whether the person wants one playbook or all of them. Say
what is in scope: a generative SET (it has an instruction) and a reasoning ASK.
An exact SET (a literal value), an exact ASK and a send step have no level, so
leave them alone.

## 2. Inventory

List every in-scope step with its playbook, its current level and its
instruction. Mark the steps that use a variable the playbook later branches on:
a wrong value there sends the customer down the wrong path, so those matter
most.

## 3. Sort the steps

Put each step in one bucket. The bucket is a guess to test, not a verdict.

| Bucket | Signs in the instruction or the variable | First move |
|---|---|---|
| Likely High | Works out a date, a weekday, a deadline or "N days or business days after". The extracted value feeds a branch or an action. | Test Normal against High |
| Test first | A rule with several parts, a long lookup list, a classification with a precedence rule, arithmetic, several variables at once | Test Normal against High. Expect no gain. |
| Keep Normal | Copies a value the customer said (an order number, a name, an email), a yes or no, a short list of accepted values | Leave it. Test only if real chats show wrong values. |
| High today | Any step already at High | Test it too. Move it to Normal when High gains nothing. |

A step with a real miss in past chats goes to the front of the line whatever
its bucket. Find the misses first: a variable that ended at its fallback value,
a customer who corrected the agent, or a branch taken on a value that was wrong.

## 4. Prove it

For each candidate, run the same instruction at Normal and at High on at least
5 inputs, 4 runs each.

- Use real inputs from past chats where you can. Add the edge cases the
  instruction names: month ends, leap years, a weekend start, a value missing
  from a list, two rules that both apply.
- Work out the right answer by hand first. Do not accept the answer of either
  level as the key.
- Use saved test cases when one reaches the step. When none does, build a
  scratch copy and A/B it, as the runtime file describes.
- Count a run that never reached the step as a missed run, not as a pass.
  Report how many runs reached it.
- Time each step. Report the median for both levels.

Raise a step to High only when Normal misses on these inputs and High does
not. A step where both are always right stays at Normal. A step where High is
wrong as often as Normal stays at Normal.

## 5. Rewrite the instruction only for a wording miss

A longer instruction did not fix date arithmetic at Normal in our runs, so do
not use a rewrite to avoid High there. Rewrite when the miss is one of these:

- The output has the wrong shape (a sentence instead of `YYYY-MM-DD`). State the
  exact format and one example.
- The value is outside the allowed set. Add `accepted_values`.
- Two rules in the instruction conflict, or one is missing. Fix the rule.
- The instruction names a customer detail the transcript never holds. Say what
  to return when it is missing.

After a rewrite, run step 4 again on the new wording at the level you chose.

## 6. Set the safety net, then stage

- Give every High step a `fallback_value` the playbook handles. High has a time
  limit and no second model, so a failure writes the fallback or leaves the
  variable empty.
- Keep each step's id, and send every other step's `reasoning_level` back as you
  read it. A rewrite that drops the field sets the step to Normal without a
  warning.
- Stage one changeset for the playbooks you change. Name it for the purpose, for
  example "Reasoning level for date steps". Never write live.
- Check the staged changeset shows the new level on each step you meant to
  change and on no other.

## 7. Report and hand over

Give the person one table, one row per step you tested:

| Playbook and step | Was | Now | Normal right | High right | Seconds, Normal and High | Why |
|---|---|---|---|---|---|---|

Under it, list the steps you left alone and why, then the open questions you
could not test (voice, real inputs, load). Link sample chats as
`https://<instance>.ada.support/insights/conversations/<id>` and say whether you
opened each one.

Then hand the changeset to `ada-promote-changeset`. Never promote it
yourself. The person decides.

## 8. After promote

Come back after a week of live traffic. Check that the variable now ends at its
fallback value no more often than before, that the playbook's completion rate
did not fall, and that nobody complains about slow replies on voice. Revert the
level on a step that got slower and did not get more accurate.
