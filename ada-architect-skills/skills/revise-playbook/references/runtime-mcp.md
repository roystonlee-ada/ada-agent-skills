# revise-playbook over the Ada MCP

For anyone connected to their AI agent's Ada MCP server, with no shell. Where
the MCP has no tool for a step, this file says so and gives the fallback. A
tool marked ASSUMED is named from its title and not yet checked against a
live call. Read its description before you rely on it.

| Step in the skill | Tool call |
|---|---|
| Read the live playbook (do this first) | `get_ada_configuration`, then read the target playbook and every playbook it runs or that routes into it (ASSUMED: it returns full playbook steps; if it returns only names, ask the person for the playbook text or use the CLI's `ada-playbook`) |
| Load saved cases (do this second) | `get_test_cases`. Keep every case that touches the use case |
| The use case's record | No memory and no tool. Cases named "<Use case>: <scenario>" in `get_test_cases` are the nearest record. Otherwise ask the person |
| Baseline for a handoff cut | The counts in review-handoffs' MCP file (`get_conversations` with `HANDOFFREASON IS <code>`), saved in your message with the window |
| Send the board again | Put the ADA-DESIGN block in a fenced code block with the same `work` and a new `round`, then write each changed scenario as a readable transcript. Nothing draws it |
| Wait for Approve | The person writes "approved", "approve" or "build it" in chat |
| Check old cases against the board | Compare each case from `get_test_cases` (opening line and `good`) with the approved board. A case the board no longer matches goes to the person with the change you would make, not into the run |
| Stage the rebuilt flow | `edit_agent_behavior` (ASSUMED: it stages into a draft changeset and does not go live). Find the id with `list_agent_changesets`. Call it only after Approve, unless the change is the one-step wording fix |
| Run the whole set on draft and live | `get_test_run_quota` first. OPEN: no listed tool starts a run. If you cannot, use the CLI's `ada-test`, or ask the person to start it on the draft and on live. Read the results with `get_test_runs` and `get_conversation` |
| Show the effect | `compare_changeset_metrics` once the promoted change has traffic |
| The updated use-case record | Put the key, playbook names and case ids in your final message |

If you could not run the cases, say that first in the report. Never promote.
