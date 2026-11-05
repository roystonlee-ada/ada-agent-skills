# design-conversation on the command line

For Ada Architect, and for Claude Code or any shell with `adacli` and the
Architect helpers (`tools/ada-architect/local/setup.py` installs them). Pick
the column that matches where you are. Inside Ada Architect the chat draws and
gates for you. Outside it, nothing does, so the second column replaces those
pieces.

| Step in the skill | Inside Ada Architect | Claude Code with `adacli` |
|---|---|---|
| Read the existing config | `ada-playbook <instance> --router`, and the four tool lists in the prompt | `ada-playbook <instance> --router`, `adacli <instance> actions list --json`, `adacli <instance> code-tools list --json`, `adacli <instance> mcp tools list` |
| How often the topic comes up | `ada-topics`, then a few transcripts with `ada-why` | the same |
| A use case already designed | `timeout 10 cat /mnt/memory/*/use-cases/*.md 2>/dev/null` | `cat ~/.ada-architect/<instance>/use-cases/*.md 2>/dev/null` |
| The choices block (at most two questions) | The chat's choices block | The AskUserQuestion tool when it exists, otherwise numbered options in chat |
| Show the board | Send the ADA-DESIGN block. The chat draws it, one scenario per tab | Write the block to `~/.ada-architect/<instance>/boards/<work>-r<round>.design.txt`, run `python3 "${CLAUDE_SKILL_DIR}/scripts/board.py" <instance> <that file>` (`ada-board` is the same script where the Architect helpers are installed), fix every warning it prints, then give the two-line summary in chat. Run it on every round. It opens the board in the browser once, then reloads that same tab on later rounds (Chrome or Safari), so never tell the person to open the file. Every turn, every scenario and the whole board has a comment field, and the top bar's Copy button copies them all for pasting into chat |
| Check the board before showing it | The chat applies the board limits | the script prints a `warnings` list. Show the board only when it is `[]` |
| Approve | The chat sends DESIGN-APPROVED | The person writes "approved", "approve" or "build it". Treat that as DESIGN-APPROVED for this `work`. Anything else is a comment: send the next round |

No gateway holds a build until Approve outside Ada Architect. "Never build
before Approve" rests on you alone: until the person approves, run no
`testing cases create`, `changeset create` or `playbooks create/update`.
