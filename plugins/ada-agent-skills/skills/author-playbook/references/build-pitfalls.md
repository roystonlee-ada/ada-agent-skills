# Build pitfalls in Playbooks 2.0

Each item below caused a wrong turn in a live agent. Each was checked against
how the playbook engine works. From a customer's review (07/11/2026).

| Pitfall | What happens | Build it this way |
|---|---|---|
| Copying a variable with a generative SET | A silent generative SET returns `unable_to_provide` when the model call fails or finds nothing, so the copy sometimes comes out empty | Use an Exact SET whose value is the other variable's pill. It copies the value with no model call |
| An `else` with no steps | Sections run as one list in printed order. An empty `else` carries on after the IF_ELSE and falls into the next section | End every branch chain with an explicit go-to or exit |
| New steps at the start of a section | A go-to points at a step, not at a section. Go-tos that pointed at the old first step jump past the new steps | After inserting, retarget every go-to that pointed at the old first step |
| An ASK set to `only_when_needed` | The step first reads the conversation for an answer and asks only when it finds none. An earlier message that looks like an answer skips the question. Rewording the instruction does not stop this | Set the ASK to `always` when the customer must answer it now |
| `contains` on a short code | Conditions ignore case by default (`match_case` is false) and `contains` matches inside a word, so `contains "RSA"` matches "UNIVERSAL" | Use `is` for short codes, or `contains` on a longer, unique string |
| A caution in general instructions | General instructions go into every step's prompt, so a caution meant for one step changes the wording of all of them | Scope it in the sentence ("When you ask for the refund reason, ...") or move it to that step |
| Zero re-asks and no fallback | At the re-ask cap the ASK writes its fallback, or leaves the variable empty, and moves on. With `max_reask_attempts: 0` one non-answer ("thanks, that's all") leaves it empty, and a later action runs without it | Give the ASK a fallback, or branch on `is null` before the action. `scripts/check_ask_instructions.py` rule A4 flags this |
| `is null` on a value of `""` | `is null` does not match an empty string | Clear a variable with no value, not `""`. In a test case, leave the variable out instead of presetting it to `""` |
| A yes/no variable in a send | A yes/no pill prints `True` or `False` in the message, capital letter and all (sandbox check, 07/11/2026) | Branch on the variable with `is true` and write the customer's words in each branch |
| A full-sections stage that drops `reasoning_level` | A staged change replaces every step. A step sent without `reasoning_level` is staged as Normal, with no warning, even if it is High on live (sandbox check, 07/11/2026) | Start from `playbooks export-steps <id> --sections`, which carries `"reasoning_level": "high"`, and edit that file. Check the staged change for each High step before you test it |
| An action output saved by variable name | `variable_name` on an action output takes the variable's ID. A name there is accepted when you save the action, then the action fails on every call with "is not a valid ObjectId", and the playbook carries on without the value | Put the variable ID in `variable_name`. Read it back with `actions get <id> --json` |
