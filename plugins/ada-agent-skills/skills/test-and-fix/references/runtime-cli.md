# test-and-fix on the command line

For anyone with `adacli`, in Claude Code or any shell. Commands were checked
against `adacli <instance> <group> <command> --help` on 28/10/2026. Replace
`<instance>` with the handle you log in with.

| Step in the skill | Command |
|---|---|
| Find saved cases (anchor 1) | `adacli <instance> testing cases list --json --page 1 --limit 100`, then `--page 2` and on until a page comes back empty. Keep cases named "<Use case>: <scenario>" |
| Read one case in full | `adacli <instance> testing cases get <id> --json` |
| Find the design board (anchor 2) | `ls ~/.ada-architect/<instance>/boards/` for `<work>-r<round>.design.txt`, and read the highest round. `cat ~/.ada-architect/<instance>/use-cases/*.md` for the record that lists case ids. Ask the person which round they approved |
| Save a case from a board scenario | Write a JSON array to a file with the Write tool, then `adacli <instance> testing cases create --from-json <file>`. Fields per case: `name`, `user_message`, `success_criteria` (list), `scenario`, `language`, `channel_id`, `variables`, `external_systems`. `--from-json` cannot be mixed with `--name` or `--criteria` |
| Capture one bad conversation | `adacli <instance> testing cases from-conversation <conversation id> --name "<Use case>: <scenario>" --criteria "<the person's outcome>" --json` prints a scaffold and creates nothing. Review it, then add `--create`. See the traps below |
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

- `from-conversation` seeds the criteria with generic lines ("Resolves the
  customer's inquiry..."). Always pass `--criteria` with the person's own
  outcome, or the case checks nothing they asked for.
- It seeds the opening message from the first customer text message and the
  scenario from the conversation's summary. Check both, and swap personal
  details for fakes.
- Exit code 22 means a degraded read. The scaffold is untrusted and nothing was
  created. Retry once, then ask the person.
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

## Inside Ada Architect

Where the Architect helpers are installed, `ada-test <instance> --cases <ids>
--changeset <id>` runs cases on live and on the changeset and prints a table,
and `ada-why <instance> <conversation id>` shows which step decided a
conversation. They are shortcuts for the commands above. Saved use-case
records are in `/mnt/memory/*/use-cases/*.md`. Architect holds a promote
behind its own gate, and this skill never promotes either way.
