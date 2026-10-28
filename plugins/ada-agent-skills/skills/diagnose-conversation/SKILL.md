---
name: diagnose-conversation
description: >
  Find out why a conversation went wrong before anyone changes anything. Use it
  whenever someone shares a conversation link or id, asks "why did it do
  that", reports a wrong answer, a loop, an unwanted handoff, a dropped
  customer or an "internal error", or when a test case fails. Names the surface
  that owns the problem (playbook exit, playbook step, knowledge, coaching,
  trigger, action, handoff, persona), rules out the others with evidence, and
  hands the fix to the right flow. Then re-tests the same case.
---

# Diagnose before you fix

A trace of a playbook always makes the playbook look guilty, because the
trace is of the playbook. Most wasted work starts there: step after step
edited one by one, when the real cause was that the conversation left the
playbook, the knowledge was wrong, or coaching pulled it elsewhere.

## 0. Pick the runtime

Each step below names what to do, not a command. Read one file for how:
- Ada MCP tools present (`get_conversation`, `get_ada_configuration`) →
  `references/runtime-mcp.md`
- `adacli` on the path, or you are inside Ada Architect →
  `references/runtime-cli.md`

No `/mnt/memory` folder means you are outside Ada Architect. Then the runtime
file holds the diagnosis block's format.

## Unattended mode

This applies when `/mnt/memory` is mounted and a scheduled loop started you, with
no person in the chat. The loop's first message and an ask ledger script in its
tools folder are the signs. Then:

- Never wait for a person, a board, an Approve button or a reply. A step that says
  to ask in chat does not apply. Decide from the evidence, mark the call ASSUMED,
  and go on.
- Write the diagnosis block to the loop's work folder, not to chat. If the cause
  needs a decision only a person can make, say so in the block, set the ask's stage
  to `cause_known` in the ledger, and stop that item. The loop's ask skill takes it
  from there.
- Never promote, revert, delete or ramp, and do not load a skill that does. The
  loop's own rules beat this skill wherever they differ.
- Record each step's outcome in the ledger as done, waived with a written reason,
  or not_testable_yet with a reason. A blank step blocks a later promote.
- Re-testing the same case still happens, on the draft only.

## 1. Read the conversation and its log

- Read the transcript.
- Read the reasoning log: which playbook ran, which steps, which knowledge
  and coaching were used, and where the playbook ended.
- If it handed off, read the handoff's `reason_code` and `reasoning`. The agent
  chose that code, so it is a lead for which surface to check first, not a
  verdict. A code the log contradicts is a finding to report.

## 2. Check the surfaces in this order

Stop at the first one that explains the symptom, but still rule out two more.

1. **Did it leave the playbook?** An exit, a switch to another playbook, an
   intent change mid-ask, or the reasoner answering on its own after the
   playbook ended. If it left early, the cause is why it left (the exit
   condition, a trigger, an intent change), not the steps it never reached.
2. **Was it the wrong playbook, or none?** The trigger or description drew it
   in, or failed to.
3. **Was it a fact or an action?** A fact that came out wrong is usually
   knowledge: a missing, outdated or duplicate article, or a correct one that
   lost to another. Check what retrieved.
4. **Did coaching or general instructions override it?** Read the coaching
   that fired. A coaching rule can make a playbook look broken.
5. **Did an action fail?** A failed action forces a handoff, and test chats
   can hide it.
6. **Only now: a step.** Name the step and what in its wording or setting
   caused the turn.

Publish the diagnosis. It states the symptom in the customer's words, the
mechanism (the actual step, rule or gap, not a restatement), the surface and
one sentence on why it owns the fix, at least two ruled-out surfaces with the
evidence that rules each out, real conversation ids as evidence, and your
confidence. The runtime file gives the format.

## 3. Hand off to the right fix

| Surface | Next |
|---|---|
| Playbook steps or flow | revise-playbook |
| Playbook exit or trigger | revise-playbook, with the routing change in the design |
| Knowledge | a knowledge edit, staged as a draft |
| Coaching or general instructions | a coaching edit, worded for the coaching review |
| Action | say what the action returned, and whether it is a config or a platform problem |
| Platform behaviour | say so, and file it with provide-feedback |

## 4. Prove it

Turn the conversation into a test case unless one already covers it. Run it on the draft
with the fix and on live, and show both conversations as links. If the same
case fails the same way after a fix, stop and diagnose again with a different
hypothesis.
