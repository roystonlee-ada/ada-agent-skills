# Playbook health over adacli

Use the persisted export and graph conversion procedure in
`../../author-playbook/references/runtime-cli.md`, under "Convert persisted
configuration to a graph". Inspect installed command help before retrieving
related guidance, knowledge, variable definitions or existing conversations.
Read only the sections needed for this intent.

Run the local prose and ASK checkers from the installed author-playbook skill
against the same decoded playbook JSON files:

```sh
python3 <author-playbook-skill>/scripts/check_playbook_text.py --help
python3 <author-playbook-skill>/scripts/check_ask_instructions.py --help
```

Use the documented input and scope options. Exit 1 reports rule findings;
inspect the output before treating it as an execution failure. Keep exports
and reports in the authorized artifact location. Do not execute write, test,
stage or promotion commands as part of this review.
