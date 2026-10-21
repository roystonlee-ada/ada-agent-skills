# create-verification-skill over the Ada MCP

For anyone connected to their AI agent's Ada MCP server. Tool names checked
against `author-playbook/references/runtime-mcp.md` on 21/10/2026. Your host
may prefix the tool names.

| Step in the skill | Tool call |
|---|---|
| Doctor: instance | `get_ada_configuration` once, to confirm you are on the right agent |
| Doctor: test quota | `get_test_run_quota`. Say how many runs you are about to use, because the quota is shared |
| Doctor: the draft | `list_agent_changesets` with `include_diff: true` shows the id and what is staged |
| List saved cases | `get_test_cases` with `name_filter` set to the use case name |
| Save a case | `edit_agent_config` with `entity_type: test_case`, `operation: create`. Call it with no `fields` first to read the schema. Read `author-playbook/references/runtime-mcp.md` for the case rules |
| Run on live | `edit_agent_config` with `entity_type: test_run`, `operation: create`, `test_case_ids` |
| Run on the draft | The same call with `changeset_id` set |
| Repeat for a pass rate | Run the same call again. The MCP has no repeat option |
| Read a run | Poll `get_test_runs` (`changeset_ids` and `status_filter` narrow it) until each run is `completed`, `failed` or `timeout`. Open each chat with `get_conversation` |
| Live against draft | No compare tool. Put the live and draft verdicts for each case in one table yourself |
| Test a code tool | `run_code_tool` with sample input. Its network calls are real, so never run one that charges, cancels or deletes. `list_entities` with `entity_type: tools` finds the id |
| Backtest on traffic | `compare_changeset_metrics` once the draft has traffic. A new draft has none |
| Recompute a number | `get_ada_metric` with the same filter and window as the claim. `get_available_filters` lists the filters |

## Writes need the person

`edit_agent_config` shows a preview. Show it to the person and call again with
`confirmed: true` only after they say yes. Saving a case and starting a run are
both writes.

## What this route cannot do

- It cannot compare live and draft runs for you, or repeat a run.
- Verification never promotes or rolls out a change, even though the MCP can.
  Those steps belong to `ada-promote-changeset` and `ada-rollout-changeset`.

Say plainly in the report which steps you could not run on this host.
