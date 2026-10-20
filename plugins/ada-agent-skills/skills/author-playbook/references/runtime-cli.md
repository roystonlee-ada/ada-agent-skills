# author-playbook on the command line

For Ada Architect, and for Claude Code or any shell with `adacli` and the
Architect helpers (`tools/ada-architect/local/setup.py` installs them). Inside
Ada Architect the chat draws and gates for you. Outside it, nothing does, so
the last column replaces those pieces.

| Step in the skill | Inside Ada Architect | Claude Code with `adacli` |
|---|---|---|
| The approved design | The chat sends DESIGN-APPROVED with the board | The person approved the board in chat. Build from the last round of `~/.ada-architect/<instance>/boards/<work>-r<round>.design.txt` |
| List saved cases | `adacli <instance> testing cases list` | the same |
| Save a case | `adacli <instance> testing cases create --from-json <file>`. Fields: `says` (first customer turn), `then` (later customer turns), `good`, `fail` | the same |
| Record the use case | Emit the block below. The chat saves it to memory | Write the same JSON to `~/.ada-architect/<instance>/use-cases/<use_case>.md`, and rewrite it once the playbook names exist |
| Platform detail | The toolkit's `references/playbook-authoring.md` and its Ada Architect overlay | The workspace's ada-agent-toolkit skill (`references/playbook-authoring.md`), then `tools/ada-architect/skills/_overlays/ada-agent-toolkit/references/playbook-authoring.md` |
| List code tools | `adacli <instance> code-tools list --json` | the same |
| Test a code tool | `run_code_tool` | `run_code_tool`, or the code tool's test command in `adacli` |
| Stage the draft | Put `design: <work>` on the changeset card so the chat links the draft to the approved design. A draft without one is held back | No card. After staging, run `ada-changeset <instance> <id>` and show its summary, the changeset id and the design's `work` in chat |
| Check routing | `ada-route <instance> --changeset <id> ...` | the same |
| Run the cases | `ada-test <instance> --cases <ids> --changeset <id>`, then the test cases block with `results` and a link per conversation | the same command, then a table: case, live, draft, a one-line note, and links to both conversations as `https://<instance>.ada.support/conversations/<id>` |

The use-case record, as the chat reads it:

```
<<<ADA-USE-CASE>>>
{"use_case": "damaged-item-refund", "playbooks": ["Damaged item refund"], "case_ids": ["<id>", "<id>"]}
<<<END-ADA-USE-CASE>>>
```

No gateway holds a draft without an approved design outside Ada Architect,
and nothing shows the diff for you, so both rest on you. Never promote: the
person does it, and the workspace's changeset-guard hook checks every promote.
