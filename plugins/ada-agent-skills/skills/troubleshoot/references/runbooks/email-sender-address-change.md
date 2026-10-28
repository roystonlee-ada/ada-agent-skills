# Change the email channel's sender or support address without downtime

Use when the person wants the AI Agent to answer from a different support
address (for example, from a new sender address on the same or another
domain). The reply-from address is always the address the end user wrote to,
so the sender changes when the inbox the customer writes to changes.

## Preconditions

- Person is an Owner or Admin on the instance (edit integrations needs it).
- Person can edit DNS for the new domain, and the mail forwarding rules on
  the mail provider.
- Record the current setup by hand first: each configured inbox, its
  Ada-provisioned address, the address forwarding to it, the sender name, the
  launch control setting and any Zendesk SMTP Connector. No changeset or
  snapshot holds email settings.

## Steps

1. Do not use the docs' "Handling changes to a domain" order (turn off
   forwarding, delete the channel, redo setup) for a live address. It leaves
   that address with no AI Agent until the setup is done.
2. Add the new inbox first with "Add inbox" under Config > CHANNELS > Email >
   Configuration. It is additive. The old inbox keeps working.
3. If the new address is on a domain that already has DNS records in Ada,
   Ada reuses them. If it is a new domain, add the 3 CNAME records and the 1
   TXT record Ada shows, and wait for them to verify.
4. Test with the new inbox's Ada-provisioned address before any customer
   mail reaches it. Do not give that address to customers.
5. Set the new address to forward to the new inbox's Ada-provisioned address.
   If forwarding leaves the mail provider's domain, allow `email.ada.support`
   on the provider.
6. Keep the old forwarding on until the new path is verified. Both
   addresses reply while they overlap.
7. Check each place the old address is named: launch controls (the secondary
   support address must differ from every Ada address), the handoff Email
   block recipient, the Zendesk SMTP Connector (set per domain), and any
   routing that filters on the recipient address variable.
8. Turn off the old address's forwarding, then delete the old inbox. The
   first inbox cannot be deleted, so rename it or keep it if it is the
   original one.

## Downtime risk

None expected when steps 2 to 6 run in order, because the old inbox keeps
receiving mail until the new one is verified. Downtime appears only if the
old forwarding is turned off first, or if the new forwarding points to a
wrong Ada address. Mail sent to a forwarded address that is not a configured
inbox still gets a reply, but from another configured address.

## How to verify

- Send a test message to the new address and read the reply's From address.
- Confirm a conversation appears on the Email channel in the dashboard.
- Send one to the old address during the overlap and confirm it still gets a
  reply.

## Rollback

Before step 8: turn off the new forwarding and delete the new inbox. The old
inbox was never touched. After step 8: add the old address back as an inbox
(the DNS records are reused if the domain is unchanged) and restore the
forwarding noted before the change. Expect a gap until forwarding is back.

## Source

- `product-docs/fern/versions/pages/docs/channels/email/email-configuration/byo-domain.mdx`
  (multiple inboxes, reuse of DNS, handling changes to a domain, reply-from)
- `.../email-deployment.mdx` (forwarding to the Ada address, `email.ada.support`)
- `.../launch-controls.mdx` (secondary support address rule)
- `.../handoffs/zendesk/zendesk-SMTP-connector.mdx` (connector per BYOD domain)

## OPEN or ASSUMED

- ASSUMED: the add-first order is the safe order. The docs describe only the
  delete-first flow for a changed domain. The add-first order follows from
  "Add inbox" being additive and old forwarding staying active.
- ASSUMED: DNS verification time. The docs do not give one.
- OPEN: whether the Ada-provisioned address of the first inbox can be
  changed. The docs say the first inbox cannot be deleted.
- OPEN: the inbox configuration keys are not in the docs, so a live read of
  the sender address is not possible through adacli or the MCP.
