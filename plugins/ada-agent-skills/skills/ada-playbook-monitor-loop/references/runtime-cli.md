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
| Create and run test cases | `adacli <instance> testing cases create --from-json <file>`, then `testing runs create --cases <ids>`, and `testing runs get <id> --json` for `did_pass` and `criteria_results` |
| A case from a failing chat | `adacli <instance> testing cases from-conversation <conversation id> --json` prints a screened draft and saves nothing. Follow its `instructions`, and `author-playbook/references/test-cases.md` section 8. Needs adacli 1.1.7 or later |
| Compare two runs | `adacli <instance> testing runs compare` |
| Stage a fix | `adacli <instance> changesets stage --file change.json`, then `changesets get <id> --diff` |

Run each case with `testing runs create`. Use `adacli <instance> chat talk`
only for a case a test run cannot express, such as a session that needs a real
one-time code.

## If the instance is read-only

Run `adacli <instance> status --json` once at the start. If `read_only` is
`true`, say so before you plan any change: this skill's writes will be
refused. Offer a writable instance, or the steps that only read. A write that
exits with code 7 means the same. Stop, name the change, and leave
`~/.adacli/config` alone. `setup-adacli` has the full rule.

## Inside Ada Architect

Architect's helpers make the same reads shorter: `ada-playbook` for a playbook
outline, `ada-convos` for chat lists, `ada-why <instance> <id>` for one chat
turn by turn, `ada-test` for the live-vs-draft table. They are optional.
