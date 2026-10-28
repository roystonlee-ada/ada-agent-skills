# Webhooks: add, stop, rotate the secret, replay

Use when a webhook endpoint stops receiving events, the person wants a new
endpoint, or a signing secret leaked.

## Preconditions

- Owner or Admin role.
- The endpoint URL, which must return a 2xx within 15 seconds.
- An Ada API key if the person uses the Webhooks API instead of the dashboard.
- Record the current endpoints, their event types, custom headers and
  channel filters. No snapshot holds webhooks.

## Steps

1. Open Config > PLATFORM > Webhooks. Read each endpoint's state.
2. An endpoint that failed for about a week is disabled automatically
   (retries use exponential backoff). Fix the receiver, then enable the
   endpoint again by hand.
3. To add one, choose Add Endpoint, enter the URL and the event types:
   end_user.created and updated, conversation.created, ended and message,
   audit_log.emitted, and the proactive call events.
4. To limit by channel, use the channel tags on the endpoint. Custom headers
   are on the Advanced tab.
5. To rotate the signing secret, retrieve or rotate it in the dashboard or the
   Webhooks API, then update the receiver. Plan for the receiver to reject
   events signed with the old secret once the secret changes.
6. To recover missed events, resend one event, or use Options > Recover Failed
   Messages for a time window. Svix Play is for testing only.
7. If the receiver filters by source IP, allow the Svix addresses for the
   instance's region.

## Downtime risk

Rotating the secret can drop events at the receiver until it holds the new
one. Missed events stay in the failed list for replay. Adding an endpoint
carries no risk to existing ones.

## How to verify

Send a test event and read the 2xx. Confirm the receiver verifies the
signature.

## Rollback

Delete an endpoint that was added. For a rotated secret, rotate again and
update the receiver. The previous value is not recoverable.

## Source

- `product-docs/fern/versions/pages/reference/webhooks/overview.mdx`

## OPEN or ASSUMED

- OPEN: the docs list the event types but this runbook does not repeat the
  payload fields. Read them on the page.
- OPEN: the EU receiver domain shows as `*.ada-eu.support` here and as
  `eu.ada.support` elsewhere. Use the host in the person's login URL.
- ASSUMED: the grace period for an old signing secret. The docs do not give
  one, so plan for none.
