# Verifying a finding before it counts

Read this when you build or change the detection pass (SKILL.md step 6, stages
2 to 4).

## Settled

Judge a chat, and above all stop a rollout, only once it has settled. A
playbook that waits on the customer looks like a dead end if you read the
messages alone.

- The chat's last update is 60+ minutes old, or it started 3+ hours ago.
- The reasoning log shows an end event for the last playbook.

## Transcript source

Build transcripts from the dashboard transcript view (the runtime file names the
command or tool). The reasoning log has no live-agent messages and freezes at
grading time, so it produces false alerts. Use `reasoning` for step and playbook
ownership only.

## Cite, then check

Make the reviewer cite the timestamps of the lines behind each finding. Then
check each finding before counting it:

1. The cited lines exist in the transcript.
2. A check with its own logic holds: text similarity for same-turn bursts, a
   playbook marker or pattern for the rest, a second model call for "already
   answered?" repeats.

On a real rebooking playbook this dropped 79 of 283 reviewer claims.

## Guard the checks themselves

- Read a sample of dropped findings by hand. A check that is too narrow drops
  real ones (a pattern for "disruption" that missed reworded apologies).
- A spot check that reads the same transcript as the reviewer does not catch the
  reviewer's errors.
- Do not put a cheap screen in front of the defect check. On one loyalty
  playbook a screen escalated 23 of 24 real chats and flagged 15 as suspected
  defects, so it saved nothing.

## Recheck

Customers reopen chats and finish them later. Each pass, list graded chats that
have messages after their grading run, and judge them again.

## Loop health

Track two numbers per pass: findings claimed, and findings that survived
verification. If under about 70% survive, fix the reviewer prompt or the checks
before the loop reports again. Adjust the 70% after the calibration labels.
