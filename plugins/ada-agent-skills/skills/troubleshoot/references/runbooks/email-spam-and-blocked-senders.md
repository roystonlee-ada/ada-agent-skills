# Email spam, blocked and trusted senders, verification mail

Use when spam reaches the AI Agent through the email channel, a real sender
is blocked, or a verification email never arrives.

## Preconditions

- Admin or Owner role for trusted senders. Blocked senders are global across
  every email channel on the instance.
- The sender address or domain in question.

## Steps

1. Ada does not filter spam. For an address that gets spam, use BYO domain and
   the mail provider's own filters before forwarding to Ada.
2. To stop one sender, add it to the blocked senders list. It applies to all
   email channels at once.
3. To let a sender through, add it to trusted senders (up to 100 addresses at
   a time). An address cannot be both trusted and blocked, so remove it from
   one list first.
4. For a verification email that does not arrive, check whether the sender or
   its domain is on the blocked list, and check that forwarding points to the
   right Ada address.
5. A thread goes quiet after 72 hours of inactivity and holds at most 150
   messages. A late reply starts a new conversation.

## Downtime risk

None expected for list changes. They apply to new mail only. A blocked sender
gets no reply, so check the address twice.

## How to verify

Send a test message from the affected address and confirm whether it is
answered or ignored as intended.

## Rollback

Remove the entry from the list.

## Source

- `product-docs/fern/versions/pages/docs/channels/email/email-configuration/block-email-addresses.mdx`
- `.../trusted-senders.mdx`, `.../email-onboarding.mdx`

## OPEN or ASSUMED

- OPEN: the docs give no steps for a verification email that fails. Step 4
  is a check list, not a documented fix. If it does not resolve, ask Ada
  support.
