# design-conversation on the command line

For Ada Architect, and for Claude Code or any shell with `adacli` and the
Architect helpers (`tools/ada-architect/local/setup.py` installs them). Pick
the column that matches where you are. Inside Ada Architect the chat draws and
gates for you. Outside it, nothing does, so the second column replaces those
pieces.

| Step in the skill | Inside Ada Architect | Claude Code with `adacli` |
|---|---|---|
| Read the existing config | Use the commands at right. `ada-playbook <instance> --router` is a shortcut for finding candidate playbooks | `adacli <instance> playbooks list --json`, `playbooks get <id> --json`, `actions list --json`, `code-tools list --json`, `mcp tools list` |
| Entry, exit and variables | Use the commands at right | `adacli <instance> channels list --json`, `channels get <id-or-name> --json`, `start-triggers list --json`, `variables list --json`, and `variables get <id> --json` for relevant fields. Read any assigned playbooks with `playbooks get <id> --json` |
| Policy and knowledge | Use the commands at right | `adacli <instance> knowledge list --page <n> --json` to find candidate articles, then `knowledge get <id> --json` for the full article. Open the supplied or linked policy pages and compare the applicable versions |
| How often the topic comes up and what people see | Use the commands at right, or `ada-topics` and `ada-why` | `adacli <instance> conversations search --help` to choose topic, channel and language filters. Read several matches with `conversations transcript <id> --json` and use `conversations log <id> --json` to check events and ordering |
| A use case already designed | `timeout 10 cat /mnt/memory/*/use-cases/*.md 2>/dev/null` | `cat ~/.ada-architect/<instance>/use-cases/*.md 2>/dev/null` |
| The choices block (at most two questions) | The chat's choices block | The AskUserQuestion tool when it exists, otherwise numbered options in chat |
| Show the board | Send the ADA-DESIGN block. The chat draws it, one scenario per tab | Write the block to `~/.ada-architect/<instance>/boards/<work>-r<round>.design.txt`, run `python3 "${CLAUDE_SKILL_DIR}/scripts/board.py" <instance> <that file>` (`ada-board` is the same script where the Architect helpers are installed), fix every warning it prints, then give the two-line summary in chat. Run it on every round. It opens the board in the browser once, then reloads that same tab on later rounds (Chrome or Safari), so never tell the person to open the file. Every turn, every scenario and the whole board has a comment field, and the top bar's Copy button copies them all for pasting into chat |
| Check the board before showing it | The chat applies the board limits | the script prints a `warnings` list. Show the board only when it is `[]` |
| Approve | The chat sends DESIGN-APPROVED | The person writes "approved", "approve" or "build it". Treat that as DESIGN-APPROVED for this `work`. Anything else is a comment: send the next round |

No gateway holds a build until Approve outside Ada Architect. "Never build
before Approve" rests on you alone: until the person approves, run no
`testing cases create`, `changeset create` or `playbooks create/update`.

Check a fresh conversation for the standard greeting and match the
transcript to the intended channel and locale. For anything the readback
does not show, use the instance dashboard's channel settings and the
assigned playbooks. If you still cannot verify greeting text, CSAT settings
or exit behavior, flag it as OPEN with the specific check needed.

## Inside Ada Architect

The native board accepts customer and bot turns. Put the core paths there
and include a readable transcript alongside the same board for translations,
system events and alternate paths. Follow [board format](board-format.md).
Label each supplement with its scenario ID and keep it in sync each round.
Use customer and bot dialogue in the native turns and mark proposed behavior
in the notes or supplement. When the
surface cannot show the supplement inline, provide it as a review artifact
alongside the board before asking for approval.
