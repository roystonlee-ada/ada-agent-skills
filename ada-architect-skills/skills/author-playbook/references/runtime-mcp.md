# author-playbook over the Ada MCP

For anyone connected to their AI agent's Ada MCP server, with no shell. Where
the MCP has no tool for a step, this file says so and gives the fallback. A
tool marked ASSUMED is named from its title and not yet checked against a
live call. Read its description before you rely on it.

| Step in the skill | Tool call |
|---|---|
| The approved design | The person approved the board in chat. Build from the last round you showed. Keep the board text in the conversation, because nothing saves it |
| List saved cases | `get_test_cases`. Reuse a case whose name or opening line matches the scenario |
| Save a case | No MCP tool creates a test case. Fallback: with the CLI, `adacli <instance> testing cases create`. Without it, give the person the cases as a table (name, first turn, later turns, good, fail) to add in the dashboard, and say you are waiting on that. OPEN: whether `edit_agent_config` can write test cases. Read its description |
| Record the use case | No memory and no tool. Put the use case key, playbook names and case ids in your final message so the person can paste them into the next session |
| Platform detail | The workspace or plugin copy of the ada-agent-toolkit skill. Otherwise `get_improvement_guide` for guidance on where a fix belongs |
| List code tools, and the existing playbooks and actions | `get_ada_configuration` (ASSUMED: it returns all of them) |
| Test a code tool | `run_code_tool` with sample input. Do this before a playbook calls it |
| Stage the draft | `edit_agent_behavior` for playbook steps, `edit_agent_config` for configuration (ASSUMED: both stage into a draft changeset and do not go live). Then `list_agent_changesets` to get the changeset id. Say the design's `work` key next to that id |
| Check routing | No MCP tool tests routing alone. Fallback: with the CLI, `ada-route`. Otherwise run each case and read which playbook ran in `get_conversation` |
| Run the cases | `get_test_run_quota` first, to see there is room. OPEN: no listed tool starts a run. `get_test_runs` reads runs. If you cannot start one, ask the person to start the run on the draft and on live, then read the results with `get_test_runs` and `get_conversation` |
| Report | A table: case, live, draft, a one-line note, links to both conversations. Add `compare_changeset_metrics` once the draft has traffic, which a new draft will not |

Never promote. The MCP tools listed here do not promote, and the person does
it. Say plainly in the report which steps you could not run on this runtime.
