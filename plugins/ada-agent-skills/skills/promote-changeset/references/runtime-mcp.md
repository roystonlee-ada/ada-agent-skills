# promote-changeset over the Ada MCP

For anyone connected to their AI agent's Ada MCP server. Your host may prefix
the tool names.

| Step | Tool call |
|---|---|
| Status and the real diff | `list_agent_changesets` with `changeset_id` and `include_diff: true`. Status is `testing`, `promoting`, `promoted` or `reverted` |
| Find a changeset | `list_agent_changesets`, optionally with `status: testing` |
| Cases that touch the playbook | `get_test_cases` with `name_filter` set to the use case name |
| Run on draft and on live | `get_test_run_quota` first. Then `edit_agent_config` with `entity_type: test_run`, `operation: create`, `test_case_ids`, and `changeset_id` for the draft. Run again without `changeset_id` for live. Poll `get_test_runs` until each run is `completed`, `failed` or `timeout` |
| Read a failure | `get_conversation` on the run's conversation |
| Before and after on live traffic | `compare_changeset_metrics` once the draft has traffic |

## What the MCP cannot do

No tool promotes, reverts, or deletes a changeset. Say so, give the person the
changeset name, and send them to Changesets in the Ada dashboard to press
Promote or Roll out. Nothing is live until they do.

## Writes need the person

`edit_agent_config` shows a preview. Show it, and call again with
`confirmed: true` only after the person says yes. The run quota is shared, so
say how many runs you are about to use.
