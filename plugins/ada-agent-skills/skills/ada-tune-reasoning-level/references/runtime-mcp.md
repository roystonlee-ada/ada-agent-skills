# ada-tune-reasoning-level with the Ada MCP

For a session with the Ada MCP tools (`get_ada_configuration`, `list_entities`, `edit_agent_behavior`).

| Step in the skill | Tool call |
|---|---|
| Inventory every in-scope step | `get_ada_configuration` for the playbook list (page with `next_cursor`), then `list_entities` with `entity_type: "playbooks"` and `entity_id` for each V2 playbook. Read each step's `type`, `ask_mode`, `instruction` and `reasoning_level`. |
| Find past inputs for a step | `get_conversations` to find chats that ran the playbook, then `get_conversation`. The `user_message` entries hold what the customer said. The `playbook_v2_step` entries hold each step's `step_id`, `outcome_status` and `reasoning`. The result has no variable values, so judge a SET from the next message the agent sent. |
| Learn the editable fields | `edit_agent_behavior` with `operation: "describe_entity"`, `entity_type: "playbook"`, `change_type: "modified"` |
| Stage the change | `edit_agent_behavior` with `operation: "update"`, a short `name`, a one-sentence `summary`, and `changes: [{"entity_type": "playbook", "change_type": "modified", "entity_id": "<id>", "fields": {"sections": [...]}, ...}]`. Set `enabled: true` in `fields` if the playbook is on, so a test run exercises the edit. |
| Check the level landed | `list_agent_changesets`, then read the changeset's playbook fields |
| Run saved cases on the draft | `get_test_cases`, then `edit_agent_config` with a `test_run` pinned to the changeset's `changeset_id`. Read results with `get_test_runs`. |
| Compare against live | `compare_changeset_metrics` after a rollout, `get_test_runs` for cases |
| Hand over | The person decides. `edit_agent_behavior` supports `promote`, `set_rollout`, `stop_rollout` and `revert`, each with its own confirmation. Do not call them yourself. |

## Gotchas

- `reasoning_level` is valid on a generative SET (it has an `instruction`) and on a reasoning ASK. The tool's own description says the same. It has no effect on an exact SET (a literal `value`), an exact ASK or a send step.
- When you rewrite `sections`, send every step's `reasoning_level` back as you read it. The tool warns about this, and a dropped field resets the step to Normal.
- Send each section and step `id` back unchanged. Mint a 24-character hex id only for a new step.
- Preserve every `note` step and every send-step `attachments` exactly. A changeset cannot edit an attachment.
- Staging runs the same checks as the dashboard. An invalid level (`High`, `turbo`) rejects the whole changeset at stage time.
- `get_conversation` stamps every `playbook_v2_step` entry with `created_at`, so the gap between two steps gives a rough step time. It has no variable values and no model name. Use the `adacli` route in `runtime-cli.md` when you need the exact value a SET wrote.
