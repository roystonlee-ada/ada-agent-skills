---
name: ada-custom-metrics-improve
description: >
  Review the custom metrics on one Ada AI Agent, decide which failures are real
  agent defects and which come from a bad judge, rank the defects by metric
  impact, and fix them as a changeset (diagnose, test, roll out, prove with
  before and after). Use when someone says "review the custom metrics", "what's
  failing on the scorecard", "which metrics can we improve", "are these custom
  metrics any good", "use the custom metrics to improve the agent", or "run the
  improvement loop off the metrics", even if they never say "skill". For an agent
  with no metrics yet, use ada-custom-metrics-setup first.
---

# Custom metrics review and improvement

Custom metrics give the loop a verdict on every ended chat, where CSAT covers a
small share. That only helps if the judge is right. So review the metrics first
and fix the agent second. A fix aimed at a judge error makes a good agent worse.

One agent per run. The metric review, the chat samples and the fixes stay in one
customer's context.

## 0. Pick the runtime

Each step names what to do, not a command. Read one file for how:
- Ada MCP tools present (`get_ada_configuration`, `get_ada_metric`) →
  `references/runtime-mcp.md`
- `adacli` on the path, or you are inside Ada Architect →
  `references/runtime-cli.md`

## 1. Check the agent has metrics

List the custom metrics and scorecards.
- Active metrics exist: go on.
- The call is refused, or the list is empty: stop and say which. Custom metrics
  are off for this agent, or nobody has created any. Offer `ada-custom-metrics-setup`.
  Create nothing in this run. A new set needs about 2 weeks of scoring before a
  review is worth reading.

## 2. Review the metric set

Use a window of 7 to 14 days. Build one row per active metric with pass, fail and
null counts, and flag the ones you cannot trust yet.

| Flag | Meaning | Action |
|---|---|---|
| few scored | Under 30 pass and fail rows | Read nothing into the rate. Widen the window |
| mostly null | Null on over half of chats | The metric rarely applies. Check its scope |
| no signal | 0% or 100% fail | The wording never matches, or always does. Edit it before you use it |
| at row cap | 10,000 rows in one result | The count is cut off. Split the window |
| numbered name | Name starts with "1." etc. | Rename it. Numeric prefixes made a whole set score false |
| outcome link | Fail wording says "handed off" | It tracks containment by construction. Do not count it as a separate finding |

Also check by hand: weights on each scorecard sum to 1.0, an older metric needs
`subject: ai_agent` before an edit passes review, and the agent is under the cap
of 20 metrics.

## 3. Calibrate the fails

The judge reads the transcript only. Tool calls, knowledge text, variables and
handoff events are not shown to it, so a metric about knowledge accuracy or
handoff summaries guesses from text.

For each of the top 3 failing metrics, pull 10 fails and open each transcript.
Label every one:
- **Real defect.** The agent did the thing the metric names.
- **Judge error.** The transcript does not show the defect, or the wording is too broad.
- **Accepted friction.** True, but the customer has said it is fine.

Trust a metric when 9 of 10 are real defects. Below that, it goes to step 4a before
it drives any fix. Give every finding 2 to 3 full conversation URLs
(`https://<instance>.ada.support/insights/conversations/<id>`), and mark each as
opened or ASSUMED.

## 4. Split the findings

**4a. Judge errors: fix the metric.** Edit the wording. If Ada's authoring review
flags the edit, it is held until you fix what the review names and activate it. An
offline check of new wording does not show how Ada's judge will read it, so watch
the live fail rate for about 2 days before you call it fixed.

**4b. Real defects: rank, then fix.** Rank by affected chats times the gap, so the
work goes to what moves containment, resolution, CSAT or a custom metric most.
- Take the headline rates from the platform's own metrics over the same window.
- Split a metric's fails by intent and by playbook, then cluster by mechanism. One
  cluster gets one fix.
- Join the verdicts to resolution and CSAT to see whether a failing metric also
  costs resolution. If it does not, say so and rank it low.

## 5. Run the improvement loop

Ask the person which path, with a recommendation and a reason.

| Path | Use when | How |
|---|---|---|
| Fix now | Clusters are ready and they want changesets this session | `diagnose-conversation` on a chat from each cluster, then `revise-playbook` or `ada-playbook-monitor-loop` to stage and test the fix |
| Ramp it | A tested fix should meet live traffic | `ada-rollout-changeset`, then judge it with the metric rates |
| Review only | They want findings, not fixes | Stop after step 4 and report |

Rules that stay fixed:
- Every fix lands as a changeset. Never edit the live agent.
- Test a fix on saved cases before any live traffic.
- The person promotes. Use `ada-promote-changeset`, and only when they ask.
- Stop after 3 attempts on a cluster and log what is missing. Never mark it passed.

## 6. Prove it

Compare the changeset against the baseline over the same dates. Custom metrics come
back as rates with no interval, so do not claim a win from one metric alone.
Require a floor of 30 scored chats per arm, and read the metric next to resolution
and containment. Report a fall as plainly as a rise.

## 7. Report

One report, ranked by impact. Each finding carries: the metric, what the agent did,
2 to 3 conversation URLs, the surface that owns it, the changeset, the test
numbers, then a recommendation and reason. Judge errors get their own short list
with the wording change made. The report holds real conversation IDs, so keep it
inside the customer's own workspace.
