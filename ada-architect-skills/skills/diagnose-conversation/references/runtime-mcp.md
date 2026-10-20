# diagnose-conversation over the Ada MCP

For anyone connected to their AI agent's Ada MCP server, with no shell. Where
the MCP has no tool for a step, this file says so and gives the fallback. A
tool marked ASSUMED is named from its title and not yet checked against a
live call. Read its description before you rely on it.

| Step in the skill | Tool call |
|---|---|
| Read the transcript and the reasoning log | `get_conversation` on the id. ASSUMED: it carries the log events (playbook, steps, handoff with `reason_code` and `reasoning.text`). If knowledge and coaching used are missing, say that the log is partial, and rely on the checks below |
| Did it leave the playbook, or was it the wrong one | The log events from `get_conversation`, then `get_ada_configuration` for the playbook's trigger and exits |
| A fact that came out wrong | `search_knowledge` with the customer's question. Check what comes back, the article's wording and any duplicate |
| Coaching or general instructions | `search_coaching` for rules that fire on this topic. Read `get_ada_configuration` for general instructions |
| An action failed | The failed call in the log from `get_conversation`. `run_code_tool` re-runs a code tool on the same input |
| How common is it | `get_conversations` with a filter, paging through every `next_cursor`. `get_ada_metric` for the rate |
| Where a fix belongs | `get_improvement_guide` |
| Turn it into a test case | No MCP tool creates one. Fallback: with the CLI, `adacli <instance> testing cases from-conversation <id>`. Otherwise write the case (first turn, later turns, good, fail) in your message for the person to add |
| Run it on the draft and on live | OPEN: no listed tool starts a run. `get_test_run_quota` and `get_test_runs` read quota and results. Start the run with the CLI, or ask the person, then read it back |
| Links to conversations | `https://<instance>.ada.support/conversations/<id>` |

## The diagnosis

Write it in chat as a plain list, with no special block:
- symptom: what the customer experiences, in their words
- mechanism: the actual step, rule or gap, not a restatement
- surface: playbook, knowledge, coaching, general instructions, action,
  trigger, persona or glossary, and one sentence on why it owns the fix
- ruled out: at least two other surfaces, each with the evidence
- evidence: at least one real conversation id and what in it shows the
  mechanism
- confidence: high, medium or low

Nothing checks this before a change here, so a fix without it is on you.
Stage no fix before it is written.
