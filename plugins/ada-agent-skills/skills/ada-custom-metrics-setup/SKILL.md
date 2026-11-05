---
name: ada-custom-metrics-setup
description: >
  Propose a first set of custom metrics for an Ada AI Agent that has none. Reads
  the agent's setup, topics and real transcripts, uses the business's vertical
  (airline, ecommerce, fintech, telecom, travel, marketplace, software) as a
  prior for what customers care about, interviews the person where the evidence
  is thin, then drafts metrics and a scorecard for approval. Use when someone
  says "set up custom metrics", "this agent has no custom metrics", "what should
  we measure", "propose metrics for the new agent", "draft a scorecard", or "CSAT
  is too thin, what else can we score", even if they never say "custom metrics".
---

# Custom metrics setup

Custom metrics give every ended chat a verdict, where CSAT covers a small share
of chats. A metric is worth creating only if Ada's judge can score it from the
transcript and someone would act on a fail. So start from evidence, use the
vertical as a prior, and ask the person only what the evidence cannot answer.

Reviewing metrics that already score, or fixing the agent from them, belongs to
`ada-custom-metrics-improve`.

## 0. Pick the runtime

Each step names what to do, not a command. Read one file for how:
- Ada MCP tools present (`get_ada_configuration`, `draft_custom_metrics`) →
  `references/runtime-mcp.md`
- `adacli` on the path, or you are inside Ada Architect →
  `references/runtime-cli.md`

Read `references/metric-quality.md` before you write any wording.

## 1. Preflight

List the agent's custom metrics and scorecards.
- Active metrics exist: say so and offer `ada-custom-metrics-improve`. To add to the
  set, continue and count the slots left (cap 20 per agent).
- The call is refused: custom metrics are not turned on for this agent. Say so and
  stop. Nothing scores until Ada turns them on.
- None exist: continue.

## 2. Learn the agent

Gather before you ask anyone anything.
- **Setup:** the use cases (playbooks), handoff rules, languages and channels.
- **Themes:** the topics report for the last 30 days, and any defined topics and
  intents.
- **Transcripts:** a recent sample of ended chats, with their outcome and CSAT
  where it exists.
- **Customer voice:** anything the person shares about what the business cares
  about.

Fewer than about 100 ended chats cannot rank themes. Say so, lean on setup and
vertical, and mark every metric ASSUMED.

## 3. Read the chats

Sample across the top topics, handoffs and non-handoffs, high and low CSAT where
any exists, and each language. About 40 chats is enough. Read each one and note
what a good human agent would have done differently.

Cluster the notes into themes: where customers get stuck, what they ask that the
agent cannot do, what they complain about, and which rules the agent must hold.
Keep 2 to 3 full conversation URLs per theme
(`https://<instance>.ada.support/insights/conversations/<id>`), marked opened or
ASSUMED.

## 4. Pick the vertical prior

Infer the vertical from the setup and the chats, then read the matching section
of `references/verticals.md`. It lists what customers in that vertical usually
care about, candidate metrics, and what the judge cannot see. It is a prior. A
metric with no support in this agent's chats or the person's stated rules is
dropped. A theme the list lacks is still a candidate. For an agent that spans
verticals, use each section for its own use case.

## 5. Interview where evidence is thin

Answer facts from steps 2 to 4. Ask only decisions and facts that live in the
person's head. Batch up to 4 questions per message. Explain each option, and give
a recommendation and a reason on each. Ask when:
- The vertical is unclear or mixed.
- The goal is unknown: containment, resolution quality, brand voice, compliance
  or cost.
- A rule exists but no chat shows it (refund limits, regulated wording).
- "Resolved" is ambiguous, for example whether a handoff on a request that needs
  a person counts as good.
- The sample is too small or skewed to trust a theme.
- Two candidate metrics overlap and only the owner knows which one they will act on.
- Nobody owns the fails of a metric yet.

Skip the interview when the evidence settles every point.

## 6. Draft the set

Draft 8 to 12 metrics, which leaves room under the cap. Mix three families:

| Family | Example |
|---|---|
| Behaviour defects, any agent | Repeated replies, re-asking, no way forward |
| Outcome, any agent | Request resolved end to end, question answered |
| Vertical or business rules | A fare rule quoted correctly, order status given before a refund offer |

For each metric write: name, pass, fail, null and scoring guidance, the theme it
traces to, the conversation URLs, the surface that owns a fix (playbook,
knowledge, coaching, handoff), then a recommendation and reason.

Drop or reword any metric that needs tool calls, knowledge text, variables or
handoff events. The judge cannot see them, so it guesses.

## 7. Dry-run the wording

Read each sampled chat against each draft and note pass, fail or null. Expect
some of each. A metric at 0% or 100% fail on the sample has bad wording or no
signal, so rework it. Ada's own judge may still read the wording differently, so
step 9 checks live traffic.

## 8. Get approval

Show the set as a table: metric, evidence, dry-run rates, weight and the open
decisions. Mark it "Proposed, not built". Ask the person to approve, drop some or
revise. Create nothing before a yes.

## 9. Create and watch

After approval, create the metrics and one scorecard as the runtime file says.
Weights sum to 1.0 (equal weight is 1/N, with one nudged for rounding). Check each
metric shows as active, because draft metrics do not score.

Let the set score for about 2 weeks. Then run `ada-custom-metrics-improve`. It
spot-checks 10 fails per metric and trusts a metric at 9 of 10 real defects. Until
then no metric drives a fix.

## 10. Report

End with: the vertical used, the metrics created in plain words, the evidence
count behind each, what is ASSUMED, the interview answers that shaped the set,
and the date to review. Frame gaps as coverage opportunities, never as failures.
