# refresh-intent-taxonomy over the Ada MCP

For anyone connected to their AI agent's Ada MCP server. Checked against the
live tool definitions and read-only calls on a sandbox instance on 30/10/2026.
Your host may prefix the tool names.

## What the tools do

| Step | Tool call |
|---|---|
| Active Topics, Intents, scope, signals, excludes | `list_entities` with `entity_type: topics` and `detail: full`. Intents nest under each Topic with their ids. Do not pass `limit` (it is for variables only) |
| Volume for one Topic or Intent | `get_ada_metric` with `conversation_volume_opened` and a `TOPIC` or `INTENT` filter (`IS`, the id) over the window |
| Resolution rate and CSAT for one intent | `get_ada_metric` with `resolution_rate`, `csat_rate` and the same `INTENT` filter |
| Conversations for one intent | `get_conversations` with `detail_level: IDS_ONLY` and the `INTENT` filter. Page with `offset` and `next_offset`. Add `ISTESTUSER IS true` to count test traffic |
| One conversation's classification | `get_conversation`. Its `classifications` list holds each Topic and Intent with a `confidence` and a `status` (`recommended` was seen), and the `__other__` bucket with `__unclassified__` |
| Create a Topic or Intent | `edit_agent_config` with `entity_type` `topic` or `intent` and `operation: create`. Call without `fields` first to read the schema, show the preview, and set `confirmed` only after the person agrees. The edit is live at once |

Use `get_available_filters` first. It lists `TOPIC` and `INTENT` (both `IS` and
`ISNOT`) and `ISTESTUSER`. `get_conversations` always needs `start_date` and
`end_date`. Test conversations are excluded unless you add `ISTESTUSER IS true`.

Split real from test volume by running each count twice, once without and once
with `ISTESTUSER IS true`. The second count includes real conversations too, so
subtract the first from it to get test-only.

## What the MCP cannot do

Seen in the live schemas and calls:
- `list_entities` on `topics` returned only the active Topic and its Intent. A
  recommended intent met in a conversation's `classifications` was not in that
  list, so the MCP does not list recommendations.
- No tool returns recommendation volume or trend, or the "other" share. The
  `__other__` bucket has no id to filter on, so compute the share: total
  volume minus the sum of the Topic volumes, over total volume. The conversation
  counts for a classified Topic can overlap, so call the result approximate.
- `get_conversations` `SUMMARY` has no Topic or Intent column. Use
  `get_conversation` per sample.
- No tool approves or dismisses a recommendation. `edit_agent_config` lists
  `topic` and `intent` as entity types, but whether an update promotes a
  recommended intent was not tested, so do not assume it.

Do these steps in the dashboard: **Analytics > Topics & Intents**. Read the
recommended list with volume and trend, approve or dismiss there, and edit an
intent in place. The CLI route (`references/runtime-cli.md`) covers moves and
Topic or Intent creation if adacli 1.1.0 is available.
