# voice-playbook-builder on the command line

For Claude Code or any shell with `adacli`, and for Ada Architect. Every
command below is plain `adacli` or a script in this skill's `scripts/` folder.
Run scripts from the skill folder. Replace `<inst>` with the builder's
instance.

## Connect and check

| Step | Command |
|---|---|
| Install and log in | `setup-adacli`, or `brew install adasupport/tap/adacli`, then `adacli <inst> login` |
| Setup check (run first) | `python3 scripts/prereq_check.py --instance <inst>`. It checks adacli is current, the session is live, and reads client behaviours from real calls. Fix every FIX line |
| Live playbook schema | `adacli <inst> playbooks steps-schema`. Its nesting limit and re-ask default can differ from the MCP's `describe_entity`. Where they disagree, trust the MCP |
| General V2 rules | `adacli docs claude-code --print` (nothing on voice) |

## Steps in the skill

| Step in the skill | Command |
|---|---|
| Read the live playbook | `adacli <inst> playbooks get <id> --json` |
| List variables, actions, handoffs | `adacli <inst> variables list`, `adacli <inst> actions list`, `adacli <inst> handoffs list` |
| Create a variable | `adacli <inst> variables create`. It goes live at once, so prefix the name |
| Stage actions, tools and the playbook | `adacli <inst> changesets stage --name "<name>" --file <changes.json>`. Add `--changeset <id>` to add to one you staged |
| Read what a changeset changes | `adacli <inst> changesets get <id> --diff` |
| Check each ask's deviation settings | `adacli <inst> playbooks deviations <id>`. Set one ask with `playbooks update-step <id> <step-id> --on-... <value>` |
| Save a test case | `adacli <inst> testing cases create --from-json <file>` (set the voice channel on the case) |
| Run cases on the changeset | `adacli <inst> testing runs create --cases <ids> --changeset <id>`. Run again without `--changeset` for live |
| Read a run | `adacli <inst> testing runs get <run-id>`, then `python3 scripts/runsummary.py --instance <inst> --prefix <var prefix> <run ids>` |
| Quick check in chat | `adacli <inst> chat talk --changeset <id> --var <name>=<value> --transport http`. Good for logic and wording, blind to voice behaviour |
| Read a call in full | `python3 scripts/monitor.py --instance <inst> --conversations <id> --detail`. Or `adacli <inst> conversations get <id>` |
| Read real calls through a playbook | `python3 scripts/monitor.py --instance <inst> --playbook <id> --start <date>` |
| Test an action with literal values | `python3 scripts/action_test.py --instance <inst> --action <id> --set <var id>=<value>` |
| Update an action's code | `adacli <inst> actions update <id> --request-body '{"request_body": "<json>"}'`. A raw PUT on the action endpoint returns 500 for every body |
| Promote | `adacli <inst> changesets promote <id>` returns a preview. The person confirms, then it runs with `--yes` |
| Roll out by percentage | `adacli <inst> changesets set-rollout <id> --percent <n> --max-conversations <n>`. End it with `changesets stop-rollout <id>` |
| Roll back | `adacli <inst> changesets revert <id> --name "<name>"`. It builds a new changeset that undoes it; promote that |

## Scripts

All use the adacli session (`adacli <inst> login` first). They read; only
`ada_api.py` can write, and only to the playbooks and actions you allow-list.

| Script | What it does |
|---|---|
| `prereq_check.py` | Adacli current, session live, MCP signed in, client behaviours read from real calls |
| `runsummary.py` | One screen per test run: pass/fail, failed criteria, what was said, variables set |
| `monitor.py` | Reads calls and flags what didn't go as designed |
| `action_test.py` | Runs an action with literal values and shows what each output stores |
| `ada_api.py` | The dashboard API helper the others import |

## What this route cannot do

- It cannot read the live schema the way the MCP's `describe_entity` does.
  `playbooks steps-schema` is close, so confirm any field it disagrees on over
  the MCP, or in the dashboard.
- Sessions expire after about a day. When a script says the session expired,
  run `adacli <inst> login` again.
- Greeting edits, caps on tools and playbooks, and a client's deviation
  switches are dashboard or Ada-support steps. Give the builder the exact
  block or setting to change.

## Inside Ada Architect

The chat draws the changeset card and gates promote. Do not run
`changesets promote` yourself: the person approves it. Outside Architect,
nothing gates for you, so show the diff and wait for a yes in chat before any
promote or rollout.
