# ada-image-cards on the command line

For a shell with `adacli` (0.8.0 or later). The numbered steps in `SKILL.md`
already give the commands. This file adds the checks around them.

| Step in the skill | Command |
|---|---|
| Check access | `adacli <handle> code-tools list --json`. A 403 means the role or the `code-actions-enabled` flag is missing |
| Create variables | `adacli <handle> variables create --name <name> --scope global --type string --json` |
| Create the tool | `adacli <handle> code-tools create --file tool.py --no-standalone ... --json` (step 8) |
| Change the source | `adacli <handle> code-tools update <id> --file tool.py`. Inputs and outputs cannot change |
| Dry run | `adacli <handle> code-tools test <id> --inputs '<json>' --json`. It really uploads, so use dummy data |
| Wire the playbook | `adacli <handle> playbooks update` (step 10). A changeset cannot carry the attachment |
| Read a test chat | `adacli <handle> conversations transcript <id> --json`, then `conversations log <id> --json` |

## What this route cannot do

- Add the allowed domain. Do it in the dashboard under Content, Tools, Allowed
  domains, or through the allowed-domains API in the gotchas.
- Show the picture. `chat talk` prints text only, so open the conversation in
  the dashboard to see the card.

## Inside Ada Architect

Use the same commands. Architect's `ada-test` helper can stand in for a test
conversation, as an optional shortcut beside the plain command.
