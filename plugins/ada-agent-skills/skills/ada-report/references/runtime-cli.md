# ada-report on the command line

For Claude Code or any shell with `adacli` logged in to the agent. Every step
here only reads. Replace `<instance>` with the agent's handle. Read
`adacli <instance> --help` or the adacli guide for a flag you have not used.

| Step in the skill | Command |
|---|---|
| Headline metrics | `adacli <instance> analytics summary --start YYYY-MM-DD --end YYYY-MM-DD --json` for volume, resolution and satisfaction. Run it again for the equal period before. Read the JSON keys before you quote one |
| Topic volumes and how each resolves | `adacli <instance> analytics topics --start YYYY-MM-DD --end YYYY-MM-DD --json` gives volume, resolution, containment and satisfaction per topic |
| Conversations to quote | `adacli <instance> conversations search --start … --end … --json`, with `--handoff` for conversations passed to a person, `--csat 1 2` for low scores, `--topic <topic>` for one topic, `--size <n>` for page size. Add `--all --limit <n>` to walk pages |
| Read a conversation in full | `adacli <instance> conversations log <id>`: messages and the agent's events interleaved. These are the signals `ada-in-action.md` maps to notes. `conversations transcript <id>` gives messages only. `conversations details <id>` gives resolution, summary, guidance and coaching applied. Add `--json` for structured output |
| Many transcripts at once | `adacli <instance> conversations export --start … --end … --transcripts --json -o <file> --limit <n>`. Read `capped` in the output: `true` means the cap stopped the walk |
| What the agent has (to name playbooks, actions) | `adacli <instance> playbooks list --json`, `adacli <instance> actions list --json`, `adacli <instance> code-tools list --json` |
| Interview choices | The AskUserQuestion tool when it exists, otherwise numbered options in chat |

Notes:
- A zero from `analytics summary` or `analytics topics` is not verified. A read
  failure returns the same zeros as a quiet period. Check a zero against a second
  source, such as `conversations search --size 1` for the same dates.
- Exit code `22` from a single-conversation reader means a degraded read. Retry it
  and treat the output as incomplete.
- Transcript fetches are rate limited. A large export may pause for up to a
  minute.
- Use `--start` and `--end` with dates rather than `--since`, so the prior period
  has exactly the same length.
- No command draws the report. `scripts/report.py` renders the HTML, and the
  person prints it to PDF from the browser.

## Inside Ada Architect

No Architect-only steps. The report is a local file, so give the person its path.
