# author-playbook on the command line

For Ada Architect, and for Claude Code or any shell with `adacli` and the
Architect helpers (`tools/ada-architect/local/setup.py` installs them). Inside
Ada Architect the chat draws and gates for you. Outside it, nothing does, so
the last column replaces those pieces.

| Step in the skill | Inside Ada Architect | Claude Code with `adacli` |
|---|---|---|
| The approved design | The chat sends DESIGN-APPROVED with the board | The person approved the board in chat. Build from the last round of `~/.ada-architect/<instance>/boards/<work>-r<round>.design.txt` |
| List saved cases | `adacli <instance> testing cases list` | the same |
| Save a case | `adacli <instance> testing cases create --from-json <file>`. Fields: `name`, `user_message` (first customer turn), `scenario` (what the simulated customer says later), `success_criteria` (a list), `language`, optional `variables` and `external_systems` | the same |
| Record the use case | Emit the block below. The chat saves it to memory | Write the same JSON to `~/.ada-architect/<instance>/use-cases/<use_case>.md`, and rewrite it once the playbook names exist |
| Platform detail | The toolkit's `references/playbook-authoring.md` and its Ada Architect overlay | The workspace's ada-agent-toolkit skill (`references/playbook-authoring.md`), then `tools/ada-architect/skills/_overlays/ada-agent-toolkit/references/playbook-authoring.md` |
| Check quick-reply labels | `adacli <instance> playbooks get <id> --json > pb.json`, then `python3 scripts/check_quick_replies.py pb.json`. It also takes a changeset file, so run it before `changesets stage`. Exit 1 means fix the labels first | the same |
| List code tools | `adacli <instance> code-tools list --json` | the same |
| Test a code tool | `run_code_tool` | `run_code_tool`, or the code tool's test command in `adacli` |
| Stage the draft | Put `design: <work>` on the changeset card so the chat links the draft to the approved design. A draft without one is held back | No card. After staging, run `ada-changeset <instance> <id>` and show its summary, the changeset id and the design's `work` in chat |
| Check routing | `ada-route <instance> --changeset <id> ...` | the same |
| Run the cases | `ada-test <instance> --cases <ids> --changeset <id>`, then the test cases block with `results` and a link per conversation | the same command, then a table: case, live, draft, a one-line note, and links to both conversations as `https://<instance>.ada.support/insights/conversations/<id>` |

The use-case record, as the chat reads it:

```
<<<ADA-USE-CASE>>>
{"use_case": "damaged-item-refund", "playbooks": ["Damaged item refund"], "case_ids": ["<id>", "<id>"]}
<<<END-ADA-USE-CASE>>>
```

No gateway holds a draft without an approved design outside Ada Architect,
and nothing shows the diff for you, so both rest on you. Never promote: the
person does it, and the workspace's changeset-guard hook checks every promote.

## If the instance is read-only

Run `adacli <instance> status --json` once at the start. If `read_only` is
`true`, say so before you plan any change: this skill's writes will be
refused. Offer a writable instance, or the steps that only read. A write that
exits with code 7 means the same. Stop, name the change, and leave
`~/.adacli/config` alone. `setup-adacli` has the full rule.

## Convert persisted configuration to a graph

Export one complete V2 playbook with section boundaries preserved:

```bash
adacli <instance> playbooks export-steps <id> --sections > playbook.json
python3 <author-playbook-skill>/scripts/playbook_graph.py playbook.json --identity <id> --state live --revision <source-revision> --channel <channel> --captured-at <ISO-8601-time> --output-dir <approved-artifact-folder>/live-graph
```

Use the installed skill directory for `<author-playbook-skill>`. A full
`playbooks get <id> --json` export is also accepted and normally includes the
identity. For a draft, obtain its persisted changeset configuration through
the installed CLI's verified read command, then use `--state draft` and the
changeset ID as `--revision`. Do not label a live export as a draft. Use a
separate output directory per revision; the two generated files are replaced
on rerun. The helper reads local JSON, uses Python's standard library and
does not call Ada or start tests. Exit 2 means invalid input or a file error;
exit 0 means files generated, not a passed graph review. See
`references/playbook-graph.md` for the evidence and review still required.

## Knowledge SET controls

Export the existing playbook steps and inspect the installed authoring guide
and command help before setting Knowledge-search or article-reference fields.
Do not infer a JSON field name from its dashboard label. Use the dashboard's
reasoning SET editor if those controls are absent from the verified schema.
The search and fallback design rules are in `references/knowledge-set.md`.

## Current CLI behavior to verify

CLI 1.8 creates a playbook inactive unless explicitly activated. Keep a new
playbook inactive while building and testing. CLI 1.6 added a stage override
for the reasoning level of all SET and ASK steps; do not apply that broad
override when preserving selected High steps. CLI 1.7 quota warnings still
start the test run, so check quota before invoking a run rather than treating
the warning as a preview. Verify the installed command help and version.

Source: https://docs.ada.cx/release-notes
