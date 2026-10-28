# onboard-agent on the command line

For anyone with `adacli` installed and logged in. Checked against
`adacli --help` (0.13.0), the adacli source and read-only runs on four real
instances on 28/10/2026. Replace `<instance>` with the agent's handle. Output
is JSON when piped, and `--json` forces it.

Contents: the inventory reads (step 1), what this route cannot read, the
write routes, and traps.

## Inventory reads (step 1)

Make every call read-only.

| Evidence | Command | What to read |
|---|---|---|
| Connection works | `adacli <instance> status --json` | `status` is anything but `not_logged_in`. Otherwise `setup-adacli` |
| Foundation, languages, redactions, channels (read first) | `adacli <instance> client show --json` (`client info` is an alias) | One call returns these keys, seen on real instances: `bot_persona`, `language`, `translated_languages`, `auto_translation`, `redactions`, `custom_redactions`, `image_redactions`, `platforms`, `scheduled_block_schedules`. What each key holds is inferred from its name (ASSUMED). The output also holds a token field. Select only the keys you need, for example with `jq`, and never print or save the whole output |
| Company description, persona (extra detail) | `adacli <instance> client persona show --json` | `company_description`, `personality`, `message_length`, `instructions`. Use it where the account allows it |
| Languages (extra detail) | `adacli <instance> snapshot export --include languages --json` | The `languages` key under `config`. The command exports a configuration snapshot to the terminal and changes nothing. `languages list` only prints the 60 supported languages, so do not read it as the enabled set |
| Redactions (extra detail) | `adacli <instance> redactions list --json` | `builtin` (each `key` and whether `active`) and `custom` |
| Glossary | `adacli <instance> glossary list --json --size 100` | Count and terms. Page with `--page` |
| Knowledge sources | `adacli <instance> knowledge sources list --json` | Each source and its sync state |
| Knowledge total | `adacli <instance> knowledge list --limit 1 --json` | `meta.total_items` (the table view prints "(N total)") |
| Knowledge coverage | `adacli <instance> knowledge probe --query "<question>" --json` | The articles that rank for the question. Run one per top question |
| Handoffs | `adacli <instance> handoffs list --json` | Each handoff and whether it is live |
| Handoff platforms | `adacli <instance> handoffs integrations list --json`, then `handoffs integrations get <integration> --json` | Which integration is configured and enabled |
| Handoffs working | `adacli <instance> conversations search --handoff --since 30d --json`, and again with `--test-users` | `total` |
| Tools | `adacli <instance> actions list --json`, `code-tools list --json`, `mcp list --json`, `mcp tools list --json` | Enabled state, and connection state for MCP servers. Treat a name or description that says placeholder, stub or template as not real |
| Playbooks | `adacli <instance> playbooks list --json` | Name and enabled state |
| Channels (extra detail) | `adacli <instance> channels list --json`, then `channels get <id-or-name> --json` | The enabled flag per channel (the table view shows an Enabled column). Use it when `platforms` in `client show` does not show the enabled state |
| Channel traffic | `adacli <instance> conversations search --since 30d --channel <id> --json` | `total` of real conversations. Test users are excluded unless you pass `--test-users` |
| Custom metrics | `adacli <instance> custom-metrics list --json`, `scorecards list --json` | State and count of each |
| Metric results | `adacli <instance> custom-metrics conversations <metric-id> --start <date> --end <date> --json` | Whether any conversation has a verdict. The list includes test conversations |
| Test cases | `adacli <instance> testing cases list --json` | Count and channel per case |
| Test results | `adacli <instance> testing runs list --json` | Latest run per case and its status. Add `--status` to narrow |
| Test quota | `adacli <instance> testing quota --json` | Runs left today |
| Changesets | `adacli <instance> changesets list --status testing --json`, then `--status promoted` | What waits and what shipped |
| Live volume | `adacli <instance> conversations search --since 30d --json` | `total` of non-test conversations |

## What this route cannot read

- Which handoff is the fallback: no command shows it. Dashboard: Config > AI
  AGENT > Handoffs.
- Off-hours schedules: `client show --json` key `scheduled_block_schedules`
  gives each schedule's name, timezone, weekly hours and special days (seen
  on real instances). `handoffs get <id> --json` shows a `scheduled_block`
  when a handoff branches on a schedule, and its schedule id matches. Dashboard:
  Config > AI AGENT > Handoffs, Off hours tab, Schedules.
- Image redactions (the two image toggles and the withheld-image message):
  `client show --json` key `image_redactions`. `redactions list` covers
  built-in and custom rules only. If the key is empty on your instance, the
  stage is Unknown. Dashboard: Config > AI AGENT > Settings, Preferences tab,
  Image redactions.
- Persona fields beyond the four `persona show` prints (agent name, company
  name, emoji): look under `bot_persona` in `client show --json`. If a field is
  absent, it is Unknown. Dashboard: Config > AI AGENT > Settings, Preferences
  tab.
- Custom metrics and scorecards on an instance without the feature: the read
  fails with FORBIDDEN (403) "Feature not available". Grade Custom metrics
  Unknown, not Not started. Dashboard: Analytics > Metrics. The error text can
  say adacli is out of date. Observed on 0.13.0, that is misleading: the adacli
  source ties the same error to instance flags (`custom-metrics-mvp`,
  `custom-metrics-v2`), so the feature is off for the instance, not the CLI.

## Writes

The skill makes no write on its own. Writes in a stage go through that
stage's skill. Foundation is the one exception, and only after the person
approves a preview. None of these commands uses a changeset: each goes live
at once. Keep the "before" value from the read above in the preview, so the
person can reverse it.

| Foundation item | Command |
|---|---|
| Company description, tone, message length, time zone | `adacli <instance> client persona update` with `--description`, `--personality`, `--length` (`concise` or `normal`) and `--timezone` (an IANA name). It merges onto the current persona, so fields you leave out stay. The help does not list the `--personality` values: the docs name Friendly, Plainspoken, Playful and Sophisticated. Match the spelling that `persona show` returns, and read it back after the write. If the value is rejected, use the dashboard |
| Built-in redaction on or off | `adacli <instance> redactions enable <key>` or `disable <key>`, with the `key` from `redactions list` |
| Custom redaction | `adacli <instance> redactions create --key <name> --pattern <regex>`. Test the regex on sample values first. A pattern that is too broad removes information the agent needs |
| Glossary term | `adacli <instance> glossary create --external-id <id> --user-term <lang:term> --ai-agent-term <lang:term> --definition <text>`. Add `--mode custom` when a user term should trigger the agent term, and `--voice` to detect it on calls |
| Languages | No command. Dashboard: Config > AI AGENT > Settings, Languages tab |
| Agent name, company name, emoji, avatar | No command. Dashboard: Config > AI AGENT > Settings, Preferences tab |

## Traps

- `glossary import` is a full sync: terms absent from the file are deleted.
  Seed with `glossary create`, or run `glossary export` first and edit that
  file.
- `channels enable` and `disable` change a live channel at once. Preview and
  get approval first.
- `knowledge list` pages 25 at a time. Quote `meta.total_items`, not the
  length of one page.
- `custom-metrics conversations` and `testing runs list` can include test
  conversations and old runs. Say which window and which changeset you read.
