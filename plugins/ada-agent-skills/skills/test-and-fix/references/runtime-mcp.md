# test-and-fix over the Ada MCP

For anyone connected to their AI agent's Ada MCP server. Checked against the
live tool definitions on 28/10/2026, and by reading a sandbox instance. Your
host may prefix the tool names.

| Step in the skill | Tool call |
|---|---|
| Find saved cases (anchor 1) | `get_test_cases` with `name_filter` set to the use case name. Cases named "<Use case>: <scenario>" are the record. Page with `cursor` and `next_cursor` until it is `null` before you count |
| Read one case in full | `get_test_cases` with `test_case_id`. A case that carries `truncated_fields` was cut to fit a page: read it by id and never write it back from the list |
| Find the design board (anchor 2) | Nothing in the MCP saves a board. Look for the last ADA-DESIGN block in this conversation. If it is not here, ask the person to paste it and to say which round they approved |
| Save a case from a board scenario | `edit_agent_config`, `entity_type: test_case`, `operation: create`. Call it with no `fields` first to read the schema. Required: `name` (256 characters at most), `user_message` (1024 at most), `success_criteria` (list, 1 to 10, 2048 characters each), `language`, `scenario_goal` (2048 at most). A create without `scenario_goal` is rejected after you confirm. Optional: `channel_id`, `variables`, `external_systems` (8000 at most). Leave `changeset_id` off |
| Capture one bad conversation | `get_conversation` on the id for the first customer message and what the customer gave later. Then create the case as above: `user_message` word for word with fakes for personal details, `success_criteria` in the person's words, the later facts in `scenario_goal`, `channel_id` from `list_entities` with `entity_type: channels` |
| Check each tool's setting | `list_entities` with `entity_type: tools` and `detail: full`. Only `full` shows `simulation_mode` on each api, code and mcp tool, and the result is large. Do not pass `limit`: only `entity_type: variables` accepts it, and the call is rejected otherwise. On the sandbox read every tool showed `live` |
| Check each handoff | `list_entities` with `entity_type: handoffs` gives name, description and `is_active`, not the platform. Ask the person where each one sends |
| Check the quota | `get_test_run_quota`: `runs_used`, `runs_remaining`, `daily_limit` |
| Run the baseline on live | `edit_agent_config`, `entity_type: test_run`, `operation: create`, `fields: {test_case_ids: [...]}`. No `changeset_id` means live |
| Run on the changeset | The same call with `changeset_id` inside `fields`. One run targets one changeset |
| Read live results | `get_test_runs` with `changeset_ids: ["baseline"]`, optionally `test_case_ids`. It returns the latest run per case. Page until `next_cursor` is `null` |
| Read changeset results | `get_test_runs` with `changeset_ids: ["<id>"]`. Add `include_history: true` to keep earlier rounds |
| Wait for a run | Poll `get_test_runs` with `test_case_ids` and the same `changeset_ids` every 30 to 60 seconds, about 20 polls at most. A run is done when its status is terminal: `completed`, `failed`, `timeout` or `cancelled`. `pending`, `simulating` and `evaluating` mean wait. `did_pass` is the verdict. One run took about 2 minutes. If the cap passes, tell the person and stop polling |
| Read why a case failed | `get_test_runs` with `test_run_id`. It returns each criterion's outcome and rationale, the `conversation` lines the judge read, and the simulated tool calls. Set `include_transcript: false` to shorten it |
| Diagnose a failure | Hand the failing run's conversation to diagnose-conversation. Its MCP file covers `get_conversation` on the run's conversation |
| Stage a fix | `edit_agent_behavior` with `operation: update`. First fix: pass `name` and `summary`. Later fixes: pass the same `changeset_id`. Entity types for direct edits: `knowledge_article`, `coaching`, `custom_instruction`. Call `operation: describe_entity` first for the fields. Relay every `notes` item. A playbook fix goes through revise-playbook |
| Stage coaching for a failing run | `get_conversation` on the failing run's conversation. Find the bot reply you want to correct, check it shows `is_coachable: true`, and take its `generative_actions_event_id`. Call `search_coaching` with the intent first and update a match rather than add a duplicate. Then `edit_agent_behavior` with `operation: update`, `entity_type: coaching`, `change_type: created`, and `fields`: `conversation_id`, `generative_actions_event_id`, `coaching_type`, `intent` (500 characters at most) and, for `reply` only, `text` (500 at most). Types that point at a target (`action`, `process`, `playbook`, `handoff`, `search_knowledge`) also need `chosen_id`. Pass the loop's `changeset_id`. Run `search_coaching` again: staged coaching must not appear there. If it does, it is live, so tell the person at once |
| Show the diff | `list_agent_changesets` with `changeset_id` and `include_diff: true` |
| Withdraw one fix | `edit_agent_behavior`, `operation: remove`, `changeset_id`, `entity_id`, `entity_type` |
| Reword a wrong case | `edit_agent_config`, `entity_type: test_case`, `operation: update`, `entity_id`, with the new `fields`. Only after the person agrees |
| Hand over | ada-promote-changeset. Do not call `promote` here |

## What goes live at once

`edit_agent_config` applies immediately for test cases, glossary terms,
variables, topics, intents and the other settings it covers. A test case or a
test run touches no customer. A glossary term, a variable, a topic or an
intent does, and a run cannot test it on a changeset first. Say so, and get the
person's yes before you call it. Only `edit_agent_behavior` stages.

## Tool settings

`list_entities` shows each tool's `simulation_mode`. Call `edit_agent_behavior`
with `describe_entity` for `api_tool`, `code_tool` or `mcp_tool` to see whether
a simulation setting is a field you can stage. If it is not listed, the person
sets "Mock in simulations" or "Block in simulations" on the Tools page of the
dashboard. Say which tools and which setting.

## Writes need the person

`edit_agent_config` shows a preview. Show it and call again with
`confirmed: true` only after the person says yes. That covers a case save, a
case reword and each test run. Say how many runs a call will use and what the
quota leaves. A `promote` is not part of this skill.

If a tool blocks you, call `send_feedback` with category `stuck` or
`missing_capability`. Leave out customer details.

## Conversation links

A link needs the instance handle, which is the subdomain of the dashboard URL
the person uses. Ask once and reuse it. A `get_conversations` call with
`detail_level: SUMMARY` also returns a dashboard URL for each row, so take the
handle from there when you have one. Write each link as
`https://<handle>.ada.support/insights/conversations/<id>`.
