# revise-playbook over the Ada MCP

For anyone connected to their AI agent's Ada MCP server. Checked against the
live tool definitions on 20/10/2026. Your host may prefix the tool names.

| Step in the skill | Tool call |
|---|---|
| Read the live playbook (do this first) | `get_ada_configuration` lists playbooks as a summary only. Pass the playbook id to `list_entities` with `entity_type: playbooks` and `entity_id` for the steps, paging with `cursor`. Read every playbook it runs or that routes into it |
| Load saved cases (do this second) | `get_test_cases` with `name_filter` set to the use case. Keep every case that touches it |
| The use case's record | Cases named "<Use case>: <scenario>" are the nearest record. Otherwise ask the person |
| Baseline for a handoff cut | The counts from review-handoffs (`get_conversations` with `HANDOFFREASON IS <code>`), saved in your message with the window |
| Send the board again | Put the ADA-DESIGN block in a fenced code block with the same `work` and a new `round`, then write each changed scenario as a readable transcript. Nothing draws it |
| Wait for Approve | The person writes "approved", "approve" or "build it" in chat |
| Check old cases against the board | Compare each case from `get_test_cases` (opening line and `success_criteria`) with the approved board. A case the board no longer matches goes to the person with the change you would make, not into the run. Update one with `edit_agent_config` (`test_case`, `update`) after they agree |
| Stage the rebuilt flow | `edit_agent_behavior` with `operation: describe_entity`, then `update`. It lands on a changeset that is not live. Read the id and the diff with `list_agent_changesets` (`include_diff: true`). Call it only after Approve, unless the change is the one-step wording fix |
| Run the whole set on draft and live | `get_test_run_quota` first. Then `edit_agent_config` with `entity_type: test_run`, `operation: create`, `test_case_ids`, and `changeset_id` for the draft. Run it again without `changeset_id` for live. Poll `get_test_runs` until each run finishes, then open the conversations with `get_conversation` |
| Show the effect | `compare_changeset_metrics` once the change has traffic. It reports a verdict per metric, so quote the verdict, not the raw delta |
| The updated use-case record | Put the key, playbook names and case ids in your final message |

## Writes need the person

`edit_agent_config` shows a preview. Show it and call again with
`confirmed: true` only after the person says yes. Say how many test runs you
are about to use. Never promote, start a rollout or stop one on your own:
offer `edit_agent_behavior` `set_rollout` or `promote` and let the person
choose. A promote shows its own Confirm or Cancel preview first.

If you could not run the cases, say that first in the report.
