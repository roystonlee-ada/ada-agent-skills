---
name: improve-agent
description: >
  Rank what to improve on an Ada AI Agent across the whole population, using
  handoff reasons, custom metrics, containment, CSAT and the conversations
  behind them, and name the next skill for each fix. Use it whenever someone
  asks "what should we improve", "what do we fix first", "where is the agent
  losing conversations", "how do we raise containment", "how do we raise
  automated resolution or CSAT", "what are humans handling that the agent
  could", "build the improvement backlog", or "review this agent" with no single
  conversation in mind, even if they never say "improve". Each recommendation
  carries a size, the metric it moves, a mechanism and two or more conversation
  links. For one conversation use diagnose-conversation. For handoff counts by
  reason alone use review-handoffs. For the custom metric scorecard alone use
  ada-custom-metrics-improve.
---

# Improve an agent, ranked by what moves the metrics

A list of fixes is easy to write and hard to trust. Three things make it
trustworthy: the size comes from the whole population, the mechanism comes from
real conversations, and every recommendation ends at a next skill, not at "add
an API". Build the list in that order.

## 0. Pick the runtime

Each step below names what to do, not a command. Read one file for how:
- Ada MCP tools present (`get_conversations`, `get_ada_metric`) →
  `references/runtime-mcp.md`
- `adacli` on the path → `references/runtime-cli.md`

If both are present, use the MCP for counts and rates, and adacli for exports.
Neither route is connected: use `setup-ada-mcp` or `setup-adacli`.

## 1. Fix the window and the population

Pick one window (28 days by default, never before 07/10/2026, because handoff
reasons start on that date). Pull, for that window, with test users excluded:
- engaged conversations: this is the population N, and the denominator for
  every share below
- containment, automated resolution, CSAT, and handoff volume
- the custom metrics and their pass rates, when the agent has them

Before you quote containment, compare the handoff steps in a sample of logs
with the handoff count for each channel. On one real instance email handoffs
ran with Count as Handoff off, so reported containment was about 27 points too
high. Split N by channel to see it.

Containment and automated resolution are different numbers. Containment counts
conversations that were not escalated. Automated resolution counts only the
contained conversations that were also relevant, accurate and safe. Report both
and say which one each recommendation moves. Each route's exact definitions are
in its runtime file.

## 2. Collect the clusters

A cluster is one task or one failure, counted over the whole window. Build them
from every signal, not handoffs alone:
- handoffs by reason: count them with `review-handoffs` (its step 1 holds the
  rules: the 07/10/2026 floor, test users excluded, `null` and `unclassified`
  never ranked). Then split each top reason by topic or intent, because one
  reason holds many tasks
- contained but not resolved conversations
- low CSAT conversations
- failing custom metrics, direction-aware
- repeat contacts and tool errors, when the counts are high

One conversation can sit in several clusters. Assign each to one cluster, the
first that applies, so no conversation is counted twice in the ranking.

## 3. Place every handoff cluster in one situation class

Open `references/situation-classes.md`. It holds the six classes, the signals
that separate them, what to recommend, and the next skill. Place each cluster in
exactly one class by reading its conversations, not by reading the reason code
alone: the agent picks the code itself, so treat it as a lead.

## 4. Learn from what the humans did

For a cluster where a person closed the case, read what the human agent said
after the handoff: what they asked for, what they told the customer, what closed
the case. That is the cheapest source of the missing article, the missing field
or the missing step. Open `references/human-agent-learning.md` for what to read
and for the helpdesk export to ask for when the route does not return those
messages. Say in the report whether this section rests on the transcript, on an
export, or is missing.

## 5. Size every cluster

Open `references/sizing.md`. For each cluster it gives the count, the share of
the population, the metric it moves and an estimated lift range, with the
arithmetic shown. The count comes from the population filter, never from the
sample. A sample of a few conversations confirms the mechanism and nothing else.

## 6. Confirm the mechanism, then write the recommendation

For each cluster in the top ten by size, read at least two conversations
(three if the cluster is large). Name the step, rule, gap or missing system
that stopped the agent. A recommendation needs all four of:
- the situation class and size (step 3 and step 5)
- the mechanism, in one or two sentences that name the step or gap
- two or more conversation links you opened
- the next skill

A cluster that lacks two conversations you can link, or a mechanism you can
name, is not a recommendation. List it under data gaps with its count and what
is missing. Hold this line when the person asks for a one-line answer: a short
answer is still a ranked line with its size and two links. If you cannot supply
them, say what is missing, never a bare suggestion. A bare suggestion is the
thing that wastes the next fix.

Link each conversation with the dashboard URL the route returns. A conversation
id alone is not a link.

## 7. Report

Use this order:
1. The window, the population N, and the baseline: containment, automated
   resolution, CSAT, and the custom metric pass rates.
2. Ranked recommendations, largest expected lift first. Each has: the plain
   name of the fix, situation class, cluster size in conversations and share of
   the population, metric moved, lift range with the arithmetic, mechanism, two
   or more conversation links, next skill.
3. The floor: clusters in the policy or authority class. Show their size, say a
   person must decide, and do not rank them as targets.
4. Caveats and data gaps: `unclassified` volume, the human-agent source, thin
   CSAT counts, clusters withheld for lack of evidence, overlap between
   recommendations (their lifts do not add).

Never promise the lift. Say "estimated", show the range, and say the range comes
from an assumed fix rate unless you measured one.

## 8. Hand off, then re-measure

Name the next skill and stop. This skill stages nothing and promotes nothing.
After a fix is promoted and has run for a window of the same length, rerun steps
1 to 5 for that cluster and show the baseline beside the new count, as in
`review-handoffs` step 5.

## Next skills

- `design-conversation`: a task the agent cannot do yet, or an end-to-end
  resolution to design
- `revise-playbook`: an existing flow that needs a step, a rule or a wording
  change
- `diagnose-conversation`: the surface that owns the problem is unclear
- `configure-handoff`: the handoff does not carry the fields or summary to the
  helpdesk
- `ada-custom-metrics-improve`: the cluster is a failing custom metric
- `test-and-fix`: after any change, to run the cases and fix what fails
- knowledge edit: for an information gap, draft or correct the article as a
  changeset edit, then test it
