# Ada Architect Skills

A Claude Code plugin that brings Ada Architect's method for working on an Ada
AI Agent to your own Claude. It works over the Ada command line (adacli) or
the Ada MCP server.

## Install

```bash
claude plugin marketplace add roystonlee-ada/ada-architect-skills
claude plugin install ada-architect-skills@ada-architect
```

Then ask Claude to "set up adacli". That skill checks for adacli, installs or
upgrades it with Homebrew, and logs you in.

## What you get

| Skill | Use it to |
|---|---|
| `setup-adacli` | Check adacli, install or upgrade it with Homebrew, log in |
| `design-conversation` | Design a new use case as sample conversations you approve before anything is built |
| `author-playbook` | Build the approved design into a playbook, save its scenarios as tests, run them |
| `revise-playbook` | Change an existing use case, with today's flow shown beside the proposed one |
| `diagnose-conversation` | Find which part of the agent owns a bad conversation, with evidence |
| `review-handoffs` | Count handoffs by the reason Ada recorded, with samples |

Each of the five method skills has two runtime files. `references/runtime-cli.md`
maps its steps to adacli commands. `references/runtime-mcp.md` maps them to Ada
MCP tools, and says where the MCP has no tool.

## Before you start

- Homebrew installs adacli on macOS and Linux. Without a shell, use the Ada MCP.
- Homebrew ships the adacli binary only. These skills come from this plugin.
- No shell? The sibling plugin `ada-architect-skills-mcp` runs the same skills
  over the Ada MCP alone, in Claude, ChatGPT and Codex.

## Update

```bash
claude plugin marketplace update ada-architect
claude plugin update ada-architect-skills@ada-architect
```

## Maintainers

Built from Ada's internal Architect skills by `local/build_plugin.py`. The
build fails if a customer name, an id or an email is left in a skill.
