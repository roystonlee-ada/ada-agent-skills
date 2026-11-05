# Rotate an API key

Use when a key leaked, a person who knew it left, or the team rotates on a
schedule.

## Preconditions

- Owner or Admin role.
- A list of everything that uses the key: scripts, webhooks calls, data
  export jobs, MCP clients, integrations.

## Steps

1. Read the key list and note the name of the key to replace. The value is
   shown once at creation and cannot be read later.
2. Create a new key. Ada allows several active keys at once, so the old key
   keeps working. Config > PLATFORM > API keys (scripted bots use Settings >
   Integrations > APIs).
3. Copy the new value once into the secret store each user reads from.
4. Update each user of the key to the new value.
5. For an MCP client on an API key, allow the new key's tools first. New keys
   start with no tools when individual MCP settings are on.
6. Verify each user works on the new key.
7. Delete the old key. Delete invalidates it at once.

Keys grant read and write to all APIs. A key labelled "(Legacy)" works for v1
of one API only and cannot be renamed.

## Downtime risk

None expected with the two-key overlap. Downtime appears when the old key is
deleted before every user has moved. If the key leaked, delete the old key
first and accept the break.

## How to verify

Make one read call with the new key from each user. Check the audit log for
the key's creation and deletion entries.

## Rollback

Before step 7: keep using the old key and delete the new one. After step 7
there is no rollback, because a deleted key cannot return. Create another key
and update the users again.

## Source

- `product-docs/fern/versions/pages/reference/introduction/authentication.mdx`
- `.../mcp/introduction/tool-permissions.mdx`
- `.../docs/other/audit-log/overview.mdx`

## OPEN or ASSUMED

- OPEN: the docs say keys do not expire, and adacli accepts an `--expiry`
  value. Treat keys as non-expiring.
- OPEN: one page says an API key cannot be renamed after creation and the
  authentication page says it can. Check in the dashboard.
