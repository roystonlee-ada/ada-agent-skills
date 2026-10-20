# revise-playbook on the command line

For Ada Architect, and for Claude Code or any shell with `adacli` and the
Architect helpers (`tools/ada-architect/local/setup.py` installs them). Inside
Ada Architect the chat draws and gates for you. Outside it, nothing does, so
the last column replaces those pieces.

| Step in the skill | Inside Ada Architect | Claude Code with `adacli` |
|---|---|---|
| Read the live playbook (do this first) | `ada-playbook <instance> <id>`, then the same for every playbook it runs or that routes into it | the same |
| Load saved cases (do this second) | `adacli <instance> testing cases list` | the same |
| The use case's record | `timeout 10 cat /mnt/memory/*/use-cases/*.md 2>/dev/null` | `cat ~/.ada-architect/<instance>/use-cases/*.md 2>/dev/null` |
| Baseline for a handoff cut | `ada-export <instance> --since 7d --exclude-test-users --handoff-reasons`, as in review-handoffs | the same |
| Send the board again | Send the ADA-DESIGN block with the same `work`. The chat draws it | Write the block to `~/.ada-architect/<instance>/boards/<work>-r<round>.design.txt` and run `ada-board <instance> <that file>`, as in design-conversation's runtime file |
| Wait for Approve | The chat sends DESIGN-APPROVED | Wait for the person to write "approved", "approve" or "build it" in chat |
| Check old cases against the board (testing step 0) | Before a run, check each old case's `says` and `good` against the approved board. A case the board no longer matches goes back for review with `updated` | A case the board no longer matches goes to the person with the change you would make, not into the run |
| Run the whole set on draft and live | `ada-test <instance> --cases <ids> --changeset <id>`, then the test cases block with `results` | the same command, then the table: case, live, draft, a one-line note, links as `https://<instance>.ada.support/conversations/<id>` |
| The updated use-case record | Emit the ADA-USE-CASE block, as in author-playbook's runtime file | Rewrite `~/.ada-architect/<instance>/use-cases/<use_case>.md` |

The one-step wording change still needs no board. Everything else waits for
approval in chat outside Ada Architect, because no gateway holds the build
there. Never promote: the person does it, and the workspace's changeset-guard
hook checks every promote.
