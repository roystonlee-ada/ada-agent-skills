# mine-human-agent-conversations on the command line

For anyone with `adacli`. Commands are `adacli <instance> <group> ...`. The
`conversations` commands below were checked against `--help` on 05/11/2026 and
against read-only runs on real instances on 28/10/2026. The draft command needs
adacli 1.1.7 or later.

Contents:
- Window and search behaviour
- Step table
- Human replies in a transcript
- What this route cannot do

## Window and search behaviour

- Handoff reasons start on 07/10/2026. Use `--start <date> --end <date>` with
  YYYY-MM-DD, never `--since 28d` across that date.
- A search returns one page. The JSON `total` is the full match count, so
  `--size 1` gives a cheap count. `--limit` needs `--all`.
- A search with zero matches prints plain text, not JSON, even with `--json`.
  Retry once before you report a zero.
- `--all` writes progress text to stderr. Drop it with `2>/dev/null` before you
  parse.

## Step table

| Step | Command |
|---|---|
| Size a cluster (step 1) | `conversations search --handoff --topic <topic> --start <date> --end <date> --size 1 --json` and read `total`. Use `--filter INTENT:IS:<id>` for an intent |
| Topics and intents | `topics list --json`. `analytics topics` ranks topics by volume |
| Ids to read (step 3) | `conversations search --handoff --topic <topic> --start <date> --end <date> --all --limit 50 --json` |
| Read the replies | `conversations transcript <id> --json`. Add `--all` for presence and variable lines. `conversations log <id>` shows the messages with the reasoning |
| Handoff target and reason | `conversations details <id> --json`, or `conversations handoffs <id> --json` when the account allows it |
| Many transcripts at once | `conversations export --topic <topic> --start <date> --end <date> --transcripts --json -o <file> --limit 200`. The export has no handoff filter, so join the file to the ids from the search above |
| Does a playbook exist (step 6) | `playbooks list --json`, then `playbooks get <id> --json` |
| Is the knowledge there | `knowledge list`, and `knowledge probe` to see which articles rank for a customer's question |
| Is there a tool for the task | `actions list`, `code-tools list`, `mcp list`. `handoffs list` for the destinations |
| Does coaching cover it | `coaching list --json` |
| Draft a test case (step 7) | `testing cases from-conversation <id> --json`. Follow `author-playbook/references/test-cases.md` section 8 |
| Links | `https://<instance>.ada.support/insights/conversations/<id>`. Mark each opened or ASSUMED |

## Human replies in a transcript

`conversations transcript <id> --json` returns presence events (`agent_arrival`,
`agent_depart`, `live_chat_end`) and agent messages. An agent message has a
`source` of agent and an `agent_info` block with the name.

- Presence lines are not replies. Count a human reply only when an agent
  message is present.
- Ticket, case and email handoffs return nothing to Ada by design (observed on
  Zendesk Ticketing, a Salesforce case, a Gorgias ticket and email). A
  handed-off conversation with no agent message is normal there. Follow
  `references/replies-source.md`.
- Time to close runs from the first to the last agent message timestamp. Presence
  events give the join and leave times.

## What this route cannot do

- No command lists a helpdesk's tickets. Ask for the export in
  `references/replies-source.md`.
- `conversations export` cannot filter to handed-off conversations. Search for
  the ids first.

## If the instance is read-only

Reading works. Saving a drafted test case exits with code 7: stop, name the case
you were about to save, and leave `~/.adacli/config` alone. `setup-adacli` has
the full rule.
