# diagnose-conversation on the command line

For Ada Architect, and for Claude Code or any shell with `adacli` and the
Architect helpers (`tools/ada-architect/local/setup.py` installs them).

| Step in the skill | Command |
|---|---|
| Read the transcript | `adacli <instance> conversations get <id> --json` |
| Read the reasoning log | `ada-why <instance> <id>`: which playbook ran, which steps, which knowledge and coaching, where the playbook ended |
| Turn the conversation into a test case | `adacli <instance> testing cases from-conversation <id>` |
| Run it on the draft and on live | `ada-test <instance> --cases <ids> --changeset <id>` |
| "File it with provide-feedback" | Send it to Ada through your usual support channel |
| Links to conversations | `https://<instance>.ada.support/conversations/<id>` |

## The diagnosis block

Inside Ada Architect the prompt defines it and the chat checks it. Outside it,
publish it in chat as a fenced block:

```
<<<ADA-DIAGNOSIS>>>
symptom: what the customer experiences, in their words where you have them
mechanism: why it happens - the actual step, rule or gap, not a restatement
surface: playbook
surface_why: one sentence on why that surface owns the fix
ruled_out: knowledge - the article exists, retrieves at 0.82, and reads right
ruled_out: trigger - 96% of these route here already, so it is not too broad
evidence: <conversation id> - what in it shows the mechanism
confidence: high
<<<END-ADA-DIAGNOSIS>>>
```

- `surface` is one of: playbook, knowledge, coaching, general_instructions,
  action, trigger, persona, glossary.
- At least two `ruled_out` lines, and at least one `evidence` line with a real
  conversation id.
- No gateway checks the block before a change outside Ada Architect, so a fix
  without one is on you.
