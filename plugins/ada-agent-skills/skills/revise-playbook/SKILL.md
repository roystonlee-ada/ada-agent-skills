---
name: revise-playbook
description: >
  Change how an existing use case works: a new step, a new rule, a new input
  such as a photo, a different outcome, or a fix that a diagnosis routed to a
  playbook. Use it whenever someone asks to change, extend or fix an existing
  playbook or flow, and after diagnose-conversation names a playbook as the
  surface. It rethinks the flow from the use case's goal instead of patching
  one step, shows today's flow next to the proposed one, and re-runs the saved
  tests.
---

# Change a use case, not a step

The common failure is editing the one step the person pointed at, then the
next one, until the playbook is a pile of patches. Start from what the use
case is for, and change the design.

## 0. Pick the runtime

Each step below names what to do, not a command. Read one file for how:
- Ada MCP tools present (`get_ada_configuration`, `get_test_cases`) →
  `references/runtime-mcp.md`
- `adacli` on the path, or you are inside Ada Architect →
  `references/runtime-cli.md`

No `/mnt/memory` folder means you are outside Ada Architect. Then the runtime
file says what replaces the board, Approve and the memory notes.

## Unattended mode

This applies when `/mnt/memory` is mounted and a scheduled loop started you, with
no person in the chat. The loop's first message and an ask ledger script in its
tools folder are the signs. Then:

- Never wait for a board, Approve or a person. The approval is the ask's answer in
  the ledger: a row in stage `answered` with the chosen option. Change what that
  option says and nothing wider. If there is no such row, stop and record why.
- If the use case's goal would change, do not redesign it alone. Set the ask's
  stage to `cause_known` so the loop asks the person, and stop that item.
- Write today's flow next to the proposed one in the loop's work folder, stage the
  change as a draft, and re-run the saved tests. Record the build and the test run
  in the ledger as done, waived with a written reason, or not_testable_yet with a
  reason.
- Never promote, revert, delete or ramp. The loop's own rules beat this skill
  wherever they differ.

## 1. Load what is already known

Do these first, before you propose anything. Skipping them is how a revision
ends up patching a playbook nobody read.
- Read the whole live playbook, and every playbook it runs or that routes
  into it. Read the live version, not a memory of it.
- Load the saved test cases and keep every one that touches this use case.
  These are the regression set. They come first because new cases replace
  nothing. Do not regenerate them.
- Run the regression set on live before you change anything. Record which
  pass. Those are the controls: if one fails after your change it got worse,
  and if it already fails, it is not yours to chase. A case that already fails
  because its wording contradicts the design goes back for review.
- Read the use case's record if one exists: its goal, approved scenarios and
  test case ids.
- If the change aims to cut handoffs, save the baseline count for that
  handoff reason first (review-handoffs, step 5).

No record? Then write today's flow as a design board first (design-conversation),
from the live playbook, marked as round 1 and titled "<use case>: today".
That gives the person a picture of what customers meet now.

## 2. Decide the size of the change

- Wording or routing in one existing step, nothing else: change it, then run
  the saved cases for this use case. No board needed.
- Anything that changes what the customer is asked, in what order, or what
  they get: send the board again with the same `work`, with today's flow as
  the scenarios that stay and the changed scenarios marked with `changed`.
  Add a scenario for the new case. Wait for Approve.
- The goal itself changed: treat it as a new design (design-conversation)
  and say so.

## 3. Rebuild the flow, then retest

After Approve, follow author-playbook from step 2, with these differences:
- Rewrite the steps the design touches as a whole, so the playbook reads as
  if it was written this way from the start. Remove steps and rules that the
  new design no longer needs.
- Save test cases only for scenarios that are new or changed. Keep the old
  ids for the rest, and update the use case's record.
- Check old cases against the approved board before running.
  An out-of-date case goes back for review with `updated`, not into the run.
- Name the step setting that decides the behaviour you are changing (accepted
  values, re-asks, fallback, stay-in-playbook, branch) from a failing live
  conversation, before you edit. A change that only adds rule text to an
  instruction will not move a step whose saved value decides it.
- Pin test the plainest new case on the draft first, then run the whole set,
  old and new, on the draft and on live. Sort every failure with the table in
  author-playbook's `references/test-cases.md`. An old case that now fails is
  a finding to show, not to hide.
- End with a table of every case, old and new: live result, draft result,
  and a link to each conversation, plus counts by kind. This is the required
  last message. If you could not run the cases, say that first and say why.
