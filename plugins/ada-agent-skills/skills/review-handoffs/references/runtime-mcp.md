# review-handoffs over the Ada MCP

For anyone connected to their AI agent's Ada MCP server. Checked against the
live tool definitions on 20/10/2026, and against a live run on a sandbox
instance that day. Your host may prefix the tool names.

| Step | Tool call |
|---|---|
| Learn the filter | `get_available_filters`, and find `HANDOFFREASON` (operators `IS`, `ISNOT`) |
| Count one reason | `get_conversations` with `detail_level: IDS_ONLY`, both dates, and `HANDOFFREASON IS <code>`. Page with `offset` and `next_offset` until it ends, then count. A page holds 100 at most |
| Count all reasons | Repeat for each of the eight causes plus `system_failed` and `unclassified` |
| Read the reasoning | `get_conversation` on a sample id. The `handoff_triggered` entry carries `reason_code` and `reasoning.text` |
| Escalations | The `HANDOFF` filter, not `HANDOFFREASON` |
| Baseline and after | `compare_changeset_metrics` for the promoted change, plus the counts above over matching windows |

Two filter traps:
- `ISNOT` also returns conversations with no handoff at all. Use `IS` per code.
- `null` codes match no `IS` value, so they drop out of every count. Say so.

`IS` also matches failed attempts. The MCP doesn't show attempt outcomes, so
report these numbers as conversations with a handoff for that reason, not as
escalations. Test conversations are excluded by default, so a count here can
differ from a count that includes changeset test chats.
