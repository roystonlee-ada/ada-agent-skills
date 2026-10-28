# troubleshoot over the Ada MCP

For anyone connected to their AI agent's Ada MCP server. Checked against the
live tool definitions on 28/10/2026, with read calls only on a sandbox
instance. Your host may prefix the tool names.

## Reads the MCP can do

| Need | Tool call |
|---|---|
| Which channels exist | `list_entities` with `entity_type: channels`. It returns id, name, type (native or custom), description and modality. |
| Knowledge source state | `list_entities` with `entity_type: knowledge_sources`. It returns id, name, external_id, status, last_sync and metadata. A non-null status means the source is being deleted or the deletion failed. |
| MCP server connections the agent uses | `list_entities` with `entity_type: mcp_server_connections` (status, auth type, enabled, tool count) |
| The agent's tools | `list_entities` with `entity_type: tools` |
| Agent name, company description, playbook summaries, custom instructions | `get_ada_configuration` |
| Changesets | `list_agent_changesets`. Filter with `status` (testing, promoting, promoted, reverted). Pass `changeset_id` with `include_diff: true` for one changeset's before and after. |
| Find a knowledge article by title | `search_knowledge` |
| Entity fields that a changeset can set | `edit_agent_behavior` with `operation: describe_entity` and an `entity_type`. It changes nothing. |

## Changes the MCP can make

`edit_agent_behavior` stages on a changeset. These entity types are
supported: knowledge_article, custom_instruction, playbook, api_tool,
code_tool, mcp_tool, mcp_server_connection, coaching, process.

- `update` adds edits to a changeset. Omit `changeset_id` and pass `name` to
  start one.
- `revert` with a promoted `changeset_id` and a `name` creates a new testing
  changeset that inverts it. Nothing goes live. Only one testing revert per
  source is allowed.
- `delete` and `promote` return a preview first. Show it to the person and
  call again with `confirmed: true` only after they approve. Hand `promote`
  and `set_rollout` to `ada-promote-changeset` and `ada-rollout-changeset`.
  This skill never promotes.

`edit_agent_config` covers test_case, test_run, topic, intent,
custom_metric, scorecard, glossary_term, knowledge_source and variable. Those
apply live with no changeset. Preview each one and get a yes first.

## What the MCP does not reach

No tool in the live list covers these. Say so plainly and give the dashboard
path from the runbook.

- Email inbox, sender address or forwarding setup. `list_entities` on
  channels shows only name, type and modality.
- Team members, roles, SSO and session limits.
- API keys and webhooks.
- The audit log, the Data Export API, end-user deletion and retention.
  (`get_conversations` reads conversations but is not the export API.)
- A snapshot export or import.
- Region and instance lookup.

For each of these the person works in the dashboard, or uses adacli where it
has a command (`references/runtime-cli.md`). Record the current values by hand
before any change, because no changeset or snapshot covers them.
