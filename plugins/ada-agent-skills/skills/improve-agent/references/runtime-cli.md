# improve-agent on the command line

For anyone with `adacli`. Checked against `--help`, the adacli source and
read-only runs on four real instances on 28/10/2026. Commands are `adacli
<instance> <group> ...`. Sign in with `adacli <instance> login` first.

Contents:
- Window and search behaviour
- Metrics and what each one counts
- Containment check
- Step table
- Human-agent messages after a handoff
- What this route cannot do
- Inside Ada Architect

## Window and search behaviour

- Handoff reasons start on 07/10/2026. When 28 days back crosses that date,
  use `--start 2026-10-07 --end <today>` (YYYY-MM-DD), not `--since 28d`. Use
  the floor date as `--start` for any longer window too.
- A search returns one page, and the JSON `total` is the full match count. For
  a cheap total, ask for a small page: `--size 1`. `--size` is capped at 500.
- `--limit` needs `--all`. The CLI refuses `--limit` on its own.
- `--all` writes progress text (`Fetching...`) to stderr in the source. A tool
  that merges stderr into the output shows that text before the JSON. Drop
  stderr (`2>/dev/null`) before you parse.
- A search with zero matches prints plain text, not JSON, even with `--json`
  (observed). The text reads "No conversations matched." and warns that the
  endpoint also returns empty on its own read failures. Check for the line
  before you parse, and retry once before you report a zero.

## Metrics and what each one counts

| Need | Command | What it counts |
|---|---|---|
| Overall automated resolution and CSAT | `analytics summary --since 28d --json` | `resolution_rate` and `csat_rate` only. No containment, no handoff rate |
| Per topic: volume, automated resolution, containment, CSAT | `analytics topics --since 28d --json` | Per topic: `count`, `resolution_rate`, `resolution_rate_opportunity`, `containment_rate`, `csat_rate`, `csat_count`. Containment here is the share of the topic's conversations with no handoff. Whether the denominator is engaged conversations, as on the MCP, is ASSUMED, so confirm it with the counts below |
| Population N | `conversations search --start <date> --end <date> --size 1 --json` | `total` is every non-test conversation. Test users are left out unless you pass `--test-users`. Do not use `--filter ENGAGED:IS:<value>` to split engaged from not: it returned the same count for true and false (observed). So N here is not engaged-only. Say so, and quote the dashboard's engaged count if the person has it. OPEN: a CLI route to the engaged count |
| Handoff volume | `conversations search --handoff --start <date> --end <date> --size 1 --json` | Conversations escalated. Divide by N for the rate. Containment is then 1 minus that |
| Custom metric results | `custom-metrics conversations <metric_id> --result fail --start YYYY-MM-DD --end YYYY-MM-DD --json` | Conversations by result. It includes test conversations, because the pass rate counts them. No command returns a pass rate, so count `pass` and `fail` and divide. Read `direction` in `custom-metrics get <id> --json` first: on a higher-is-worse metric a pass is the bad behaviour |
| Scorecard results | `scorecards conversations <scorecard_id> --result fail --metric <metric_id> --json` | Conversations by scorecard result |

Containment and automated resolution differ. Containment is not escalated.
Automated resolution also needs the conversation to be relevant, accurate and
safe.

## Step table

