# diagnose-conversation on the command line

For Ada Architect, and for Claude Code or any shell with `adacli` and the
Architect helpers (`tools/ada-architect/local/setup.py` installs them).

| Step in the skill | Command |
|---|---|
| Read the transcript | `adacli <instance> conversations get <id> --json` |
| Read the reasoning log | `ada-why <instance> <id>`: which playbook ran, which steps, which knowledge and coaching, where the playbook ended |
| See what a SET or tool wrote | `adacli <instance> conversations reasoning <id> --json`. Each `variable_value_set` event has `variable_name` and `new_value`, and a failed tool shows its `error_message`. The text `conversations log` never prints variable values, and `--all` adds only a bare `[variable_change]` line |
| Turn the conversation into a test case | `adacli <instance> testing cases from-conversation <id> --json` prints a screened draft and saves nothing. Follow its `instructions`, and `author-playbook/references/test-cases.md` section 8. Needs adacli 1.1.7 or later |
| Run it on the draft and on live | `ada-test <instance> --cases <ids> --changeset <id>` |
| "File it with provide-feedback" | Send it to Ada through your usual support channel |
| Links to conversations | `https://<instance>.ada.support/insights/conversations/<id>` |

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

## On a read-only instance

Diagnosis only reads, so it works. The re-test step creates a test run, which
a read-only instance refuses with exit code 7. Report the diagnosis and the
proposed fix as untested, and say a writable instance is needed to prove it.
Leave `~/.adacli/config` alone. `setup-adacli` has the full rule.
