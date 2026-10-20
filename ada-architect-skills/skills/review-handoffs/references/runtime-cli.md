# review-handoffs on the command line

For Ada Architect and anyone with `adacli` and the Architect helpers.

| Step | Command |
|---|---|
| Count by reason | `ada-export <instance> --since 7d --exclude-test-users --handoff-reasons` |
| A longer window | add `--start YYYY-MM-DD --end YYYY-MM-DD` (never before 2026-10-07) |
| More conversations for one reason | `ada-convos <instance> --since 7d --filter HANDOFFREASON:IS:<code> --ids` |
| Every handoff with its reasoning | `ada-export <instance> --since 7d --exclude-test-users --fields _id,is_escalated,handoffs > /tmp/h.json` |
| Read one conversation | `adacli <instance> conversations get <id> --json`, then `ada-why <instance> <id>` |
| Baseline and after | run the count twice over matching windows and keep both outputs |

`--handoff-reasons` prints JSON: `conversations`, `conversations_with_handoff`,
`escalated_conversations`, `null_reason_attempts`, and `by_reason`, ranked by
conversations. Each entry has `attempts`, `failed_attempts`, `conversations`,
`escalated_conversations` and up to two `samples` with `id` and `reasoning`.

Each handoff in the export has `reason_code`, `reasoning`, `outcome_status`,
`name` and `date_created`. Test chats on a changeset get reasons too, so a
before and after on a draft works. `unclassified` is a real code with blank
reasoning: count it, but read the conversation to explain it.

The export stops at 20,000 conversations, newest first, and says on stderr
which dates it covered. Quote those dates.
