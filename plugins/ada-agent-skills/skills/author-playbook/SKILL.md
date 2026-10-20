---
name: author-playbook
description: >
  Build a V2 playbook from an approved design board, save the design's
  scenarios as test cases, stage it as a draft and run every case before
  reporting back. Use it as soon as the chat sends DESIGN-APPROVED, and
  whenever you are about to write or rewrite a playbook's steps. Covers when to
  use a code tool, how to word asks, channel choices, and the test run that
  ends every build. The ada-agent-toolkit skill holds the platform detail; this
  skill holds the method.
---

# Build the playbook from the design

The approved design is the spec. Build the simplest playbook that produces
those conversations, then prove it does. The person should never have to ask
"have you tested it?" or "can I see the conversation?".

## 0. Pick the runtime

Each step below names what to do, not a command. Read one file for how:
- Ada MCP tools present (`get_ada_configuration`, `get_test_cases`) →
  `references/runtime-mcp.md`
- `adacli` on the path, or you are inside Ada Architect →
  `references/runtime-cli.md`

No `/mnt/memory` folder means you are outside Ada Architect. Then the runtime
file says what replaces Approve, the changeset card and the chat blocks.

## 1. Save the scenarios as test cases, first

Before you write a step:
1. List the saved test cases and reuse any that covers the same scenario.
   Never write a duplicate.
2. For each approved scenario, save a case: the customer's first turn, the
   later customer turns, `good` (the scenario's `expect`) and `fail` (what
   would break it). Name each "<Use case>: <scenario>". Saved cases are the
   regression set for every later change, so they come before the playbook.
   Read `references/test-cases.md` before you write the wording. A case's
   `good` and `fail` name something the judge can find in the conversation,
   hold for one outcome, and the customer's turns let the agent reach it.
   Add two or more controls from the nearest existing use cases, named
   "(must not change)".
3. Run every case on live only before you build. A target case that passes on
   live is a wrong case or a wrong diagnosis: fix it now. If more than half
   the targets already pass, stop and say so.
4. Record the use case so the next session reuses it: its key, the playbook
   names once they exist, and the case ids. Record it again when the
   playbook names are known.

## 2. Design the playbook from the whole conversation

Read the playbook authoring guide for platform detail (the runtime file
says where it is). Then work from the design, not from the last comment:
- Map each bot turn to one step. One ASK collects one fact. If the design has
  a turn that collects two, the design is wrong; go back to the board rather
  than writing a step that asks for both.
- Write each step's instruction for the turn it produces, in a few lines. No
  rule lists. A step that needs "also include X, unless Y, but if Z" is a sign
  the logic belongs in a code tool or a branch.
- Choices: give an ASK `accepted_values` when the design shows `options`. On
  social channels the question itself carries the numbered list, and a typed
  number maps back to its value.
- Reuse their existing actions. Never invent one. If the design needs data no
  action returns, say so plainly and stop.
- Branch with IF_ELSE on variables, two or three levels at most.

## 3. When to use a code tool

Use a code tool for anything that must come out exactly the same every time.
The step model is good at language and bad at exactness, so moving that work
out keeps the steps short and the results stable.

| Use a code tool | Keep it in the step |
|---|---|
| Dates and times: parse, compare, add days, time zones, "before 06:00 counts as the day before" | Wording a question or an answer |
| Formats: normalise a phone, reference or name; check a pattern | Understanding a free-text reply |
| Arithmetic, totals, fees, eligibility thresholds | Choosing between a few meanings the customer might have |
| Lookup tables (fare classes, region codes, price bands) | Saying sorry, explaining a policy from knowledge |
| Reading a value out of an action's response | Summarising for a handoff |

List the existing code tools first and reuse one if it fits. Give a new code
tool one job, clear input and output names, and run it on sample input before
a playbook calls it. Set its inputs with SET steps
before the RUN step that calls it, because RUN does not fill code tool inputs
itself.

## 4. Push back on patches

When asked for a change that adds a rule to a step to fix one case, look at
the whole flow first. If the case shows the question or the flow is wrong,
fix the design: change the board, get it approved, rebuild. Say why in one
sentence: "Adding 'also ask for the time' to the date question makes it ask
two things at once. I've made the time its own question instead."

## 5. Stage, test, report. Every time.

1. Stage it as a draft linked to the approved design (its `work` key). A
   draft with no approved design is not allowed. It needs no diagnosis: the
   approved design is the reason for the change.
2. Check routing for every case's opening message against the draft. Fix
   routing before running full cases.
3. Pin test: run the plainest target case on the draft alone. If it fails the
   way live did, the edit is not working. Find the step setting that decided
   the outcome and fix it before you run anything else. Rule text in an
   instruction does not override a saved value, a fallback, an
   accepted-values list or a stay-in-playbook setting.
4. Run every case on the draft and on live. Sort each failure with the table
   in `references/test-cases.md`: got worse, same on live, case wrong, works
   in part, not reached. Fix a wrong case by rewording it and rerunning that
   case. Show the results as the required last message: one row per case,
   with live, draft, a one-line note and a link to each conversation, plus
   counts by kind ("targets fixed 4 of 6, controls worse 0 of 8").
5. Compare the draft conversations with the approved board. Say plainly where
   a conversation differs from the design, even when the judge passed it.
   For a scenario that ends with a person, check the handoff's `reason_code`
   against why the design sends it there. Leave a handoff step's reason empty
   so Ada assigns one after save. Set `reason_code` and a one-line `reasoning`
   on the step only when the recorded reason is wrong, because Ada never
   overwrites a reason you set.
6. Only then say what the evidence supports. The person decides on Promote.
