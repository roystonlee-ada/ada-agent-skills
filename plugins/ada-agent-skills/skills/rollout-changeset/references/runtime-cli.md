# rollout-changeset on the command line

For anyone with `adacli` logged in to the instance, and for Ada Architect. The
instance comes first in every command, and there is no `--instance` flag.

| Step | Command |
|---|---|
| Active rollouts on the instance | `adacli <instance> changesets list --json`, read each `rollout.percentage` and `rollout.status` |
| Start or raise a stage | `adacli <instance> changesets set-rollout <id> --percent <n> --max-conversations <cap>`. The percents across active rollouts must total 100 or less |
| Stop a rollout | `adacli <instance> changesets stop-rollout <id>`. Safe to repeat |
| Chats on the changeset so far | `adacli <instance> changesets get <id> --json`, read `rollout.applied_count` |
| Find the sampled chats | `adacli <instance> conversations search --since <date>` with the changeset filter. It needs `--since`, caps a page at 50 and reports no total, so quote counts as lower bounds |
| Settled check | `adacli <instance> conversations get <id>`, then `conversations reasoning <id>` |
| Transcript | `adacli <instance> conversations transcript <id> --json` |
| Playbook ownership of a line | `adacli <instance> conversations reasoning <id> --json` (see the attribution steps in `rollout-metrics.md`) |
| Custom metric verdicts per chat | `adacli <instance> custom-metrics conversations` |
| Judge the whole rollout | `adacli <instance> changesets compare <id> --start <date> --end <date>` |

`set-rollout` and `stop-rollout` change what live customers meet. Run them only
when the person has asked for that step in chat. A stop that the stop check
triggered needs no second ask: run it, then report.

## Inside Ada Architect

The same commands work. Architect's gateway may also show the rollout in the
review panel. Promote stays with the person (`promote-changeset`).
