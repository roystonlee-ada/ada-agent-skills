# Audit log: who changed what

Use when the person asks who changed a setting, when, and from where.

## Preconditions

- Access to the profile menu in the dashboard.

## Steps

1. Open the profile menu, then Audit log.
2. Read the columns: Timestamp (UTC), Activity, Entity, Actor (a user or an
   API key) and Interface (Ada Dashboard, API, MCP, Import or Export).
3. Entities include playbooks, articles, knowledge sources, tools, handoffs,
   API keys, Team Access, SSO configuration and Session limits.
4. The date range defaults to the last 30 days. Filter by Interface, Actor,
   Activity or Entity with "Is" or "Is not", or search an entity name.
5. Download a CSV for a longer review. A download holds at most 10,000 rows,
   so narrow the date range first.
6. To stream events to another system, use the audit_log.emitted webhook
   (`webhooks.md`).

Convert the UTC timestamps to the person's zone before comparing with their
own notes.

## Downtime risk

None. It is read-only.

## How to verify

Find the entry for a change the person just made.

## Rollback

Not applicable. The log does not undo anything. Reverse a content change from
the Change sets page, or put a recorded setting back by hand.

## Source

- `product-docs/fern/versions/pages/docs/other/audit-log/overview.mdx`
- `api/core/analytics/audit_log/stores/clickhouse.py` (entity labels)

## OPEN or ASSUMED

- OPEN: how long audit history is kept is not stated in the docs.
- Not covered by the log: edits that never reach the entities listed above.
  ASSUMED, not tested.
