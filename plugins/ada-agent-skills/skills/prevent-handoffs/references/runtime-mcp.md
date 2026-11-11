# prevent-handoffs over the Ada MCP

For anyone connected to their AI agent's Ada MCP server. The calls below are
the ones the chained skills checked against the live tool definitions:
`review-handoffs` (20/10/2026), `improve-agent` and `test-and-fix`
(28/10/2026), `mine-human-agent-conversations` (05/11/2026). This skill adds
no new tool. Your host may prefix the tool names.

## Steps 1 to 4: read only

| Step | Tool call |
|---|---|
| Population N, handed off H | `get_ada_metric` with `conversation_volume_engaged`, both dates, and the filter `HANDOFF IS true` for H. Test conversations are excluded by default |
| Containment and resolution | `get_ada_metric` with `containment_rate` and `resolution_rate` |
| Counts by reason (step 2) | Follow `review-handoffs` over the MCP: `HANDOFFREASON IS <code>`, one code at a time |
| Every handed-off conversation (step 2) | `get_conversations` with `detail_level: SUMMARY`, both dates and `HANDOFF IS true`. Page with `offset` and `next_offset` to the end. Each row has the `conversation_url`. Use `IDS_ONLY` per reason code to tag each id with its code |
| Read one transcript with the human replies (step 3) | `get_conversation`. Human replies are `live_agent_message` entries after the `handoff_triggered` entry, which carries `reason_code` and `reasoning.text` |
| The agent's tools, playbooks and handoffs | `list_entities` with `entity_type` `tools`, `playbooks` and `handoffs` |
| Is the knowledge there (step 5) | `search_knowledge` with a short keyword |
| Where a fix belongs (step 5) | `get_improvement_guide`, once per session, then `diagnose-conversation` over the MCP |

The `SUMMARY` rows carry no human messages. If they also carry no summary
text on your instance, the record pass in step 3 has only the intent and the
reason code: read more transcripts, and say the record pass was thin.

## Steps 5 to 7: writes

| Step | Tool call |
|---|---|
| Stage a fix | `edit_agent_behavior` with `operation: update`. First call: `name` and `summary` make the changeset; one changeset per fix. Call `describe_entity` first for the fields |
| Draft a case from a handed-off conversation (step 6) | `draft_test_case_from_conversation` with `conversation_id`. Saves nothing. 6 a minute per agent. Follow its `instructions` |
| Save the cases | `edit_agent_config`, `entity_type: test_case`, `operation: create`, after the person agrees the criteria. It previews first; call again with `confirmed: true` on a yes |
| Replay | `get_test_run_quota`, then `edit_agent_config` with `entity_type: test_run`, `operation: create`, `fields: {test_case_ids: [...]}` for live and with `changeset_id` for the fix. Poll `get_test_runs` |
| Did the replay hand off | `get_test_runs` with `test_run_id`: read the `conversation` lines for the handoff step. A run that ends in a handoff is not contained, whatever its criteria say |
| Discard a fix | `edit_agent_behavior`, `operation: remove`, with the `changeset_id`, `entity_id` and `entity_type` |
| Show the diff | `list_agent_changesets` with `changeset_id` and `include_diff: true` |
| Promote | Not here. `ada-promote-changeset` |

## What this route cannot do

- No call returns every handed-off conversation with its reason in one go.
  Page `get_conversations`, and tag ids per reason.
- No call shows when a human joined. Read the `live_agent_message` order.
- `edit_agent_config` is missing from some agents' tool lists. Then cases can
  be drafted but not saved, so stop at the proposed fix list and say why.

If a tool blocks you, call `send_feedback` with category `stuck` or
`missing_capability`. Leave out customer details.

## Conversation links

`https://<handle>.ada.support/insights/conversations/<id>`. Take the handle
from a `conversation_url` in the `SUMMARY` rows.
