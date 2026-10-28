---
name: ada-custom-metrics-loop
description: >
  Run the custom metrics improvement loop on one Ada AI Agent, for a single
  metric or for every active metric: measure, judge the judge, find the cause
  behind the fails, stage a tested fix, ramp it, then re-measure and go round
  again until the metric holds. Use when someone says "improve this metric",
  "fix the metric that's failing", "run the metrics loop", "loop on all the
  custom metrics", "keep improving the scorecard", "did the fix move the metric",
  or "start the next cycle", even if they never say "loop". For a one-off review
  of the set with no fixes, use ada-custom-metrics-improve. For an agent with no
  metrics yet, use ada-custom-metrics-setup.
---

# Custom metrics improvement loop

One cycle is: measure, calibrate the judge, cluster the fails, fix, test, ramp,
re-measure. The loop repeats cycles until each metric in scope is at its target
or you hit a stop rule. It builds on `ada-custom-metrics-improve` (the review) and
hands each fix to the skills that already stage, test, ramp and promote changesets.

One agent per run. Metric rates, chat samples and fixes stay in one customer's context.

## 0. Pick the runtime

Each step names what to do, not a command. Read one file for how:
- Ada MCP tools present (`get_ada_configuration`, `get_ada_metric`) →
  `references/runtime-mcp.md`
- `adacli` on the path, or you are inside Ada Architect →
  `references/runtime-cli.md`

## Unattended mode

This applies when `/mnt/memory` is mounted and a scheduled loop started you, with
no person in the chat. The loop's first message and an ask ledger script in its
tools folder are the signs. Then:

- Never wait for a person. Take the scope the loop names, use the recommended
  target and window, and mark each ASSUMED in the run notes.
- Steps 1 to 5 (scope, check, measure, calibrate, cluster) and step 7 (re-measure)
  are allowed.
- In step 6, the "Ramp it" path and the rule that the person promotes are **not
  allowed** here. Only "Fix now" (stage and test a draft) and "Report only" are
  open. The loop owns every ramp and every promote, through its own guarded steps.
- Step 8's next cycle starts only in a later run, never in the same one.
- Never promote, revert, delete or ramp, and do not load a skill that does. The
  loop's own rules beat this skill wherever they differ.
- Record each step's outcome in the ledger as done, waived with a written reason,
  or not_testable_yet with a reason. Write the report to the loop's work folder.

## 1. Set the scope

Ask with a recommendation and a reason. Take what the person already said.

| Scope | Use when | Cycle shape |
|---|---|---|
| One metric | They name a metric, or one metric is the problem | Go deep: calibrate it, cluster every fail, fix each cluster, re-measure it |
| All metrics | They want the scorecard to improve overall | Run the health table, then work the metrics in rank order, one at a time |

For all metrics, do not fix them in parallel. Two changesets on the same playbook
make the before and after unreadable. Take the highest-impact metric first, finish
its cycle, then move to the next.

Also fix these before cycle 1, and write them in the run notes:
- **Target** per metric: a pass rate the customer would call good. If they have
  none, propose one from the current rate and mark it ASSUMED.
- **Direction** per metric. A `higher_is_worse` metric reads backwards.
- **Window** of 7 to 14 days, and the start date of the baseline.

## 2. Check the agent has metrics

List the custom metrics and scorecards.
- Active metrics exist: go on. For one metric, confirm it is active and match it
  by id or name. If two match, ask which.
- The call is refused, or the list is empty: stop and say which. Offer
  `ada-custom-metrics-setup`. Create nothing in this run.

## 3. Measure the baseline

Pull pass, fail and null counts per metric in scope over the window, plus the
headline rates (containment, resolution, CSAT). Apply the trust flags in step 2 of
`ada-custom-metrics-improve` (few scored, mostly null, no signal, row cap, numbered
name, outcome link) and skip any metric that is flagged until its cause is fixed.

Rank the rest by affected chats times the gap to target. Drop any already at target.

## 4. Calibrate the judge

Run step 3 of `ada-custom-metrics-improve` on each metric before you work it: open
10 fails, label each real defect, judge error or accepted friction, and trust the
metric only at 9 of 10 real. A judge error gets a wording edit and about 2 days of
live fail rate before you build on it, because a fix aimed at a judge error makes a
good agent worse. Give every finding 2 to 3 conversation URLs, marked opened or ASSUMED.

## 5. Cluster the real defects

Split the metric's fails by intent and by playbook, then group by mechanism. One
cluster gets one fix. Join the verdicts to resolution and CSAT. If a failing
metric does not cost resolution, say so and rank it low.

For one chat per cluster, run `diagnose-conversation` to name the surface that owns
the problem (playbook, knowledge, coaching, trigger, action, handoff, persona).

## 6. Fix, test, ramp

Ask the person which path, with a recommendation and a reason.

| Path | Use when | How |
|---|---|---|
| Fix now | A cluster is ready and they want a changeset this session | `revise-playbook` or `ada-playbook-monitor-loop` to stage and test the fix |
| Ramp it | A tested fix should meet live traffic | `ada-rollout-changeset`, then judge it on the metric rates |
| Report only | They want findings and a plan | Stop after step 5 and report |

In unattended mode, "Ramp it" and the promote rule below are not allowed.

Rules that stay fixed:
- Every fix lands as a changeset. Never edit the live agent.
- Test on saved cases before any live traffic. Build the cases from the cluster's chats.
- The person promotes, through `ada-promote-changeset`, and only when they ask.
- Stop after 3 attempts on a cluster and log what is missing. Never mark it passed.

## 7. Re-measure

Compare the changeset against the baseline over the same dates, with at least 30
scored chats per arm. Custom metrics come back as rates with no interval, so do not
claim a win from one metric. Read it next to resolution and containment.

For each cluster, record: fixed, no change, or worse. Report a fall as plainly as a
rise. If a fix lowered another metric, revert only when the change is the cause.

## 8. Go round again

After each cycle, update the run notes with the new rate against target, then
choose:
- **At target** for two windows in a row: mark the metric done.
- **Moved but short of target**: start the next cycle on the clusters that remain.
- **No movement after 3 cycles**: stop, log what is missing (a data source, an
  integration, a product limit) and tell the person.

In all-metrics scope, move to the next metric in the rank order from step 3 only
after the current one is done or stopped. Re-run the health table at the start of
each metric, because one fix often moves a neighbour.

## 9. Report

One report per cycle, ranked by impact, in the customer's own workspace (it holds
real conversation IDs). Each row carries: metric, rate before and after against
target, what the agent did, 2 to 3 conversation URLs, the owning surface, the
changeset, test numbers, then a recommendation and reason. Add a short list of judge
errors with the wording change made, and the run notes with each metric's status:
done, in progress, stopped.
