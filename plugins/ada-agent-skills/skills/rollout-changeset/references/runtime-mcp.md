# rollout-changeset over the Ada MCP

For anyone connected to their AI agent's Ada MCP server. Your host may prefix
the tool names.

| Step | Tool call |
|---|---|
| Changeset and its status | `list_agent_changesets` with `changeset_id` |
| Active rollouts | `list_agent_changesets` with `status: testing`. If a rollout's percentage is not in the result, ask the person to read it from Changesets in the Ada dashboard |
| Sampled chats | `get_conversations` with the `CHANGESETID` filter (read the filter from `get_available_filters`). Page through every `next_cursor` before you quote a total |
| One chat | `get_conversation` for the transcript, and the reasoning entries for step and playbook ownership |
| Settled check | `get_conversation`: last update 60+ minutes old, and the last playbook has an end event |
| Metrics for the changeset arm | `get_ada_metric` with a `CHANGESETID` filter, or `compare_changeset_metrics` for both arms with intervals and a verdict per metric |
| Custom metric verdicts | `get_ada_metric` with `metric_type: custom_metric_pass_rate`. Read each metric's direction before you read a pass rate |
| Judge the whole rollout | `compare_changeset_metrics` with `start_date` on the first full day after the rollout began |

## What the MCP cannot do

No tool starts, raises or stops a sampled rollout. Do the analysis, then give
the person the exact step: open the changeset in Changesets in the Ada
dashboard, choose Roll out, and set the percent and the chat cap. For a stop,
tell them first and say why. Nothing changes for customers until they press it.

`compare_changeset_metrics` returns a verdict and a 95% interval per metric.
Report the verdict, not the raw delta, and remember that with many metrics an
occasional "better" or "worse" can be chance.
