---
name: playbook-monitor-loop
description: >
  Set up and run a monitoring and fix loop for a playbook: a test suite, a
  control set, a check of real chats that stays silent unless a verified
  finding exists, design-level fixes staged as changesets, and before-and-after
  metrics once a change is live. Use for "monitor this playbook", "set up the
  fix loop for X", "keep an eye on it after promote", "run the improvement
  loop", "cut the noise in the alerts", or "should we revert this change".
---

# Playbook monitor loop

The loop has two outputs: silence, or one finding that arrives with a staged,
tested fix. It never sends a bare suspicion, and it never fixes one chat at a
time. Per-chat patches pile up into a playbook nobody can reason about.

## 0. Pick the runtime

Each step below names what to do, not a command. Read one file for how:
- Ada MCP tools present (`get_ada_configuration`, `get_conversations`) →
  `references/runtime-mcp.md`
- `adacli` on the path, or you are inside Ada Architect →
  `references/runtime-cli.md`

## Inputs

Ask for what is missing, and nothing more: the instance, the playbook (id or
name), and anything the person already suspects is broken. Derive the rest.

## Who judges

Ada judges first. You judge only what Ada cannot see.

| Check | Judge |
|---|---|
| Test case pass or fail | The test run's `criteria_results` |
| Quality per chat (repeats, re-asks, false handoff claims, privacy) | Ada custom metrics, if the instance has active ones. A refusal or an empty list means judge from the transcript. |
| Anything outside the transcript (tool calls, KB facts, handoff summaries) | Read the reasoning log, then judge |

## 1. Discover

1. Read the playbook and every playbook that routes into it or that it runs.
2. Note the KB articles and actions it depends on.
3. Pull 20 to 30 recent real chats for it (real traffic only, no test chats)
   and read the transcripts, not only the outcome labels. Note the languages
   and code-switching used, how customers really phrase the intent, recurring
   state (status, channel, tier, urgency, repeat contact), and friction already
   visible. The test suite builds on this.

## 2. Monitoring record

Write `/mnt/memory/<instance>/monitoring/<playbook-slug>.md`:

- **Intended design:** the success criteria every case and fix is judged
  against, taken from the playbook's own instructions. If they are vague or
  contradict each other, say so and ask.
- **Test cases and control set** (steps 3 and 4).
- **Accepted friction:** patterns the person labelled fine (step 5).
- **Open findings:** dedupe key, first seen, conversations, state.
- **Fix log:** one entry per attempt, win or dead end.

Name each chat by its full dashboard URL, not a bare id, because people check
findings by clicking through.

## 3. Test suite

Build 6 to 12 cases from the step graph, the intended design and the step 1
sample together. Cover the happy path, every explicit branch, the known issues,
and 2 or 3 cases modelled on real transcripts (a different language mix,
channel or urgency). Name the real chat each follows.

Script each case as explicit turns. A vague goal like "get their invoice" makes
the simulated customer declare success after the first bot reply. Give each a
checkable pass condition, not "handles it well". Show the draft suite before
the first run.

## 4. Run it and keep the controls

Create the cases and run them on live (draft and live runs are `promote-changeset`
step 1). Read each verdict from the test run, not by re-reading the transcript
yourself. The cases that pass on live today are
the **control set**. After any fix, a control that fails is a regression. A case
that already failed is not the fix's to chase.

## 5. Calibrate before the first report

Show the person 3 to 5 flagged real chats with full URLs and ask them to label
each: real defect, accepted friction, or not a defect. Record the labels in
Accepted friction. Repeat when a threshold changes.

## 6. Detect

Run a pass when the person asks, or when `/mnt/memory` shows a scheduled one is
due. A sandbox has no timer, so say that nothing runs between your turns.
Each stage removes noise, so keep the order.

1. **Pull Ada's fails** for the window, for the baseline and every active
   rollout arm.
2. **Settle.** Drop chats still moving. Recheck graded chats for later messages.
3. **Review what Ada cannot see**, only for fails that could stop a rollout.
4. **Verify** every finding against the transcript before it counts
   (`references/finding-verification.md`).
5. **Deduplicate.** Drop Accepted friction. Match the rest on playbook, step and
   mechanism against Open findings, and add to an open one.
6. **Apply the threshold.** A finding is worth raising only when:
   - the harm is a wrong fact, privacy breach, loop, false connect claim,
     blocked customer or unexpected escalation, in 2 or more chats (one is
     enough for a wrong fact or a privacy breach), or
   - a rate gap against baseline has a 95% interval clearing the margin, or
   - a funnel step drops against baseline. A silent drop-off sets off no bad-turn
     flag, so track completion as well as bad turns.
7. **Rank** by affected chats times the gap. Drop what would not move
   resolution, containment, CSAT or a custom metric.

A pass with nothing to raise says "no findings" in one line and stops.

**Friction mining** uses the same stages. Candidate steps are replies that give
the customer something to do elsewhere (a link, a contact, a multi-step
instruction). Scan the customer's next 1 or 2 typed turns for confusion or
re-ask markers. Raise a step only with 3 or more hits across 3 or more chats and
a friction rate above the baseline rate. A friction finding is a hypothesis: it
goes to step 7 as a design change, with the person's go-ahead.

## 7. Fix a confirmed finding

1. **Cluster** findings by owning surface and mechanism. Fix each cluster once.
2. **Diagnose** with `diagnose-conversation`. It names the surface (exit, wrong
   playbook, knowledge, coaching, action, then a step) and rules out others with
   chat ids.
3. **Route by size.** A mechanical bug in one named step, or wording in one step,
   takes the small path in `revise-playbook`. A change to what the customer is
   asked, the order or the outcome, several clusters on one playbook, or a step
   patched before takes the full path. A changed goal goes to
   `design-conversation`.
4. **Keep the controls.** Run the control set on live before the change, then on
   the draft and on live after it. Add the finding's chats as cases. A control
   that regresses blocks the fix. Report failures by kind.
5. **Try to break it.** Hand the raw diff and run evidence, not your summary, to
   a fresh reviewer told to refute it: judge against Intended design, re-derive
   the verdict from the reasoning log, reproduce the original failure, and look
   for collateral damage. A fix that does not survive goes in the Fix log as a
   dead end. Do not argue down a refutation.
6. **Test before traffic.** Follow `promote-changeset` step 1: the finding's chats
   plus a regression sample, draft against live.
7. **Hand over a fix, not a suspicion:** the finding, 2 or 3 chat URLs, the owning
   surface, the changeset and its diff, test numbers and control results.
   The person promotes or rolls out (`promote-changeset`, `rollout-changeset`).
8. **Re-test live** with a fresh chat after promotion.
9. **Stop guard.** If a case fails the same way after a fix, diagnose again with a
   different hypothesis. After 3 attempts on a cluster, or 2 cycles with no
   progress, log the cluster as failed with every hypothesis tried. Never mark
   it passed.

## 8. After a change is live

Compare the changeset arm with the baseline and trace every loop or bad chat to
the playbook that sent the line (`rollout-changeset`, `references/rollout-metrics.md`).
Recommend a revert only on the terms stated there. Monitoring reports. It never
promotes or reverts.

## What reaches the person

One report, ranked by impact. Never report a clean pass.

| Kind | Content |
|---|---|
| Action needed | A verified finding with a staged, tested fix: URLs, owning surface, whether the change touched it, changeset name, test numbers, one-line ask |
| Decision needed | A design question, or a finding with no safe fix yet: what is known, then a recommendation and why |
| FYI | Friction steps raised and loop health: the share of findings that survived verification |
