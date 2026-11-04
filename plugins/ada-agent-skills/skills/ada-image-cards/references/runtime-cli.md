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

## If the instance is read-only

Run `adacli <instance> status --json` once at the start. If `read_only` is
`true`, say so before you plan any change: this skill's writes will be
refused. Offer a writable instance, or the steps that only read. A write that
exits with code 7 means the same. Stop, name the change, and leave
`~/.adacli/config` alone. `setup-adacli` has the full rule.

## Inside Ada Architect

Use the same commands. Architect's `ada-test` helper can stand in for a test
conversation, as an optional shortcut beside the plain command.
