# Ada Agent Skills

Skills for designing, building, changing, rolling out and monitoring an Ada AI
Agent. Anyone who can reach their agent through the Ada command line (adacli)
or the Ada MCP server can use them. You do not need Ada Architect.

One repo and one plugin serve both routes. Each skill has a
`references/runtime-cli.md` and a `references/runtime-mcp.md`. Your assistant
reads the one that matches the tools it has, and says plainly what it cannot do
on your route.

## Install

| Assistant | Command or steps |
|---|---|
| Claude Code | `claude plugin marketplace add roystonlee-ada/ada-agent-skills` then `claude plugin install ada-agent-skills@ada-agent-skills` |
| Codex | `codex plugin marketplace add roystonlee-ada/ada-agent-skills` then `codex plugin add ada-agent-skills@ada-agent-skills`. Start a new session afterwards |
| ChatGPT | Upload the plugin folder under Personal plugins, or ask a workspace admin to publish it. See OpenAI's plugin docs |
| Any other assistant that reads Agent Skills | Copy `plugins/ada-agent-skills/skills/` into that assistant's skills folder |

Then ask your assistant to "set up adacli" (command line) or "set up the Ada
MCP" (no shell needed). Each setup skill checks the connection to your
instance.

## Skills

| Skill | Use it to |
|---|---|
| `setup-adacli` | Check adacli, install or upgrade it with Homebrew, log in |
| `setup-ada-mcp` | Connect your assistant to your Ada instance over MCP and check it works |
| `design-conversation` | Design a new use case as sample conversations you approve before anything is built |
| `author-playbook` | Build the approved design into a playbook, save its scenarios as tests, run them |
| `revise-playbook` | Change an existing use case, with today's flow shown beside the proposed one |
| `diagnose-conversation` | Find which part of the agent owns a bad conversation, with evidence |
| `review-handoffs` | Count handoffs by the reason Ada recorded, with samples |
| `ada-image-cards` | Show a per-customer picture card in chat, drawn by a code tool and hosted through Ada's File Upload |
| `promote-changeset` | Check a staged change, show its real diff, and hand you the promote step |
| `rollout-changeset` | Ramp a change onto live traffic in steps or at one percent you choose, and judge it against the baseline |
| `playbook-monitor-loop` | Test a playbook, watch real chats for verified problems, and stage tested fixes |

## What each route can do

| | adacli | Ada MCP |
|---|---|---|
| Read the agent, conversations and metrics | Yes | Yes |
| Stage changes on a changeset | Yes | Yes |
| Save test cases and run them | Yes | Yes, with your confirmation and the daily run quota |
| Start, raise or stop a sampled rollout | Yes | No. The skill tells you the dashboard step |
| Promote a changeset | Yes, after your go-ahead | No. The skill tells you the dashboard step |

Nothing reaches live customers without you. Edits land on a changeset that is
not live, and you approve every test run, rollout step and promote.

## Before you start

- What you can do depends on your Ada user's permissions.
- Homebrew installs adacli on macOS and Linux. It ships the binary only. The
  skills come from this plugin.
- Some `runtime-cli.md` files also name optional helper scripts from Ada's
  Architect tool. Without them, use the plain adacli commands beside them.
- The ChatGPT and Codex steps follow those products' docs. They have not been
  tried against a live Ada instance yet.

## Update

Claude Code: `claude plugin marketplace update ada-agent-skills`, then
`claude plugin update ada-agent-skills@ada-agent-skills`.
Codex: `codex plugin marketplace upgrade ada-agent-skills`.

## Moving from the old names

This repo was `ada-architect-skills`, and a sibling repo,
`ada-architect-skills-mcp`, held the MCP-only copy. This one plugin replaces
both. Remove the old plugin, then add this marketplace:

```bash
claude plugin uninstall ada-architect-skills@ada-architect
claude plugin uninstall ada-architect-skills-mcp@ada-architect-mcp
```

## Maintainers

Built from Ada's internal Architect skills by `local/build_plugin.py`. Every
skill must run over adacli or the Ada MCP without Architect. The build fails if
a customer name, an id or an email is left in a skill.
