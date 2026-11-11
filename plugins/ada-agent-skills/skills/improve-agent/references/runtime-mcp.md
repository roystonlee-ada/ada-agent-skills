# improve-agent over the Ada MCP

For anyone connected to their AI agent's Ada MCP server. Checked against the
live tool definitions and the api source on 28/10/2026, and against a sandbox
instance that day. Your host may prefix the tool names.

Contents:
- Metrics and what each one counts
- Step table
- What this route cannot do

## Metrics and what each one counts

All come from `get_ada_metric`, with `start_date`, `end_date` and optional
`filters`. Test conversations are excluded by default. Learn the filter names
with `get_available_filters` first.

| Need | `metric_type` | What it counts |
|---|---|---|
| Containment | `containment_rate`, `containment_volume` | Conversations not escalated to a human agent, over engaged conversations. An escalation counts even when no human joined. On the sandbox the volume equalled the engaged count when nothing had handed off, so the denominator is engaged |
| Automated resolution | `resolution_rate` | Resolved over resolved plus not resolved, for assessed conversations. A conversation also has to be contained, relevant, accurate and safe. This is not containment |
| CSAT | `csat_rate` | Percent satisfied across all surveys. `csat_rate_ai` counts surveys where no human joined. `csat_rate_human` counts surveys where a human joined |
| Population N | `conversation_volume_engaged` | Customers who actively engaged. `conversation_volume_opened` also counts greetings with no engagement, so it is larger |
| Handoff rate | none | Not a metric type. Use 100 minus `containment_rate`, or `conversation_volume_engaged` with the `HANDOFF IS true` filter divided by N |
| Human handle time | `avg_handle_time_agent` | Seconds with live agents after escalation, returned as `{pre, post}` phases |
| Tool errors | `api_tool_performance` | One row per API tool with `error_rate`. Excludes code tools and MCP tools |

## Step table

| Step | Tool call |
|---|---|
| Window and baseline (step 1) | `get_ada_metric` for `conversation_volume_engaged`, `containment_rate`, `resolution_rate` and `csat_rate` |
| Handoffs by reason (step 2) | Follow `review-handoffs` over the MCP. Its runtime file holds the `HANDOFFREASON` calls |
| Count a cluster fast (step 2, 5) | `get_ada_metric` with `conversation_volume_engaged` and filters, for example `HANDOFF IS true` with `HANDOFFREASON IS <code>` and `TOPIC IS <id>`. It returns one number, so no paging. Use the same dates for N. `get_conversations` with `IDS_ONLY` pages 100 at a time and gives the ids |
| Topics and intents | `list_entities` with `entity_type: topics` and `detail: full`. Use the ids in `TOPIC` and `INTENT` filters |
| Contained but not resolved | `get_conversations` with `ARSTATUS IS Not Resolved` and `HANDOFF ISNOT true` |
| Low CSAT | `get_conversations` with `detail_level: SUMMARY` and `CSATSCORE IS 1`, then `2` (or `isnegative`). SUMMARY returns the score, comment and feedback tags |
| Repeat contact, tool errors | `REPEATCONTACT IS true`; `STATUSCODE` and `ACTIONID` filters |
| Sample for the mechanism (step 6) | `get_conversations` with `SUMMARY` and the cluster's filters. Each row carries the dashboard URL. Then `get_conversation` for the transcript |
| A fix rate from a past change (sizing) | `compare_changeset_metrics` for a changeset of the same kind. Read the `verdict`, not the raw delta |
| Where a fix belongs | `get_improvement_guide`, once per session, before recommending a knowledge, coaching or playbook edit |
| Is the knowledge there | `search_knowledge` with a short title keyword |
| Is there a tool for the task | `list_entities` with `entity_type: tools`, and `entity_type: handoffs` for the destinations |
| Links | The `conversation_url` that `get_conversations` `SUMMARY` returns, shaped `https://<instance>.ada.support/insights/conversations/<id>`. Mark each link opened or ASSUMED |

## What this route cannot do

- It has no handoff-rate metric. Derive it, as in the table.
- It cannot show presence events, so it cannot show when a human joined.
- It cannot return the human's back-office lookups. Only their messages.

For any of these, the dashboard shows the conversation view and the reports.
Give the person the page and the filter to open.

If a tool blocks you, call `send_feedback` with category `stuck` or
`missing_capability`. Leave out customer details.
