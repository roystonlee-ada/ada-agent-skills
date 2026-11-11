# prevent-handoffs on the command line

For anyone with `adacli`. Commands are `adacli <instance> <group> ...`. The
read commands in steps 1 to 4 were run read-only on a real instance on
11/11/2026, over a 14-day window of about 4,700 handoffs. The write commands
are the ones `test-and-fix` names, and its runtime file holds their traps.

## Steps 1 to 4: read only

| Step | Command |
|---|---|
| Is the instance writable (step 0) | `status --json`, and read `read_only` |
| Population N | `conversations search --start <date> --end <date> --size 1 --json`, read `total`. Test users are left out unless you pass `--test-users` |
| Handed off H | the same with `--handoff` |
| Counts by reason (step 2) | `conversations handoff-reasons --start <date> --end <date> --samples 5 --with-reasoning --json`. The JSON has `totals` (`conversations`, `escalated`, `with_reason`) and `reasons`, each with `reason_code`, `conversations`, `share`, `samples` and `reasoning_samples` |
| Every handed-off conversation (step 2) | `conversations search --handoff --start <date> --end <date> --all --limit 10000 --size 500 --json 2>/dev/null > handoffs.json`. Each row has `id`, `platform`, `primary_intent_name`, `intents`, `first_user_message`, `summary`, `automated_resolution_status`, `csat` and `test_user`. About 4,700 rows took 18 seconds |
| The reason code per conversation | One search per code: `conversations search --handoff --handoff-reason <code> --start <date> --end <date> --all --limit 5000 --json`. Join the ids to the file above. A conversation in no list has no code, or the code that holds the rest (check the counts add up) |
| Handoffs that ran through one playbook | `conversations handoff-reasons --playbook <id> --start <date> --end <date> --count --json`, and read `totals`. On adacli 1.0.0, `conversations search --filter PLAYBOOK:IS:<id>` is refused with a 400 |
| Changes since the window started (step 5) | `changesets list --json`: read `status`, the date, `name` and `summary` |
| Read one transcript with the human replies (step 3) | `conversations log <id>` shows customer, agent, knowledge searches, the handoff and then the human agent's messages. `conversations transcript <id> --json` for messages only |
| Many transcripts | `conversations export --start <date> --end <date> --transcripts --json -o <file>`. It has no handoff filter, so join it to the ids |
| The agent's tools, playbooks and handoffs (verdicts.md "Before you start") | `actions list`, `code-tools list`, `mcp list`, `playbooks list --json`, `handoffs list` |
| Is the knowledge there (step 5) | `knowledge list`, and `knowledge get <id>` for an article |
| Why one conversation handed off (step 5) | Follow `diagnose-conversation` on the command line. `conversations diagnose <id> --json` gives a first guess at the surface |

## Steps 5 to 7: writes

| Step | Command |
|---|---|
| Stage a fix | `changesets stage --name "<cause> fix" --summary "<one line>" --file <changes.json>`, as in `test-and-fix`. One changeset per fix |
| Draft a case from a handed-off conversation (step 6) | `testing cases from-conversation <id> --json`. Saves nothing. Needs adacli 1.1.7 or later, and allows 6 drafts a minute. A 429 (exit code 6) can come early when other jobs share the instance: wait a minute and retry, with 12 seconds between drafts. Follow its `instructions` |
| Save the cases | `testing cases create --from-json <file>`, after the person agrees the criteria |
| Replay | `testing quota --json`, then `testing runs create --cases <ids...> --json` for live and the same with `--changeset <id>`. Read with `testing runs list --changesets <id> --json` and `testing runs compare --baseline <ids...> --candidate <ids...> --json` |
| Did the replay hand off | `testing runs get <run id> --json`, and look for the handoff step in the simulated conversation. A run that ends in a handoff is not contained, whatever its criteria say |
| Discard a fix | `changesets remove <changeset id> <baseline id> --entity-type <type>`, or delete a changeset that held only that fix, after asking |
| Promote | Not here. `ada-promote-changeset` |

## Traps

- `handoff-reasons` counts a conversation under every reason it recorded, so
  the shares can add to more than 100%. Count verdicts by conversation id.
- When one code holds nearly every handoff (a handoff-by-design playbook
  records `handoff_configured`), the code cannot rank causes. Say so and rank
  by verdict.
- `--all` writes progress text to stderr. Drop it before you parse.
- A search with zero matches prints plain text, not JSON. Retry once before you
  report a zero.
- `chat talk` and other live chats are real conversations and count in the
  metrics. Never use them to replay a handoff. Use test runs.
- A summary can say a handoff happened when the log shows the human never
  replied. The log decides.

## If the instance is read-only

Steps 1 to 4 work. Any write exits with code 7: stop, write the fixes as
drafts, and report "not replayed". Leave `~/.adacli/config` alone.
`setup-adacli` has the full rule.

## Inside Ada Architect

`ada-export <instance> --start <date> --end <date> --exclude-test-users
--handoff-reasons` counts by reason, `ada-why <instance> <id>` reads one
conversation's reasoning, and `ada-test` runs cases on live and a changeset.
They are shortcuts for the commands above. Architect holds a promote behind
its own gate, and this skill never promotes either way.
