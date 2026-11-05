# Who can use the Ada MCP server, and which tools

Use when the person asks who can connect an AI assistant to the Ada MCP
server, what data it returns, or how to limit it.

## Preconditions

- Owner role to change tool permissions. Owner or Admin to manage API keys.
- The connection URLs: `https://<instance-domain>/api/mcp/oauth` for OAuth and
  `https://<instance-domain>/api/mcp` for an API key.

## Steps

1. Role access over OAuth: Owner and Admin get all tools, including the two
   write tools (`edit_agent_behavior`, `edit_agent_config`). Agent and Read
   Only get read-only tools. A role change applies on the next call.
2. API keys do not follow the role. Their access comes from the key's
   permissions.
3. To limit tools, open Config > PLATFORM > MCP server. Set Global settings to
   All tools or Selected tools, and set individual settings per member and
   per API key. Once individual settings are on, a new API key starts with no
   tools.
4. To see OAuth connections, open Platform > MCP Server. A revoke takes effect
   within 5 minutes. API keys are managed on the API keys page, not here.
5. With Claude Team or Enterprise, an organisation Owner adds the connector
   first.
6. Tell the person what data flows: conversation transcripts, reasoning
   history, inquiry summaries, resolution status, handoff reasons, CSAT,
   knowledge content, coaching and agent configuration. Redaction rules
   apply to reasoning text from `get_conversation`. Advise turning off model
   training in the assistant before connecting.

## Downtime risk

None expected. A permission change applies on the next call, so an assistant
in the middle of a task can lose a tool.

## How to verify

Connect as a user with the role under test and list the tools the assistant
sees.

## Rollback

Set tool permissions back to the recorded values. Re-add a revoked
connection from the assistant.

## Source

- `product-docs/fern/versions/pages/mcp/introduction/authentication.mdx`
- `.../tool-permissions.mdx`, `.../managing-connections.mdx`, `.../data-privacy.mdx`

## OPEN or ASSUMED

- OPEN: the tool permissions page is marked noindex in the docs, so it may
  change. Recheck it. If an Owner cannot see Global settings, the docs say to
  contact the account team.
- OPEN: the docs give no setting for change approval. The tool definitions
  show that `edit_agent_behavior` stages edits on a changeset and asks for a
  confirmed promote, while `edit_agent_config` applies live.
