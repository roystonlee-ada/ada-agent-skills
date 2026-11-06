# voice-playbook-builder over the Ada MCP

For anyone connected to their AI agent's Ada MCP server. Checked against the
live tool definitions on 06/11/2026. Your host may prefix the tool names.

Every bot's server has the same tool names. Only the prefix names the
instance (for example `mcp__ada-<instance>__`). Before each call, check the
prefix is the builder's instance.

## Steps in the skill

| Step in the skill | Tool call |
|---|---|
| Setup check | No single call. Confirm `get_ada_configuration` answers, then read the live schema and guide below. Client behaviours the check reads from real calls are covered in "Client behaviours" below |
| Live playbook schema | `edit_agent_behavior` with `operation: describe_entity`, `entity_type: playbook`, before every build. It lists every field, the operators by variable type, nesting limits, deviation settings and the action-error rule |
| Platform guide | `get_improvement_guide`, once per session. It covers which entity to use, the changeset lifecycle and the voice ask rules |
| Find what exists | `list_entities` with `entity_type` `variables`, `handoffs`, `playbooks`, `tools`, `channels`. Pass `entity_id` for one playbook's steps or a code tool's source. `get_ada_configuration` for actions |
| Create a variable | `edit_agent_config` with `entity_type: variable`, `operation: create`. It goes live at once, so prefix the name. Show the builder the whole list once and get one approval |
| Stage actions, tools, the playbook | `edit_agent_behavior` with `operation: update`, `changes`, and a `name` and `summary` on first use. Pass `changeset_id` to add to one you staged. Relay every `notes` item in the reply |
| Read what a changeset changes | `list_agent_changesets` with `include_diff: true` |
| Withdraw one edit | `edit_agent_behavior` with `operation: remove`, `changeset_id`, `entity_id` |
| Save a test case | `edit_agent_config` with `entity_type: test_case`, `operation: create`. Call it with no `fields` first to read the schema. Set `channel_id` to the voice channel from `list_entities` (`channels`), or the test runs as chat |
| Run cases on the changeset | `get_test_run_quota` first, and say how many runs you will use. Then `edit_agent_config` with `entity_type: test_run`, `operation: create`, `test_case_ids`, `changeset_id`. Run again without `changeset_id` for live |
| Read a run | `get_test_runs` (`test_run_id`, or `changeset_ids` and `status_filter`). Its `conversation` leaves out playbook steps and tool calls, so open the call with `get_conversation` |
| Read a call in full | `get_conversation` with the id. It returns the full transcript with playbook events, handoffs and reasoning. It is long, so read the part that matters |
| Find real calls through a playbook | `get_available_filters`, then `get_conversations` with `detail_level` `IDS_ONLY` or `SUMMARY`, a date range and filters. Simulations are not in the index, so use `get_test_runs` for those |
| Test a code tool | `run_code_tool` with sample input. Its network calls are real, so never run one that charges, cancels or deletes |
| Quick check without a test case | `simulate_conversation` where your server lists it (it takes a channel id). Otherwise run a test case on the changeset |
| Promote | `edit_agent_behavior` with `operation: promote` and `changeset_id`. The first call returns a Confirm/Cancel preview. Show it, and call again with `confirmed: true` only after the builder says yes. If the preview has a `warnings_token`, send it back with the confirm |
| Roll out by percentage | `operation: set_rollout` with `changeset_id`, `percentage` (1 to 90) and `max_conversations`. End it with `operation: stop_rollout` |
| Roll back | `operation: revert` with `changeset_id` of the promoted changeset and a `name`. It builds a new changeset that undoes it. Promote that |
| Report | A table: case, live, draft, a one-line note, and links to both conversations |

## Replacing the scripts

The scripts in the CLI route read through the adacli session. Over MCP, do the
same by hand:

| CLI script | MCP replacement |
|---|---|
| `monitor.py` on test runs | `get_test_runs`, then `get_conversation` per run. Read the caller turns, what the caller heard, each variable set and the playbook events |
| `monitor.py` on real calls | `get_conversations` (`SUMMARY`) for the playbook's date range, then `get_conversation` on every call that ended in a handoff and a few that did not. Look for a failure phrase, a status outside 2xx, a backtrack, an off-topic exit, an "I don't have it" and digits of six or more read aloud |
| `runsummary.py` | `get_test_runs` for pass or fail and the failed criteria, then `get_conversation` for what was said and the variables set |
| `prereq_check.py` | See "Client behaviours" |
| `action_test.py` | `run_code_tool` for code tools. For an API tool, see "What MCP-only cannot do" |

## Client behaviours

Several client switches change how a playbook acts: whether a failure branch
after an API call runs, whether the three deviation settings act independently,
whether the Send SMS step is on. No tool shows them. Read them from evidence:

- Failure branches: find a real call where an API returned a non-2xx status
  (`get_conversation`) and check whether playbook steps followed, or a handoff
  came first. A bot with no such call yet gives no answer. Say so, and plan on
  the API returning 200 with an error field.
- Deviation settings: `list_entities` with the playbook's `entity_id` shows the
  value stored on each ask. Whether it takes effect is a client switch, so
  prove it with a test case that asks a side question mid-ask.
- Send SMS: run a real call. Sims fake delivery.

## Case rules

- A test case holds the first caller message and a goal. A simulated caller
  plays out the call from `scenario_goal`, so later scripted turns do not
  exist. Put what the caller gives only when asked, and what they do not know,
  in `scenario_goal`.
- Write `success_criteria` as outcomes for the caller. Add each "must not" as
  its own criterion.
- `variables` only sets meta variables, such as `phone_number`. Variables you
  created are not applied.
- Say in `external_systems` how each system behaves. An API in live mode sends
  its real request even in a simulation, so check each tool's
  `simulation_mode` first.
- Use fake values of the same shape for every personal detail and credential.

## What MCP-only cannot do

- It cannot test an API tool with literal values. The tool list has
  `run_code_tool` for code tools and nothing for API tools. Use a test case with
  the API in mock mode, the action test panel in the dashboard, or the CLI route.
- It cannot show a client's switches (see above).
- It cannot read a call's audio. The builder listens to recordings in the
  dashboard.
- Dashboard steps remain: the greeting where it does not use the Conversation
  Start protocol, selecting a code or MCP tool on a run step once, and raising
  caps on tools and playbooks (ask the builder to request it from Ada support).

## Writes need the person

`edit_agent_config` shows a preview. Show it and call again with
`confirmed: true` only after the builder says yes. The run quota is shared.
After staging, offer a test run, a rollout or a promote and let the builder
choose. Do not start one on your own.

Say plainly in the report which steps you could not run on this host.
