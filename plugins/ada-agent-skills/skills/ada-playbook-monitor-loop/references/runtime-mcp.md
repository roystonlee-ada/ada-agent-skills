# ada-playbook-monitor-loop over the Ada MCP

For anyone connected to their AI agent's Ada MCP server. Your host may prefix
the tool names.

| Step | Tool call |
|---|---|
| Read a playbook and what it uses | `list_entities` with `entity_type` `playbooks`, `tools` (code, API and MCP tools), `handoffs`, `variables`. `get_ada_configuration` for the whole setup. Search knowledge with `search_knowledge` |
| Platform detail before any edit | `get_improvement_guide`, once per session |
| Recent real chats | `get_conversations` with the playbook filter (read filters from `get_available_filters`), leaving test chats out. Page through every `next_cursor` before you quote a total |
| Transcript and reasoning | `get_conversation` for the chat. The reasoning entries carry the playbook and step that sent each line |
| Custom metrics on the instance | `list_entities` with `entity_type: custom_metrics`. None means judge from the transcript |
| Ada's verdicts over a window | `get_ada_metric` with `metric_type: custom_metric_pass_rate`, and with `scorecard_score`. Read each metric's direction before you read a rate |
| Create test cases | `edit_agent_config` with `entity_type: test_case`, `operation: create`. Call it with no `fields` first to read the schema |
| Run them | `get_test_run_quota`, then `edit_agent_config` with `entity_type: test_run`, `operation: create`, `test_case_ids`, and `changeset_id` for a draft. Poll `get_test_runs` until each run is `completed`, `failed` or `timeout` |
| Stage a fix | `edit_agent_behavior` with `operation: describe_entity` first, then `operation: update`. It lands on a changeset that is not live. Read the diff with `list_agent_changesets` (`include_diff: true`) |
| Before and after on live traffic | `compare_changeset_metrics`, or `get_ada_metric` before and after a promote time |

## Limits to say out loud

- There is no timer. A pass runs when the person asks for it, so say that
  nothing is watching between your turns.
- `edit_agent_config` previews every write. Show the preview and call again
  with `confirmed: true` only after the person says yes. The test run quota is
  shared, so say how many runs you are about to use.
- No tool promotes or rolls out a change. Hand the person the changeset name
  and point them to Changesets in the Ada dashboard.
