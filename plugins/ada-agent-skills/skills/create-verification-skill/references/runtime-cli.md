# create-verification-skill on the command line

For Claude Code, Codex or any shell with `adacli`, and for Ada Architect.
Command shapes checked against adacli `main` on 21/10/2026. Replace
`<instance>` with the agent's handle.

| Step in the skill | Command |
|---|---|
| Doctor: session | `adacli <instance> status` |
| Doctor: test quota | `adacli <instance> testing quota` |
| Doctor: the draft | `adacli <instance> changesets get <changeset-id>` shows what is staged. `changesets list` finds the id |
| Find the draft | `adacli <instance> changesets list`, then `changesets get <id>` for each one in status `testing`. Read the staged diff and match it to the case |
| List saved cases | `adacli <instance> testing cases list --json`. The table view is very wide. The JSON is `{"test_cases": [...]}` |
| Save a case | `adacli <instance> testing cases create --from-json <file>`. Read `author-playbook/references/test-cases.md` before you word `good` and `fail` |
| Save a case from a real chat | `adacli <instance> testing cases from-conversation <conversation-id>` prints a scaffold for review. Add `--create` to save it, and `--criteria` to replace the seeded criteria |
| Run on live | `adacli <instance> testing runs create --cases <id> <id> ...` |
| Run on the draft | The same command with `--changeset <changeset-id>` |
| Repeat for a pass rate | Add `--repeat <n>` |
| Read a run | `adacli <instance> testing runs get <run-id> --json`. Always use `--json`. The table view labels every transcript line "User:", prints `undefined` for some turns and shows no verdict per criterion. In the JSON, read `status`, `did_pass`, `conversation_id`, `criteria_results[].did_pass` and `criteria_results[].rationale`. `testing runs list --status <status>` finds runs |
| Wait for a run | A run is `simulating`, then `completed` (about 30 seconds). Poll `runs get` until it is `completed`, `failed` or `timeout` |
| What a run touched | `simulated_calls` in the run JSON lists each action call. An entry with `kind: live_web_action_call` sent a real request, so the test was not a dry run |
| Live against draft | `adacli <instance> testing runs compare --baseline <live-run-ids> --candidate <draft-run-ids>` lists newly passing and regressed cases |
| Open a conversation | `adacli <instance> conversations get <id>`, or `conversations diagnose <id>` for the failure surface. Treat the surface as a lead: on a test conversation it can name knowledge for a case that guidance owns |
| Test a code tool | `adacli <instance> code-tools test <tool-id> --inputs '<json>'`. It makes real network calls and uses real secrets, so never run one that charges, cancels or deletes. `code-tools list --json` finds the id |
| Backtest on traffic | `adacli <instance> changesets compare <changeset-id> --start <YYYY-MM-DD> --end <YYYY-MM-DD>`. It reads conversations that ran on the changeset, so a new draft has none. Test conversations also count in the baseline volume |
| Recompute a number | `adacli <instance> analytics summary` with the same filter and window as the claim |

## Exit codes

- Exit code `22` means a degraded or unverifiable read. Retry, and treat the
  output as incomplete.
- A zero from `analytics summary` is not proof of a quiet window. A failed read
  can return the same zeroed payload. Check the window against a second read.

## Inside Ada Architect

The helper `ada-test <instance> --cases <ids> --changeset <id>` runs the same
test as `testing runs create`. Use either. Architect has no timer, so a
verification pass runs when someone asks for it.

Verification never promotes or rolls out a change. The person does that.
