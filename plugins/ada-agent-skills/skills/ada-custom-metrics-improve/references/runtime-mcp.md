# ada-custom-metrics-improve over the Ada MCP

For anyone connected to their AI agent's Ada MCP server. Your host may prefix the
tool names.

| Step | Tool call |
|---|---|
| Metrics and scorecards | `list_entities` with `entity_type: custom_metrics`, then `scorecards`. Read each metric's `direction` |
| Pass rate per metric | `get_ada_metric` with `metric_type: custom_metric_pass_rate` and the metric's `entity_id`, over the window. `scorecard_score` gives each metric in a scorecard |
| Headline rates | `get_ada_metric` with `containment_rate`, `resolution_rate`, `csat_rate` over the same window |
| Find failing chats | `get_available_filters` first. If a custom metric result filter exists, use it with `get_conversations`. If none exists, sample with `get_conversations` (`SUMMARY`) and judge each chat against the metric's wording yourself. Say you did, because that is your read and not Ada's verdict |
| Transcript and reasoning | `get_conversation` |
| Edit wording | `edit_agent_config` with `entity_type: custom_metric`, `operation: update`, and the metric's `entity_id`. Call it with no `fields` first to read the schema. Pass `subject: ai_agent` for an older metric |
| Test a fix | `get_test_run_quota`, then `edit_agent_config` with `entity_type: test_run`, `operation: create`, `test_case_ids` and `changeset_id`. Poll `get_test_runs` until each run is `completed`, `failed` or `timeout` |
| Stage a fix | `edit_agent_behavior` with `operation: describe_entity` first, then `update`. It lands on a changeset that is not live |
| Compare arms | `compare_changeset_metrics` with `start_date` on the first full day of the changeset's traffic. It returns each metric's rate with a 95% interval and a verdict, and custom metrics come back without an interval |

## Limits to say out loud

- The health table in step 2 needs pass, fail and null counts per metric. The MCP
  gives a pass rate and a chat sample, not the counts. Quote the rate with the
  sample size you read, and mark the flags you could not compute as unchecked.
- `edit_agent_config` previews every write. Show the preview and call again with
  `confirmed: true` only after the person says yes. Editing a metric changes what
  Ada scores on live chats. The test run quota is shared, so say how many runs you
  are about to use.
- A metric with `direction: higher_is_worse` reads backwards: a rising pass rate
  is a regression.
- Rollout and promote go through `ada-rollout-changeset` and `ada-promote-changeset`,
  and only when the person asks.
