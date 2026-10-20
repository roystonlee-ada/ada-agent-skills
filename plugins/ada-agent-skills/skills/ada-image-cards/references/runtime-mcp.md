# ada-image-cards over the Ada MCP

For anyone connected to their AI agent's Ada MCP server. Your host may prefix
the tool names. This route has not been checked end to end for this skill.

| Step | Over MCP |
|---|---|
| Design the card, build the atlas and `tool.py`, test locally | Works. These run on your machine and need no Ada tools |
| Allow the upload host | Dashboard step: Content, Tools, Allowed domains |
| Create or update the code tool | Not confirmed over MCP. Use adacli, or the dashboard |
| Run the tool with dummy data | `run_code_tool`, if your MCP exposes it |
| Wire the playbook and the send attachment | Dashboard or adacli. Changesets reject send attachments |
| Read a test chat | `get_conversation` |

Say which steps you could not do and give the person the adacli or dashboard
step instead.
