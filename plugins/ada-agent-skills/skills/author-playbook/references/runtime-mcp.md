# author-playbook over the Ada MCP

For anyone connected to their AI agent's Ada MCP server. Checked against the
live tool definitions on 20/10/2026. Your host may prefix the tool names.

| Step in the skill | Tool call |
|---|---|
| The approved design | The person approved the board in chat. Build from the last round you showed and keep its text in the conversation, because nothing saves it |
| List saved cases | `get_test_cases` with `name_filter` set to the use case name. Reuse a case whose name or opening line matches the scenario |
| Save a case | `edit_agent_config` with `entity_type: test_case`, `operation: create`. Call it with no `fields` first to read the schema. Required: `name` ("<Use case>: <scenario>"), `user_message` (the customer's first turn, 1024 characters at most), `success_criteria` (a list), `language`, `scenario_goal`. See the case rules below |
| Record the use case | No memory and no tool. Put the use case key, playbook names and case ids in your final message so the person can paste them into the next session |
| Platform detail | `get_improvement_guide`, once per session. It says where each kind of fix belongs |
| List code tools, actions, playbooks | `list_entities` with `entity_type` `tools` (code, api and MCP tools, with ids), `playbooks`, `handoffs`, `variables`, `channels`. Pass a code tool's id as `entity_id` for its source |
| Test a code tool | `run_code_tool` with sample input, before a playbook calls it. Its network calls are real, so never run one that charges, cancels or deletes |
| Stage the draft | `edit_agent_behavior` with `operation: describe_entity` and `entity_type: playbook` first, then `operation: update` with `changes` and a `name` and `summary` for the changeset. It lands on a changeset that is not live. Relay every `notes` item in the reply. Read the id and the diff with `list_agent_changesets` (`include_diff: true`) |
| Check routing | No tool tests routing alone. Run the cases and read which playbook ran in `get_conversation` |
| Run the cases | `get_test_run_quota` first. Then `edit_agent_config` with `entity_type: test_run`, `operation: create`, `test_case_ids`, and `changeset_id` for the draft. Run it again without `changeset_id` for live. Poll `get_test_runs` (`changeset_ids` filter, `status_filter`) until each run is `completed`, `failed` or `timeout`, and open the conversations with `get_conversation` |
| Report | A table: case, live, draft, a one-line note, links to both conversations. Add `compare_changeset_metrics` once the draft has traffic, which a new draft will not |

## Case rules

- A test case holds the first customer message and a goal. A simulated
  customer then plays out the whole conversation from `scenario_goal`, so
  later scripted turns do not exist. Put what the customer gives only when
  asked, and what they do not know, in `scenario_goal`.
- Write `success_criteria` as outcomes for the customer. Add each "must not"
  from the design as its own criterion, such as "The agent does not promise a
  refund."
- Use fake values of the same shape for every personal detail and credential.
- Say in `external_systems` how each system the playbook calls behaves, with
  the identifiers the playbook reads. Where a variable would let the playbook
  skip a lookup, set it in `variables` or the test never checks the lookup.
- Leave `changeset_id` off a regression case. Set it only for a case that
  verifies one unpromoted change and never runs live.

## Writes need the person

`edit_agent_config` shows a preview. Show it to the person and call again with
`confirmed: true` only after they say yes. The run quota is shared, so say how
many runs you are about to use. Do not start a test run, a rollout or a
promote on your own after staging. Offer them and let the person choose.

Say plainly in the report which steps you could not run on this host.
