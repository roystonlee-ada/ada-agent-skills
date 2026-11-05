# ada-report over the Ada MCP

For anyone connected to their AI agent's Ada MCP server. Checked against the live
tool definitions on 28/10/2026. Your host may prefix the tool names. Every step
here only reads.

| Step in the skill | Tool call |
|---|---|
| Headline metrics | `get_ada_metric` with `start_date` and `end_date`, one call per `metric_type`: `resolution_rate`, `containment_rate`, `csat_rate_ai`, `conversation_volume_opened`, `conversation_volume_engaged`, `avg_handle_time`. Run the same calls for the equal period before. Call `get_available_filters` first when you filter |
| Topic volumes and how each resolves | `list_entities` with `entity_type: topics` for ids, then `get_ada_metric` with `conversation_volume_engaged` and `resolution_rate`, each with a `TOPIC` filter, one topic per call. Rank by volume |
| Tool and quality measures (optional) | `get_ada_metric` with `api_tool_performance` for lookups that error or run slow. `custom_metric_pass_rate` and `scorecard_score` when the agent has them: read each metric's direction before you describe a rise as good |
| Conversations to quote | `get_conversations` with `detail_level: SUMMARY`, both dates, and a filter for the outcome you want (resolved, handed off, low or high satisfaction). The summary gives the inquiry, resolution status and satisfaction, so you can choose before you read |
| Read a conversation in full | `get_conversation` for the transcript with playbook events, actions, knowledge searches, handoffs and coaching. Those events are the signals `ada-in-action.md` maps to notes. Transcripts are long: read three to five |
| What the agent has (to name playbooks, actions) | `get_ada_configuration`, then `list_entities` with `entity_type: playbooks` or `tools` for one item |
| Interview choices | The host's question tool when it has one, otherwise numbered options in chat |

Notes:
- Test conversations are excluded by default. Leave them out.
- Dates are `YYYY-MM-DD`. Use the first and last day of the period, and give the
  same number of days to the prior period.
- `get_conversations` pages with `offset` and `next_offset`. `get_ada_configuration`
  and the list tools page with `cursor`. Read every page before you quote a count.
- `conversation_summaries` returns up to 250 records with a dashboard link. Use it
  to fill `url` on a transcript.
- Resolution and reason are empty until a conversation has been assessed. Do not
  pick a recent conversation for the "resolved" example without checking.
- No tool draws or exports the report. `scripts/report.py` renders the HTML, and
  the person prints it to PDF from the browser.
