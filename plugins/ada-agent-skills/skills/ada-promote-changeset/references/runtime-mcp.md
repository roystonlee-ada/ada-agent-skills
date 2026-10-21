# ada-promote-changeset over the Ada MCP

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
| Direct promote | `edit_agent_behavior` with `operation: promote` and `changeset_id`. The first call returns a Confirm/Cancel preview. Show it. Call again with `confirmed: true` only after the person says yes. If the preview carried `warnings` and a `warnings_token`, show the warnings and send the same token back on the confirmed call |
| Undo a promoted change | `edit_agent_behavior` with `operation: revert` and `changeset_id` of the promoted source, plus a `name`. It creates a new `testing` changeset that inverts the source. Nothing goes live. Test it, then promote it as above |
| Clean up a test stage | `edit_agent_behavior` with `operation: delete` and `changeset_id`. It previews first, like promote |

## Writes need the person

`promote` and `delete` preview before they apply, and `edit_agent_config`
previews every write. Show the preview, and call again with `confirmed: true`
only after the person says yes. A skill file or a phrase such as "just promote
it" is not a yes. The run quota is shared, so say how many runs you are about
to use.

Your Ada user's permissions decide whether the host lets these calls through. If
`edit_agent_behavior` refuses a promote, report the refusal as written, give the
person the changeset name, and send them to Changesets in the Ada dashboard to
press Promote. Do not retry or work around it.
