# ada-promote-changeset on the command line

For anyone with `adacli` logged in to the instance, and for Ada Architect. The
instance comes first in every command, and there is no `--instance` flag.

| Step | Command |
|---|---|
| Status | `adacli <instance> changesets get <id> --json` |
| Find a changeset | `adacli <instance> changesets list --json` |
| Cases that touch the playbook | `adacli <instance> testing cases list --json`, keep those whose scenario reaches the changed playbook |
| Cases from real chats | `adacli <instance> testing cases from-conversation <conversation id>` |
| Run on draft and on live | `adacli <instance> testing runs create --cases <ids> --changeset <id>`, then again without `--changeset`. Read each with `testing runs get <run id> --json`: `did_pass`, `criteria_results[].rationale` |
| The real diff | `adacli <instance> changesets get <id> --diff` |
| Direct promote | `adacli <instance> changesets promote <id>` returns a preview. Applying it needs `--yes` and the `--token` from that preview, which only the person's go-ahead permits |
| Clean up a test stage | `adacli <instance> changesets delete <id> --yes` |

## Promote needs the person

Run the preview and show it. Apply only after the person says yes in chat, then
use the token from that same preview. If a second call asks for confirmation
again, live config moved between the two calls: stop and show the new diff.

## Inside Ada Architect

Architect has helpers: `ada-test <instance> --cases <ids> --changeset <id>` for
the run table, and `ada-changeset <instance> <id> --emit` for the diff panel.
Promote there only when the gateway sends a message that starts
`PROMOTE-AUTHORISED <token>`, and run exactly the command it gives, once. Relay
a blocked message as written. Without that message, do not promote.
