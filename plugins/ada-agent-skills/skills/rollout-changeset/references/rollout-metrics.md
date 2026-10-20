# Rollout metrics, attribution and the revert decision

Read this when a change is live on some or all traffic and someone needs to
judge whether it made things worse.

## Arms

- **Sampled rollout.** Changeset arm is chats served by the changeset, baseline
  is the rest. The split is random, so a gap is caused by the change.
- **Promoted to live.** Changeset arm is chats after the promote time, baseline
  is chats before it. Label every table "before and after, not randomized",
  because traffic mix shifts by day and hour.
- Count only chats after this build's rollout start, so an earlier build does
  not blend into the baseline.

## Metrics

| Metric | Use |
|---|---|
| Containment, automated resolution, CSAT | Context only. Never a stop signal alone. |
| Loop rate | The same 60+ character bot line re-sent after a customer reply, AI part only. |
| Bad rate | Trapped (one bot line sent 3+ times), a false connect claim (bot says it is connecting, asks nothing that turn, no handoff ran), or unreached (customer asked for an agent 2+ times, no handoff, chat ends waiting). |
| Custom metrics | Ada's per-chat verdicts. Use them first, before writing your own check. |
| Stop check | Bad-rate gap whose 95% interval lower bound clears a set margin (2 points unless the person sets another), with 100+ chats per arm. |

A transfer that is asking for the customer's details ("I'm arranging a
transfer, could you share your name?") is the handoff playbook working. It is
not a false connect claim.

Report every gap with a 95% interval. A point estimate alone invites false alarms.

## Attribution

Split loops and bad chats by the playbook that sent the repeated or wrong line,
not by every playbook that ran in the chat. Co-occurrence blames always-on
playbooks such as Greeting and Triage for rises that come from elsewhere.

1. Read the chat's reasoning log (the runtime file says how).
2. For each `step_invoked` event with `step_type` reply_to_customer, pair the
   message text in `args` with `playbook_observability.playbook_id`.
3. Match the flagged bot line to a pair by an 80-character prefix. Record the
   owning playbook on the flagged chat.
4. Per playbook, report flagged chats it owns per sampled chat, changeset arm
   minus baseline, in points.
5. Recompute the gap without the top contributor the change did not touch. If
   the gap closes, the change is not the cause.
6. State the share of flagged chats you traced. Below about 80%, call
   attribution a lead, not a finding.

## Revert decision

Recommend a revert only when both hold:

- The defect comes from a step the change touched, shown by attribution or by
  reading the log.
- No quick forward fix exists, such as a one-line question or instruction edit.

A count that meets a threshold is not enough. A false connect count can meet its
threshold while its rate fell after the change, and the cause can be one
question's wording that takes minutes to fix. In that case the whole rise came
from a playbook the change never touched.

Monitoring reports. It does not revert. A report names the criterion, the full
conversation URLs, the owning playbook, whether the change touched it, and a
suggested forward fix. A revert staged in advance goes stale the moment anyone
edits live config, so never promote one unprompted.
