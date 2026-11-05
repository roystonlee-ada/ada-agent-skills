# mine-human-agent-conversations over the Ada MCP

For anyone connected to their AI agent's Ada MCP server. Filter and metric names
come from the `improve-agent` runtime file, checked against the live tool
definitions and the api source on 28/10/2026. `get_conversations` and
`draft_test_case_from_conversation` were run on a sandbox instance on
05/11/2026. That instance had no human replies, so no live reply was read here.
Your host may prefix the tool names.

Contents:
- Step table
- Human replies in a transcript
- What this route cannot do

## Step table

| Step | Tool call |
|---|---|
| Learn the filters | `get_available_filters`. Find `HANDOFF`, `TOPIC`, `INTENT`, `HANDOFFREASON` |
| Size a cluster (step 1) | `get_ada_metric` with `metric_type: conversation_volume_engaged`, both dates, and filters `HANDOFF IS true` with `TOPIC IS <id>` or `INTENT IS <id>`. It returns one number. Use the same dates for every cluster |
| Topic and intent ids | `list_entities` with `entity_type: topics` and `detail: full` |
| List handed-off conversations (step 3) | `get_conversations` with `detail_level: SUMMARY`, both dates and the same filters. Page with `offset` and `next_offset`. Each row has a `conversation_url` |
| Read the replies (step 3) | `get_conversation` on the id. Look for `live_agent_message` entries after the `handoff_triggered` entry |
| Human handle time | `get_ada_metric` with `avg_handle_time_agent`, which returns `{pre, post}` seconds. For one conversation, use the first and last `live_agent_message` timestamps |
| Does a playbook exist (step 6) | `list_entities` with `entity_type: playbooks`, then the playbook id for its steps |
| Is the knowledge there | `search_knowledge` with a short title keyword |
| Is there a tool for the task | `list_entities` with `entity_type: tools`, and `entity_type: handoffs` for the destinations |
| Does coaching cover it | `search_coaching` describing the scenario |
| Draft a test case (step 7) | `draft_test_case_from_conversation` with `conversation_id`. Follow `author-playbook/references/test-cases.md` section 8 |
| Links | `https://<instance>.ada.support/insights/conversations/<id>`. Mark each opened or ASSUMED |

## Human replies in a transcript

`get_conversation` returns the unified transcript. A message that the handoff
integration relays from a human agent is a `live_agent_message` entry with
`content` and `agent_name`. The `handoff_triggered` entry carries `reason_code`
and `reasoning.text`. The api source and the product docs say replies appear
when the integration relays them.

- The MCP drops `presence` entries, so it does not show when an agent joined or
  left.
- `get_conversations` `SUMMARY` has no human-message field. Read each sample with
  `get_conversation`.
- A `handoff_triggered` entry with no `live_agent_message` after it means no
  reply came back through Ada. Follow `references/replies-source.md`.
- `get_conversation` returns the customer's and the human's own words, with
  personal data. Use it to read. Never copy from it into a test case.

## What this route cannot do

- No tool lists a helpdesk's tickets. A handoff that returns no replies needs the
  export in `references/replies-source.md`.
- To check that a path holds across people, group by `agent_name` yourself from
  the conversations you read.
