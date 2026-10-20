# ada-image-cards over adacli

For anyone with adacli logged in to their AI agent. Every step in `SKILL.md`
uses these commands, so this route can do all of it.

| Step | Command |
|---|---|
| Create the variables | `adacli <handle> variables create --name <name> --scope global --type string --json` |
| Create the code tool | `adacli <handle> code-tools create --file tool.py ... --no-standalone --json` |
| Change the source | `adacli <handle> code-tools update <id> --file tool.py` |
| Dry-run it | `adacli <handle> code-tools test <id> --inputs '{...}' --json` |
| Wire the playbook | `adacli <handle> playbooks update` (changesets reject the attachment) |
| Read a test chat | `adacli <handle> conversations transcript <id> --json` and `conversations log <id> --json` |

Needs adacli 0.8.0 or later, an ADMIN or OWNER role, and the
`code-actions-enabled` flag on the agent.
