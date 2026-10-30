# refresh-intent-taxonomy on the command line

For anyone with `adacli`. Checked against the adacli 1.1.0 documentation and
command definitions on 30/10/2026. The installed 0.13.0 has no `topics class`
group, so every command below needs **adacli 1.1.0 or later**. Update first if
`adacli <instance> topics class list` answers "unknown command". No command
here was run live.

## Commands

| Step | Command | Version |
|---|---|---|
| Active Topics and their Intents | `adacli <instance> topics class list --json` | 1.1.0 |
| One Topic with its Intents | `adacli <instance> topics class get <topic-id> --json` | 1.1.0 |
| Intents, all or one Topic | `adacli <instance> topics class intents list [topic-id] --json` | 1.1.0 |
| Conversations for one intent | `adacli <instance> conversations search --intent <intent-id> --since 180d --json` (add `--all --limit 500` to walk a whole window, `--test-users` for test traffic only) | 1.1.0 |
| Read a sample | `adacli <instance> conversations transcript <conversation-id>` | 1.1.0 |
| New Topic | `adacli <instance> topics class create --name <name> --description <scope> [--signals <text>] [--excludes <text>]` | 1.1.0 |
| New Intent | `adacli <instance> topics class intents create <topic-id> --name <name> --description <scope> [--included <text>] [--excluded <text>]` | 1.1.0 |
| Move an Intent to another Topic | `adacli <instance> topics class intents move <topic-id> <intent-id> --to <target-topic-id>` | 1.1.0 |

Notes:
- The command definitions do not say whether recommended intents appear in
  `topics class list`. Look for a status field on each intent in the output.
  Without one, treat the list as the active set.
- `--intent` takes classification intent ids. Whether the search accepts the id
  of a recommended intent is not verified. If it returns nothing, use the
  dashboard counts.
- `--limit` needs `--all`. A search with zero matches may print plain text, not
  JSON, so check the exit code before parsing.
- `intents move` waits for the move. Only the 2,000 most recent conversations
  from the last 90 days follow the intent in reports. Older history stays under
  the old Topic. Say so in the snapshot.
- `topics class delete` removes the Topic and every Intent under it. Do not run
  it on a Topic with live volume.
- Use the full host as `<instance>` when the saved login has one, for example
  `<handle>.us2.ada.support`. A bare handle can fail with AUTH_REQUIRED on
  non-default regions.

## What adacli cannot do

`topics report` and `analytics topics` read the older generated topics. On an
agent that uses classification Topics and Intents they return an empty list
and exit 0, which is not a quiet window. Do not use them here.

As of 30/10/2026 adacli has no command to:
- list AI-recommended intents with their volume and trend
- show per-intent volume, resolution rate and CSAT, or the "other" and
  "unclassified" shares
- approve or dismiss a recommendation
- edit an existing Intent in place (`topics class update` edits a Topic, and
  Intents only have `create`, `move` and `delete`)

Two adacli changes are open and unmerged: a classification default for topic
commands, and `conversations classification <id>`. Do not rely on either until
a release lists them.

Do these in the dashboard: **Analytics > Topics & Intents**. Read the
recommended list, volume, trend and the "other" share there. Use its buttons to
approve or dismiss a recommendation and to edit an intent. For per-intent
resolution rate, count with
`conversations search --intent <id> --resolution not-resolved --since 180d`
against the same search without `--resolution`.
