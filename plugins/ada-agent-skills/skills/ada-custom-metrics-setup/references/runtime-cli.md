# ada-custom-metrics-setup on the command line

For anyone with `adacli` logged in to the instance, and for Ada Architect. The
instance comes first in every command, and there is no `--instance` flag.

| Step | Command |
|---|---|
| Existing metrics and scorecards | `adacli <instance> custom-metrics list --json` and `adacli <instance> scorecards list --json` |
| Use cases and handoffs | `adacli <instance> playbooks list`, and `adacli <instance> topics class list` for defined topics and intents |
| Themes | `adacli <instance> topics report --since 30d --json` |
| A recent sample of chats | `adacli <instance> conversations export --since 30d --limit 500 --transcripts --json -o <file>` |
| Slice by outcome | `adacli <instance> conversations search --since 30d --handoff`, `--csat 1 2`, `--resolution not-resolved`, `--language <code>` |
| One transcript | `adacli <instance> conversations transcript <conversation id> --json` |
| Create a metric | `adacli <instance> custom-metrics create --name <name> --pass-description <text> --fail-description <text> --scoring-guidance <text> --null-description <text>`. Add `--intent-ids <ids>` to scope it, `--direction higher_is_better` or `higher_is_worse`, and `--subject ai_agent` |
| Create the scorecard | `adacli <instance> scorecards create --name <name> --description <text> --metrics '[{"metric_id":"<id>","weight":<n>}]'`. Weights must sum to 1.0 |
| Make a metric score | `adacli <instance> custom-metrics activate <id>`, then check `custom-metrics list --json` shows it active |

Read the `state` in each `create` result. A draft metric does not score.

`--subject` is required on an instance with `custom-metrics-v2` and refused on one
without. If `create` is refused for the subject, read the error and retry with
or without it. If Ada's authoring review returns a 422, the message names the
reason, so fix the wording and retry.

Backfilling chats that ended before a metric existed needs a Platform API key with
the `custom_metrics:write` scope: `POST /api/v2/analytics/custom-metrics/backfill`
with `start_date` and `end_date`. A multi-day range can return a gateway 504 while
the server keeps queuing, so check the scored counts per day before you retry or
chats are queued twice.

`create` changes what Ada scores on live chats. Run it only after the person
approved the set in chat.

## Inside Ada Architect

The same commands work. Architect's review panel can show the proposed table. Do
not create metrics before the person approves.
