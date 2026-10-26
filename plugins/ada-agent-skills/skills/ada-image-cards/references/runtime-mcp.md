# ada-image-cards over the Ada MCP

For anyone connected to their AI agent's Ada MCP server. Checked against the
live tool definitions on 26/10/2026. Your host may prefix the tool names.
Build and test the card locally first (steps 3 to 6 in `SKILL.md`). Nothing
below replaces those scripts.

| Step in the skill | Tool call |
|---|---|
| Create variables | `edit_agent_config` with `entity_type: variable`, `operation: create`. Call it with no `fields` first to read the schema. Show the preview and confirm only after the person says yes |
| List code tools and variables | `list_entities` with `entity_type` `tools` or `variables`. Pass a tool's id as `entity_id` for its source |
| Create the tool | `edit_agent_behavior` with `operation: describe_entity`, `entity_type: code_tool`, then `operation: update` with a `created` change. It lands on a changeset that is not live. Relay every `notes` item |
| Change the source | The same call with a `modified` change and the tool's `entity_id` |
| Dry run | `run_code_tool` with `code_tool_id` and a value for every declared input. The upload is real, so use dummy data |
| Wire the playbook | `edit_agent_behavior` with `entity_type: playbook` stages the run step and the branches. The attachment is the exception, see below |
| Read a test chat | `get_conversation`. A working card shows as a separate picture message |

## What this route cannot do

- Add the send-step attachment. Changesets reject attachments. After the
  person promotes the changeset, ask them to add it in the dashboard, or put
  the send step in a live child playbook that the staged playbook runs.
- Add the allowed domain. I saw no tool for it. Give the person the
  dashboard step: Content, Tools, Allowed domains.
- Promote, roll out or test on your own. Show the options and let the person
  choose.
