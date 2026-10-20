# ada-playbook-monitor-loop on the command line

For anyone with `adacli` logged in to the instance, and for Ada Architect. The
instance comes first in every command, and there is no `--instance` flag.

| Step | Command |
|---|---|
| Read a playbook | `adacli <instance> playbooks get <id> --json`, and `playbooks list --json` to find the ones that route into it |
| KB articles, actions, code tools it uses | `adacli <instance> knowledge list`, `actions list --json`, `code-tools list --json` |
| Recent real chats | `adacli <instance> conversations search --since 7d` with the playbook filter. It needs `--since`, caps a page at 50 and reports no total, so quote counts as lower bounds. Leave out test chats |
| Transcript (for judging) | `adacli <instance> conversations transcript <id> --json` |
| Reasoning log (for ownership) | `adacli <instance> conversations reasoning <id> --json` |
| Why a chat went the way it did | `adacli <instance> conversations diagnose <id>` names the failing surface |
| Custom metrics on the instance | `adacli <instance> custom-metrics list --json`. A 403 or an empty list means judge from the transcript |
| Ada's verdicts on live chats | `adacli <instance> custom-metrics conversations` |
| Create and run test cases | `adacli <instance> testing cases create --from-json <file>`, then `testing runs create --cases <ids>`, and `testing runs get <id> --json` for `did_pass` and `criteria_results` |
| A case from a failing chat | `adacli <instance> testing cases from-conversation <conversation id>` |
| Compare two runs | `adacli <instance> testing runs compare` |
| Stage a fix | `adacli <instance> changesets stage --file change.json`, then `changesets get <id> --diff` |

Run each case with `testing runs create`. Use `adacli <instance> chat talk`
only for a case a test run cannot express, such as a session that needs a real
one-time code.

## Inside Ada Architect

Architect's helpers make the same reads shorter: `ada-playbook` for a playbook
outline, `ada-convos` for chat lists, `ada-why <instance> <id>` for one chat
turn by turn, `ada-test` for the live-vs-draft table. They are optional.
