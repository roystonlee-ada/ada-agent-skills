# diagnose-conversation over the Ada MCP

For anyone connected to their AI agent's Ada MCP server. Checked against the
live tool definitions on 20/10/2026. Your host may prefix the tool names.

| Step in the skill | Tool call |
|---|---|
| Read the transcript and the reasoning log | `get_conversation` on the id. It returns the transcript with playbook events, handoffs, knowledge searches, coaching used, actions and reasoning, plus the summary and CSAT. Transcripts are long, so read it once and quote from it |
| Did it leave the playbook, or was it the wrong one | The playbook events in `get_conversation`, then `list_entities` with `entity_type: playbooks` and the playbook id for its steps and exits |
| A fact that came out wrong | `search_knowledge` with a short title keyword from the customer's question. Check the article's wording and look for a duplicate title |
| Coaching or general instructions | `search_coaching` describing the scenario, for rules that fire on it. `get_ada_configuration` for the custom instructions |
| An action failed | The failed call in the `get_conversation` log. `run_code_tool` re-runs a code tool on the same input (pass `code_tool_id`). Its network calls are real, so never re-run one that charges, cancels or deletes |
| How common is it | `get_available_filters`, then `get_conversations` with `detail_level: SUMMARY` and both dates, paging with `offset` and `next_offset`. `get_ada_metric` for a rate |
| Where a fix belongs | `get_improvement_guide`, once per session |
| Turn it into a test case | `edit_agent_config` with `entity_type: test_case`, `operation: create`. Call it with no `fields` first. Copy the customer's first message word for word, swap each personal detail and credential for a fake of the same shape, and state the outcome the customer wanted in `success_criteria` |
| Run it on the draft and on live | `get_test_run_quota`, then `edit_agent_config` with `entity_type: test_run`, `operation: create`, `test_case_ids`, and `changeset_id` for the draft. Run again without it for live. Poll `get_test_runs` |
| Links to conversations | `https://<instance>.ada.support/insights/conversations/<id>`. `get_conversations` with `SUMMARY` also returns each dashboard URL |

`edit_agent_config` shows a preview. Show it to the person and call again with
`confirmed: true` only after they say yes.

If a tool blocks you, call `send_feedback` with category `stuck` or
`missing_capability`. Leave out customer details.

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
