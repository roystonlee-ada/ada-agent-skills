---
name: setup-ada-mcp
description: >
  Connect an AI assistant to an Ada AI Agent's MCP server and check that the
  connection works. Use it first, before any other Ada Architect skill, and
  whenever the person says "connect to Ada", "set up the Ada MCP", "Ada tools
  are missing", "get_ada_configuration not found", or an Ada tool call fails
  with an authentication error. Covers Claude Code, Claude Desktop, ChatGPT and
  Codex.
---

# Set up the Ada MCP

The other skills in this plugin call Ada MCP tools such as
`get_ada_configuration` and `get_conversation`. Without a working connection
they have nothing to run on. This skill makes one and proves it.

## 1. Check first

If a tool named `get_ada_configuration` is already listed (your host may add a
prefix), skip to step 4.

## 2. Get the address

Ask for the dashboard domain, for example `acme-corp.ada.support`. The MCP
server address is `https://<domain>/api/mcp/oauth`. It signs in with OAuth, so
there is no API key to paste.

One connection reaches one Ada instance. Name each connection after its
instance, such as `ada-acme-corp`, and keep one customer's instance per
session so their data never mixes with another's.

## 3. Connect

Pick the person's assistant. Say what you will run or click, and wait for a yes.

| Assistant | How |
|---|---|
| Claude Code | `claude mcp add ada-<instance> -- npx mcp-remote https://<domain>/api/mcp/oauth`. Needs Node. Then run `/mcp`, choose the server and finish the sign-in in the browser. Restart the session so the tools load |
| Claude Desktop or Cowork | Use Ada's `install-ada-mcp` skill if it is installed. Otherwise add a server with command `npx` and arguments `mcp-remote` and the address above to the Claude Desktop config, then restart the app |
| ChatGPT | Settings, Connectors, Advanced, turn on Developer mode, then Create. Paste the address, choose OAuth, finish sign-in, and switch the connector on in the chat's tools menu. ChatGPT reaches only public HTTPS addresses. Business and Enterprise workspaces may need an admin to allow custom connectors, and the menu has moved between releases, so follow what the screen shows |
| Codex | Add the address as an MCP server through Codex's MCP settings, then sign in when asked |

ASSUMED: the ChatGPT and Codex rows follow those products' published steps and
have not been run against an Ada instance. If the sign-in fails, say so
plainly and fall back to Claude Code or Claude Desktop.

## 4. Prove it

1. Call `get_ada_configuration`. A reply with the agent name means the
   connection and the sign-in work.
2. Call `get_test_run_quota`. It says how many test runs remain today, which
   the author and revise skills spend.
3. Tell the person in two or three lines: the instance, the agent name, and
   the runs left today.

If either call fails, read the error. An authentication error means the
sign-in did not finish, so repeat step 3. Never ask for a password or a key in
chat.

## 5. Hand over

Name the skill that fits what they came for: `design-conversation` for a new
use case, `author-playbook` to build an approved design, `revise-playbook` to
change one, `diagnose-conversation` for a bad conversation, `review-handoffs`
for why conversations hand off.
