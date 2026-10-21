# ada-custom-metrics-setup over the Ada MCP

For anyone connected to their AI agent's Ada MCP server. Your host may prefix the
tool names.

| Step | Tool call |
|---|---|
| Existing metrics and scorecards | `list_entities` with `entity_type: custom_metrics`, then `scorecards` |
| Use cases and handoffs | `get_ada_configuration` for the whole setup. `list_entities` with `entity_type` `playbooks` or `handoffs` |
| Themes | `list_entities` with `entity_type: topics` and `detail: full` (includes intents) |
| A sample of chats | `get_conversations` with `detail_level: SUMMARY`, a `start_date` and `end_date`, and filters from `get_available_filters`. It returns summary, resolution status and CSAT per chat. Page through every `next_cursor` or `offset` before you quote a total |
| One transcript | `get_conversation` |
| Outcome rates | `get_ada_metric` with `containment_rate`, `resolution_rate` or `csat_rate` |
| Draft metrics | `draft_custom_metrics` with a plain description of one behaviour. It returns up to 3 drafts and stores nothing. If it returns a `clarifying_question`, ask the person and call again with the answer. Read `not_drafted` for behaviours it refused and why |
| Save a metric | `edit_agent_config` with `entity_type: custom_metric`, `operation: create`. Call it with no `fields` first to read the schema. Pass the draft's `name`, `pass_description`, `fail_description`, `null_description`, `scoring_guidance`, `direction` and `intent_ids`, and add `subject: ai_agent`. Do not pass `rationale` |
| Save the scorecard | `edit_agent_config` with `entity_type: scorecard`, `operation: create`. Read the schema first. Weights must sum to 1.0 |
| Check it is active | `list_entities` with `entity_type: custom_metrics` |

## Limits to say out loud

- There is no bulk export and no backfill over the MCP. Sample chats by paging
  `get_conversations`, and say the sample is a lower bound. A new metric scores
  chats that end after it is active.
- `edit_agent_config` previews every write. Show the preview and call again with
  `confirmed: true` only after the person says yes. Saving a metric changes what
  Ada scores on live chats.
- The save runs Ada's authoring review. If it refuses, read the reason, fix the
  wording and retry. If `edit_agent_config` is refused for permissions, give the
  person the final wording and ask them to save it in the Ada dashboard.
