# ada-tune-reasoning-level on the command line

For Claude Code or any shell with `adacli`. Replace `<instance>` with the agent's handle.

| Step in the skill | Command |
|---|---|
| Inventory every in-scope step | `python3 "${CLAUDE_SKILL_DIR}/scripts/inventory.py" <instance>`. Add `--playbook <id>` for one playbook, `--json` for a file. It reads every V2 playbook, so a large agent takes a few minutes. |
| Read one playbook's steps | `adacli <instance> playbooks export-steps <id> --sections > steps.json` |
| Find past values for a step | `adacli <instance> conversations reasoning <conversation-id> --json`. Each `variable_value_set` event carries `variable_name` and `new_value`. |
| Time one step | In the same output, subtract the `created_at` of the previous event from the `created_at` of the step's `variable_value_set` event. |
| Stage the change | Edit `reasoning_level` in `steps.json`. Wrap it as `[{"entity_type": "playbook", "change_type": "modified", "entity_id": "<id>", "fields": {"sections": <the sections array>}}]`, then run `adacli <instance> changesets stage --name "<name>" --summary "<one sentence>" --file change.json` |
| Add a second playbook to the same changeset | The same command with `--changeset <changeset-id>` |
| Check the level landed | `adacli <instance> changesets get <changeset-id> --json`, then read `reasoning_level` in `changes[].fields.sections` |
| List saved cases | `adacli <instance> testing cases list` |
| Run cases on live and on the draft | `adacli <instance> testing runs create --cases <ids...> --repeat 3`, then the same with `--changeset <changeset-id>`, then `adacli <instance> testing runs compare` |
| Test one step with your own inputs | Copy the playbook to a scratch playbook in a sandbox, then stage the change there. See "A/B in a sandbox" below. |

## Gotchas

- A playbook that stores `sections` ignores a flat steps file. `playbooks update --file` prints success and changes nothing. Always export with `--sections` and push the same shape.
- `playbooks update` writes live. Use it for a scratch copy only. A real change goes through `changesets stage`.
- `playbooks update-step` has no reasoning flag. Edit the JSON.
- The API accepts exactly `normal` and `high`, in lower case, or no field. Any other value returns 400 `'reasoning_level' must be one of ['high', 'normal'] or absent`, in a live write and in a changeset.
- The API accepts `reasoning_level` on a send step and stores it. It does nothing there. Do not add it.
- Removing the field is the same as `normal`.
- A `sections` rewrite that drops a step's `reasoning_level` resets that step to Normal. Send every step's level back as you read it.

## A/B in a sandbox

Use this when no saved case reaches the step.

1. Create the variables the step needs and one output variable per arm.
2. Build one scratch playbook that asks for the input, then runs the same SET instruction three times: Normal, High, Normal again. The second Normal shows whether order alone changes the time.
3. End with a send step that prints the three outputs.
4. Start the playbook with a chat turn that reads as a command ("Run test case X now. Input: ..."), not as a question. A message that looks like a customer question is answered from Knowledge and the playbook never starts.
5. Send one turn per chat: `adacli <instance> chat talk`, one `__CONVO_ID__` per run. Read the three values and their times with `conversations reasoning`.
6. Run each input at least 4 times. Count a chat that did not reach the step as a missed run, not as a pass.
7. Deactivate the scratch playbooks when done, so the router does not pick them.

## Inside Ada Architect

Run the same commands. Do not promote: the person does it.
