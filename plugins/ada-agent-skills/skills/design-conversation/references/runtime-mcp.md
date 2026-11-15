# design-conversation over the Ada MCP

For anyone connected to their AI agent's Ada MCP server. Checked against the
live tool definitions on 20/10/2026. Your host may prefix the tool names.

| Step in the skill | Tool call |
|---|---|
| Read what the agent has today | `get_ada_configuration` for the agent, its playbooks (summary only), tools and custom instructions. `list_entities` with `entity_type: playbooks` and an `entity_id` for one playbook's steps, `tools` for code and api tools, `handoffs`, `variables`, `channels`. `search_knowledge` matches article titles only. `search_coaching` is semantic, so describe the scenario |
| Entry, exit and variables | Read the channel and relevant variable entities, then the target and linked playbooks. Read a matching fresh conversation with `get_conversation` to see the actual greeting, locale and ending. For settings the tools or transcript do not show, check the dashboard's channel settings and assigned playbooks. Mark anything still unverified OPEN |
| Policy and knowledge | Use `search_knowledge` for known or likely titles and follow the article references in playbook steps and conversation events. Read the full article and linked policy for the intended market and dates. If the tool returns only an excerpt, use the article URL or dashboard to read the rest |
| How often the topic comes up | `list_entities` with `entity_type: topics` for topic ids, then `get_ada_metric` with `metric_type: conversation_volume_opened` and a `TOPIC` or `INTENT` filter, one call per topic, to rank them. Call `get_available_filters` first. Test conversations are excluded by default |
| How it goes today | `get_conversations` with `detail_level: SUMMARY` and both dates to find three to five ids, then `get_conversation` on each. It returns the transcript with playbook events, knowledge searches, coaching and reasoning |
| A use case already designed | `get_test_cases` with `name_filter` set to the use case. Cases named "<Use case>: <scenario>" are the record. If none, ask whether it was designed before |
| The choices block | The host's question tool when it has one, otherwise numbered options in chat. At most two questions |
| Show the board | Put the ADA-DESIGN block in a fenced code block, then write each scenario as a readable transcript, with translations below the original, system events clearly labeled, and named alternate paths through their endings. Follow [board format](board-format.md) and apply the checklist in section 2 |
| Approve | The person writes "approved", "approve" or "build it" in chat. Treat that as approval for this `work`. Anything else is a comment: send the next round |

Until the person approves, call no write tool: `edit_agent_behavior` or
`edit_agent_config`. Nothing in the MCP holds a build for you. `edit_agent_behavior`
stages onto a changeset that is not live, but `edit_agent_config` edits
(test cases, topics, glossary and others) go live at once.

If you propose a photo path, ask the person which channels accept images. No
tool reports that setting.

Paging: `get_conversations` pages with `offset` and `next_offset`. The list
tools page with `cursor` and `next_cursor`. Read every page before you quote a
count.
