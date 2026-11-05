# Move a Zendesk token connection to OAuth

Use when the person asks about retiring the Zendesk API token and moving to
OAuth. Handoff wiring itself belongs to `configure-handoff`. This runbook
covers the platform side only.

## Preconditions

- Owner or Admin role.
- A Zendesk admin who can approve the OAuth connection.
- Record the current Zendesk connection: subdomain, which handoffs use it.

## Steps

1. Connect with OAuth at Config > Apps > Zendesk > Connect. The subdomain is
   shared across Zendesk handoffs.
2. With the multi-brand toggle on, authorise against the primary account
   subdomain.
3. Zendesk Support uses the OAuth route. Zendesk Messaging in adacli takes
   subdomain, email and an API token, so a token is still used there.
4. Re-check each handoff that uses Zendesk with `configure-handoff`. Do not
   edit handoffs from here.

## Downtime risk

Unknown. A handoff that loses its connection fails to hand off, so test one
handoff end to end before changing the next. Do not remove the token
connection until the OAuth one passes a test.

## How to verify

Run a handoff test through `configure-handoff` and confirm the ticket
arrives in Zendesk.

## Rollback

Reconnect with the recorded token connection.

## Source

- `product-docs/fern/versions/pages/docs/handoffs/zendesk/` (connect and
  multi-brand pages)
- `adacli/docs/guide.md` (`handoffs integrations`)

## OPEN or ASSUMED

- OPEN: the plan to retire Zendesk tokens is not in the docs. Ask Ada
  support for the date and path.
- OPEN: the Zendesk subdomain limit shows as 10 on one page and 3 on another.
