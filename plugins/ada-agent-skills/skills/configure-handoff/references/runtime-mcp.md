# configure-handoff over the Ada MCP

For anyone connected to their AI agent's Ada MCP server. Checked against the
live tool definitions on 28/10/2026 and a read-only run on a sandbox
instance. Your host may prefix the tool names.

| Step | Tool call |
|---|---|
| List handoffs | `list_entities` with `entity_type: handoffs`. Returns id, name, description, `is_active`, and `availability_rules` when a rule exists |
| Read availability rules | The same call. `availability_rules: null` means a rule exists that the tool cannot show. Do not overwrite it |
| Find channels | `list_entities` with `entity_type: channels` |
| Find variable ids for a rule | `list_entities` with `entity_type: variables`, with `name_filter` or `scope: oauth` |
| Find playbooks that run a handoff | `list_entities` with `entity_type: playbooks` and `entity_id`. A step with `target_type: handoff` carries the handoff id |
| Count handoff outcomes | `get_conversations` with `detail_level: IDS_ONLY`, both dates, and a `HANDOFF` filter (`IS`, `true`). Add `CHANNEL` to narrow |
| Read one handoff attempt | `get_conversation`. The transcript holds the handoff event with its target, outcome and reason |
| Include test conversations | Add the `ISTESTUSER` filter. They are excluded by default |
| Simulate the trigger | `simulate_conversation`. Handoff blocks are replaced by a mock, so nothing reaches the helpdesk |
| Check a playbook change | `list_agent_changesets`, and `edit_agent_behavior` with `operation: update` for a playbook that routes to a handoff |

## What this route cannot do

- It cannot read a handoff's block tree, its integration, or whether an
  integration is connected or enabled. `list_entities` returns name,
  description, active flag and rules only. Use adacli, or the dashboard at
  Config > AI AGENT > Handoffs > Integrations.
- It cannot create or edit a handoff, an integration or a schedule. The
  `entity_type` lists of `edit_agent_behavior` and `edit_agent_config` hold
  no handoff, integration or schedule. Give the person the dashboard path,
  or use adacli for the handoff itself.
- It cannot read Ada schedules (Off hours > Schedules). Use the dashboard.
  Read the Scheduled block in the handoff through adacli.

## Notes

- `simulate_conversation` is a single turn. A simulation can show that the
  agent offers the handoff. It cannot show a connection, a queue or a return.
  That the tool sets the simulated flag is read from its description and the
  code that swaps the block. Treat a live helpdesk side effect as ASSUMED
  absent, and say so.
- A test run uses the same mock path. ASSUMED.
- `get_conversations` has a `HANDOFF` filter and a `HANDOFFREASON` filter.
  Reason counts belong to `review-handoffs`.
- If a tool blocks you, call `send_feedback` with category `stuck` or
  `missing_capability`, and give the person the dashboard step.
