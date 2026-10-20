# design-conversation over the Ada MCP

For anyone connected to their AI agent's Ada MCP server, with no shell. Where
the MCP has no tool for a step, this file says so and gives the fallback. A
tool marked ASSUMED is named from its title and not yet checked against a
live call. Read its description before you rely on it.

| Step in the skill | Tool call |
|---|---|
| Read playbooks, actions, code tools, knowledge | `get_ada_configuration` for the structure (ASSUMED: it returns all four kinds; if one is missing, say so and ask the person). `search_knowledge` for what an article says today. `search_coaching` for coaching that touches the topic. `list_entities` for the entities the agent already knows |
| How often the topic comes up | `get_conversations` with a keyword or topic filter over a window, paging through every `next_cursor` before you quote a count. `get_ada_metric` for volume. No MCP tool ranks topics, so if the person has the CLI, `ada-topics` does |
| How it goes today | `get_conversation` on three to five real ids |
| A use case already designed | No memory folder and no tool for it. Call `get_test_cases` and look for cases named "<Use case>: <scenario>". If none, ask the person whether it was designed before |
| The choices block | The host's question tool when it has one, otherwise numbered options in chat. At most two questions |
| Show the board | Nothing draws it. Put the ADA-DESIGN block in a fenced code block, then write each scenario as a readable transcript (customer and agent turns, with `options` in brackets) so the person can read it as a customer. Apply the checklist in section 2 yourself, because no tool does it |
| Approve | The person writes "approved", "approve" or "build it" in chat. Treat that as approval for this `work`. Anything else is a comment: send the next round |

Until the person approves, call no write tool: `edit_agent_behavior`,
`edit_agent_config`, or anything that saves a test case. Nothing in the MCP
holds a build for you. ASSUMED: those two tools stage into a draft changeset
and do not go live. Check with `list_agent_changesets` before you trust that.

OPEN: whether `get_ada_configuration` returns the image-reading settings.
If you propose a photo path, ask the person which channels are on.
