# Sizing a recommendation

Every recommendation shows five things: the cluster size in conversations, its
share of the population, the metric it moves, an estimated lift range, and the
arithmetic. The size comes from counting the whole window. A sample of a few
conversations confirms the mechanism. It never sets the size.

Contents:
- Terms
- Count the cluster
- Lift on containment
- Lift on automated resolution
- Lift on CSAT
- Lift on a custom metric
- Lift on human handle time
- Choose the fix rate
- Overlap and ranking
- Show the arithmetic

## Terms

- N: engaged conversations in the window, test users excluded. Containment is
  measured over this population, so every share uses it.
- c: conversations in the cluster, counted over the whole window.
- share: c divided by N, as a percentage. Also give c divided by all escalated
  conversations when the cluster is a handoff cluster.
- r: the fix rate, the fraction of the cluster the fix would keep from handing
  off. A range, low to high.

## Count the cluster

1. Count c with the population filter, not by reading conversations. The
   runtime file names the call. Use the same window and the same test-user rule
   as N.
2. Split a big reason into tasks by topic or intent, and count each part the
   same way. A reason code is too coarse to size a fix. When the generated
   topics are empty, cut clusters by `primary_intent_name` from the search
   results.
3. A conversation with several handoff attempts counts under each of their
   reasons. Dedupe by conversation id before you add counts across reasons or
   clusters.
4. Assign each conversation to one cluster. Where two clusters overlap, give the
   shared conversations to the first class that applies in
   `situation-classes.md`. Count a conversation once in the ranking.
5. A count of 0 on the filter does not prove the cluster is absent. Handoffs
   with no recorded reason match no reason filter, so a reason count is a lower
   bound. Say so.

## Lift on containment

Containment lift in points = 100 x c x r / N

Give it for r low and r high. Example with made-up numbers: c = 240, N = 4,000,
r from 0.4 to 0.8. Low: 100 x 240 x 0.4 / 4,000 = 2.4 points. High: 100 x 240 x
0.8 / 4,000 = 4.8 points. Range: 2.4 to 4.8 points.

For an information-gap cluster, size the two parts apart. The handed-off part
moves containment, so size it with the containment lift. The contained but not
resolved part moves automated resolution, so size it with the resolution lift.
Do not add one part's count to the other's formula.

Classes where this applies: information gap, system action with an API, design
or routing, agent-resolvable. For a system action with no API, a policy cluster
and a judgment cluster, the containment lift is 0. Write 0. Do not stretch it.

## Lift on automated resolution

Automated resolution lift in points = 100 x c x r x q / A

- A: conversations assessed for resolution in the window, which is resolved
  plus not resolved, each counted from search. Observed on a real instance: the
  platform's resolution rate matched resolved / (resolved + not resolved), not
  resolved / N. Unclear conversations are in neither term. Use N only when you
  cannot count A, and say so.
- q: the share of the newly contained conversations that would also count as
  resolved. Use the automated resolution rate of the same topic's contained
  conversations. Use the agent's overall rate when you do not have it, and say
  so.

Handed-off conversations are not resolved, so each one the fix keeps in the
agent is already in the denominator and moves from not resolved to resolved only
at rate q. That is why this lift is smaller than the containment lift.

## Lift on CSAT

Only surveyed conversations count, so size CSAT on the surveyed part.

1. Count the cluster's surveyed conversations, s.
2. If s is under 30, say the CSAT effect is not measurable on this window and
   give direction only.
3. Otherwise take the CSAT rate for the cluster's conversations that handed off,
   and the CSAT rate for contained conversations on the same topic. The gap is
   the most the fix can move a kept conversation.
4. CSAT lift in points = 100 x (s x r x gap) / S, where S is all surveyed
   conversations in the window and gap is a fraction.

Report it as an estimate with the gap and s shown.

## Lift on a custom metric

Read the metric's direction first. On a lower-is-better metric, a "pass" is the
bad behaviour.

- fails in cluster = f, conversations the metric applied to = M
- Pass rate lift in points = 100 x f x r / M, in the good direction

Custom metric counts include test conversations on some routes. The runtime file
says which. Exclude them or say they are in.

## Lift on human handle time

Used for the collect-and-summarize fix, where containment does not move.

- Baseline: the post-handoff handle time for the cluster, from the metric the
  runtime file names.
- Bound the saving by the human replies. Count the share of the human agent's
  turns that only asked for fields the agent could have collected. That share
  caps the saving. Without the human replies, give the cluster size and the
  baseline, and write "saving not estimated".

## Choose the fix rate

r is an assumption until you measure it. Use these defaults and mark them
ASSUMED:

| Fix | r low | r high |
|---|---|---|
| Add or correct an article | 0.3 | 0.7 |
| New end-to-end resolution on an existing API | 0.4 | 0.8 |
| Routing, trigger or loop fix | 0.5 | 0.9 |
| Playbook or instruction gap | 0.3 | 0.7 |

Narrow the range when you have evidence:
- a test run of the fix on cases built from this cluster's real conversations
  gives r directly
- a past change of the same kind on this agent, read with the changeset
  comparison, gives r for that kind of fix

Never set r from the two or three conversations you read. They were chosen to
show a mechanism, so they flatter it.

## Overlap and ranking

- Rank by the midpoint of the lift on the metric the person cares about most.
  Ask which metric if it is unclear, and say what you chose.
- Lifts from clusters that share conversations do not add. State which
  recommendations overlap.
- Do not add containment lift to automated resolution lift to CSAT lift. Show
  each on its own line.
- A big cluster with a low r can outrank a small cluster with a high r. That is
  the point of sizing by the population.

## Show the arithmetic

Write each estimate as a line the reader can recompute: the inputs, the formula,
the range. For example: "c = 240 of N = 4,000 (6.0 percent). Containment lift =
100 x 240 x r / 4,000. r 0.4 to 0.8 (ASSUMED) gives 2.4 to 4.8 points."
