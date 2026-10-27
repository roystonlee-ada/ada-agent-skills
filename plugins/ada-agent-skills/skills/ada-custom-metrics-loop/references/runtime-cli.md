# ada-custom-metrics-loop on the command line

For anyone with `adacli` logged in to the instance, and for Ada Architect. The
instance comes first in every command, and there is no `--instance` flag.

The health script ships with `ada-custom-metrics-improve`. Run it from that skill's
folder as `scripts/metric_health.py`.

| Step | Command |
|---|---|
| Metrics and scorecards | `adacli <instance> custom-metrics list --json` and `adacli <instance> scorecards list --json` |
| Baseline for all metrics | `python3 <improve skill folder>/scripts/metric_health.py <instance> --start <date> --end <date>`. Add `--json` for machine output |
| Baseline for one metric | The same script with `--metric <id or part of the name>` |
| Fail chat lists | The same script with `--fails-out <dir>` writes one file of failing conversation ids per metric |
| One metric's wording | `adacli <instance> custom-metrics get <id> --json` |
| Fail, pass or null chats | `adacli <instance> custom-metrics conversations <id> --result fail --start <date> --end <date> --json`. Rows are keyed `key`, the conversation id. A result returns at most 10,000 rows |
| Transcript | `adacli <instance> conversations transcript <conversation id> --json` |
| Why it went wrong | `adacli <instance> conversations reasoning <conversation id> --json` |
| Headline rates | `adacli <instance> analytics summary` over the same window |
| Resolution and CSAT per chat | `adacli <instance> conversations export --start <date> --end <date> -o <file>` |
| Edit wording | `adacli <instance> custom-metrics update <id> --scoring-guidance <text>`. Add `--subject ai_agent` for a metric made before the subject field |
| Apply a held edit | `adacli <instance> custom-metrics get <id>`, fix what the review names, then `adacli <instance> custom-metrics activate <id>`. `discard-edit <id>` drops it |
| Test a fix | `adacli <instance> testing runs create --cases <ids> --changeset <id>`, then `testing runs get <run id> --json` |
| Re-measure | `adacli <instance> changesets compare <id> --start <date> --end <date>`. It adds each enabled metric's pass rate for both arms and no interval |
| Next cycle's baseline | The baseline script again, with `--start` on the first full day after the change went live |

`update` applies in place when the authoring review passes. If the review flags the
edit, it stays held and off until `activate`. An edit counts only for chats that end
after it, so start the next window after the edit.

`custom-metrics update` and `activate` change what Ada scores on live chats. Run
them only when the person has asked for that change.

A metric with `--direction higher_is_worse` reads backwards: a pass there records
the bad behaviour, so a rising pass rate is a regression.

## Inside Ada Architect

The same commands work. Promote stays with the person (`ada-promote-changeset`).
