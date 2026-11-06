# test-and-fix on the command line

For anyone with `adacli`, in Claude Code or any shell. Commands were checked
against `adacli <instance> <group> <command> --help` on 28/10/2026. Replace
`<instance>` with the handle you log in with.

| Step in the skill | Command |
|---|---|
| Find saved cases (anchor 1) | `adacli <instance> testing cases list --json --page 1 --limit 100`, then `--page 2` and on until a page comes back empty. Keep cases named "<Use case>: <scenario>" |
| Read one case in full | `adacli <instance> testing cases get <id> --json` |
| Read a requirements sheet (anchor 2) | A Google Sheet or doc: use a Google Drive or Sheets tool if your host has one, else ask the person to download the tab as CSV and give you the path, then read it with the Read tool. See `anchor-from-sheet.md` |
| Find the design board (anchor 3) | `ls ~/.ada-architect/<instance>/boards/` for `<work>-r<round>.design.txt`, and read the highest round. `cat ~/.ada-architect/<instance>/use-cases/*.md` for the record that lists case ids. Ask the person which round they approved |
| Save a case from a board scenario | Write a JSON array to a file with the Write tool, then `adacli <instance> testing cases create --from-json <file>`. Fields per case: `name`, `user_message`, `success_criteria` (list), `scenario`, `language`, `channel_id`, `variables`, `external_systems`. `--from-json` cannot be mixed with `--name` or `--criteria` |
| Capture one bad conversation | `adacli <instance> testing cases from-conversation <conversation id> --json` saves nothing. It prints the screened draft and an `instructions` field: follow it. After the person confirms, write the case as a JSON array and save it with `testing cases create --from-json <file>`. Needs adacli 1.1.7 or later. See the traps below |
| Add what the customer gave later | `adacli <instance> testing cases update <id> --scenario "<text>"` |
| Check each tool's setting | `adacli <instance> actions list` shows each api tool's Mode (mock or live). `adacli <instance> actions profile <id>` shows its sampled replies |
| Check each handoff | `adacli <instance> handoffs list`, then `adacli <instance> handoffs get <id> --json`. Ask the person which platform each one sends to |
| Check the quota | `adacli <instance> testing quota --json` |
| Run the baseline on live | `adacli <instance> testing runs create --cases <ids...> --json`. No `--changeset` means live |
| Run on the changeset | `adacli <instance> testing runs create --cases <ids...> --changeset <id> --json`. Runs on a changeset stay out of the metrics |
| Read live results | `adacli <instance> testing runs list --changesets baseline --json`. Page with `--page` |
| Read changeset results | `adacli <instance> testing runs list --changesets <id> --json` |
| Read why a case failed | `adacli <instance> testing runs get <run id> --json` gives the simulated conversation and each criterion's result. Add `--calls` for each simulated tool call and the failure code. Call records last one day |
| Round against baseline | `adacli <instance> testing runs compare --baseline <live run ids...> --candidate <changeset run ids...> --json` returns `newly_passing`, `regressed` and `summary.delta` |
| Diagnose a failure | Hand the failing run's conversation to diagnose-conversation. Its CLI file covers `adacli <instance> conversations log <id>` |
| Stage a fix | Write a JSON array of changes (`entity_type`, `change_type`, `entity_id`, `fields`) with the Write tool. First fix: `adacli <instance> changesets stage --name "<use case> fixes" --summary "<one line>" --file <file>`. Later fixes: `--changeset <id>` in place of `--name`. `adacli docs guide` lists the fields of each entity type under "Staging reference by entity type". A playbook fix goes through revise-playbook |
| Show the diff | `adacli <instance> changesets get <id> --diff` |
| Withdraw one fix | `adacli <instance> changesets remove <changeset id> <baseline id> --entity-type <type>` |
| Reword a wrong case | `adacli <instance> testing cases update <id> --criteria "<one>" "<two>"`. The list replaces the stored criteria. Only after the person agrees |
| Hand over | ada-promote-changeset. Do not run `changesets promote` here |

## Traps

- adacli before 1.1.7 builds the case from the unscreened transcript. Check
  `adacli --version` first and upgrade (`setup-adacli`).
- `--create`, `--name` and `--criteria` are deprecated. `--create` saves a case
  with a fixed scenario and fixed criteria, and prints a warning. Use the
  `--json` flow so the case gets a real scenario and the person's outcome.
- The command fails with no draft when the conversation is not found, 6 drafts
  in a minute were used, or the conversation cannot be screened. Wait a minute
  and retry once, then ask the person.
- Exit code 22 means a degraded read. The draft is untrusted and nothing was
  created. Retry once, then ask the person.
- Run the case, then read the run with `testing runs get <run id> --json --calls`.
  `simulation_not_covered` means the case's external systems text misses a call:
  fix the text, not the agent. A live web action call means an API tool is not
  mocked: hold further runs and name the tool.
- `testing runs create --repeat <n>` runs each case n times. Count each repeat
  against the quota (ASSUMED: the quota counts every run).
- A case that sets `variables` can make a playbook skip the lookup you meant to
  test. Set the variable or describe the lookup in `external_systems`, not both.

## What goes live at once

Fixes stage on a changeset. Glossary, variable and topic commands write to live
config with no changeset (ASSUMED: they do on the CLI, as the same entities do
on the MCP), so a run cannot test them first. Say so and get the person's yes.
`coaching create --live` also goes live at once, so stage coaching on the
changeset instead.

## Tool settings

`adacli <instance> actions update <id> --simulation-mode mock` sets an api
tool to mock in simulations. It is a write to the live action, though it
changes only what simulations do, so get the person's yes first. The CLI shows
no simulation setting for code tools or MCP tools (`code-tools update --help`
and `mcp tools update --help` list none), so the person sets "Block in
simulations" on the Tools page of the dashboard.

## If the instance is read-only

Run `adacli <instance> status --json` once at the start. If `read_only` is
`true`, say so before you plan any change: this skill's writes will be
refused. Offer a writable instance, or the steps that only read. A write that
exits with code 7 means the same. Stop, name the change, and leave
`~/.adacli/config` alone. `setup-adacli` has the full rule.

## Inside Ada Architect

Where the Architect helpers are installed, `ada-test <instance> --cases <ids>
--changeset <id>` runs cases on live and on the changeset and prints a table,
and `ada-why <instance> <conversation id>` shows which step decided a
conversation. They are shortcuts for the commands above. Saved use-case
records are in `/mnt/memory/*/use-cases/*.md`. Architect holds a promote
behind its own gate, and this skill never promotes either way.
