# Bring your own email domain, DNS and extra inboxes

Use when the person wants replies to come from their own domain, wants a
second inbox, or says replies come from an Ada-provided address.

## Preconditions

- Owner or Admin role.
- Access to the domain's DNS.
- A mail provider that can forward each support address to Ada.
- The current inbox list and forwarding noted by hand.

## Steps

1. Open Config > CHANNELS > Email > Configuration > Bring your own domain.
2. Add the domain. Ada shows 3 CNAME records and 1 TXT record for each
   domain. Add them at the DNS host.
3. Wait for Ada to show the domain as verified.
4. Each address is its own inbox and its own channel, with its own
   Ada-provisioned address. Add more with "Add inbox". Inboxes on the same
   domain reuse the DNS records.
5. Forward each support address to its inbox's Ada-provisioned address. The
   provisioned address follows the pattern of the agent handle on
   `email.ada.support`.
6. Keep the human team's address different from the AI Agent's address, or
   set up the Zendesk SMTP Connector (per domain) so escalated replies do not
   loop back to the AI Agent.
7. Set the sender name per channel on the Customization tab.

If no DNS is set, replies come from the Ada-provided address. The Email API
route has a 422 error when the reply-as and reply-to addresses match, which
means a forwarding loop.

## Downtime risk

Adding a domain or an inbox: none expected, because nothing receives mail
until forwarding points to it. Deleting an inbox or changing a domain stops
mail for that address. See `email-sender-address-change.md` for the
no-downtime order.

## How to verify

Send a test email to the new address. Confirm a conversation appears and the
reply's From address is the BYO address.

## Rollback

Remove the forwarding rule for the new address, then delete the inbox. DNS
records stay in place and are harmless. Restore any rule noted before.

## Source

- `product-docs/fern/versions/pages/docs/channels/email/email-configuration/byo-domain.mdx`
- `.../email-deployment.mdx`, `.../implementation-method.mdx`, `.../overview.mdx`
- `.../appearance-settings.mdx` (sender name per channel)

## OPEN or ASSUMED

- OPEN: how long DNS verification takes. Not in the docs.
- OPEN: the docs do not say how to read an inbox's settings by API.