| Step | Command |
|---|---|
| Window and baseline (step 1) | `analytics summary`, `analytics topics`, and the counts above |
| Handoffs by reason (step 2) | Follow `review-handoffs` on the command line. `conversations handoff-reasons --start <date> --end <date> --samples 5 --with-reasoning --json` counts conversations per reason with sample ids and short reasoning text. When the account refuses `handoff-reasons`, run `conversations search --handoff --handoff-reason <code> --start <date> --end <date> --size 1 --json` once per code and read each `total`. The codes are `tool_failed`, `end_user_requested`, `out_of_scope`, `tool_unavailable`, `knowledge_unavailable`, `issue_unresolved`, `handoff_configured`, `other`, `system_failed` and `unclassified` |
| Split a reason by task (step 2, 5) | `conversations handoff-reasons --handoff-reason <code> --topic <topic> --count --json`, or `--playbook <id>`. For any other cut, `--filter TYPE:OP:v1,v2[:item]`, for example `--filter INTENT:IS:<id>` |
| Count a cluster (step 5) | `conversations search --handoff --handoff-reason <code> --topic <topic> --start <date> --end <date> --size 1 --json` and read `total`. One conversation with two reasons counts under both |
| Contained but not resolved | `conversations search --resolution not-resolved --filter HANDOFF:ISNOT:true --json` |
| Low CSAT | `conversations search --csat 1 2 --json` |
| Custom metric failures | `conversations search --custom-metric <id> --metric-result fail --json` |
| Ids for sampling | `conversations search ... --all --limit 200 --json` |
| Read a sample (step 6) | `conversations details <id> --json` for the summary, resolution and handoffs. `conversations log <id>` for messages and reasoning together. `conversations handoffs <id> --json` for each attempt's target, outcome, reason code and reasoning. `conversations diagnose <id> --json` names the failure surface |
| Topics and intents | `topics list --json`, and `topics class --help` for intents. `analytics topics` ranks topics by volume. Use the values in `--topic` and `--intent` |
| Is the knowledge there | `knowledge list`, and `knowledge probe` to see which articles rank for a customer's question |
| Is there a tool for the task | `actions list`, `code-tools list`, `mcp list` (see `mcp --help`). `handoffs list` for the destinations |
| A fix rate from a past change | `changesets compare <id>` for a promoted or rolled-out change of the same kind, over a date range. `testing runs` for a test run on cases from the cluster |
| Links | `https://<instance>.ada.support/insights/conversations/<id>`, built from the id. Mark each link opened or ASSUMED |

## Containment check

Before you quote containment, check that every handoff is counted. A handoff
action block with Count as Handoff (`is_handoff`) off is invisible to the
`--handoff` filter.
1. Sample logs: `conversations log <id>` for about 20 conversations per channel.
   Count the conversations with a handoff step.
2. Count the same channel with `conversations search --handoff --channel <id>
   --start <date> --end <date> --size 1 --json` and read `total`.
3. Split N by channel the same way, without `--handoff`.
4. If the logs show handoff steps that the `--handoff` count does not, the
   containment figure is too high. On one real instance, email handoffs ran with
   Count as Handoff off and the reported containment was about 27 points too
   high. Name the channel and send the fix to `configure-handoff`.

## Human-agent messages after a handoff

Two commands show the return path when `conversations handoffs <id>` is refused:
- `conversations details <id> --json`: the `handoffs` array has the target,
  status and reason code of each attempt.
- `conversations transcript <id> --json`: presence events (`agent_arrival`,
  `agent_depart`, `live_chat_end`) and agent messages. An agent message has a
  `source` of agent and an `agent_info` block with the name (the source also
  accepts `by`). `conversations log <id> --json` shows the same messages with
  the reasoning.

Presence-only lines are not replies. Count a human reply only when an agent
message is present. Ticket, case and email handoffs return nothing to Ada by
design (observed on Zendesk Ticketing, a Salesforce case, a Gorgias ticket and
email), so a handed-off conversation with no agent message is normal there.

`conversations export --transcripts --json -o <file>` writes full transcripts
for a window, with a bound set by `--limit`. Use it to read human replies across
a cluster, then join on the conversation id.

If a handed-off conversation has no agent message after the handoff, follow
`human-agent-learning.md`: ask for the helpdesk export, and say so in the report.

## What this route cannot do

- `analytics summary` returns no containment, no handoff rate and no CSAT split.
  Derive them from counts.
- No command returns a custom metric pass rate. Count the results. When the
  read fails with FORBIDDEN or 403 "Feature not available", report the baseline
  as not readable and point to the dashboard (Analytics > Metrics). Do not
  report it as zero.
- No command returns post-handoff handle time. Take it from the first and last
  agent message timestamps in the log.
- `custom-metrics conversations` includes test conversations. Say the numbers
  include them.

The dashboard has the Reports pages for these. Give the person the page and the
filter to open.

## Inside Ada Architect

Architect has helpers beside the plain commands: `ada-export <instance> --since
28d --exclude-test-users --handoff-reasons` counts handoffs by reason, and
`ada-why <instance> <id>` reads one conversation's reasoning. The plain commands
above give the same answers and work anywhere.
