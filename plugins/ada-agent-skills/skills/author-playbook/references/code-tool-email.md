# Send an email from a code tool

Source: https://docs.ada.cx/docs/automation/tools/code-tools/inputs-outputs-and-environment#send_email--send-an-email-from-the-conversation

A code tool can call `send_email(to, subject, body, bcc=None, html=False,
reply_to=None)` with no import. It sends one email through the agent's Email
channel, from the channel's address and sender name, and returns
`{"sent": bool, "error": str | None}`.

## Build the tool

- Name every argument in the call. Put the values a teammate may change
  (subject, `html`, `reply_to`, `bcc`) in named settings at the top, so they
  can edit them without reading the code.
- Return `sent` and `error` as outputs. A refused send does not raise, so
  the playbook only knows it failed if it branches on `sent`. Only a wrong
  argument type raises and fails the run.
- For a one-time code, write the code with `set_variable` and return only
  `sent` and `error`. Never return the code as an output, and never let the
  agent read that variable: a customer can ask the agent for any value it
  can see, and then pass the check without the inbox. A later step compares
  the variable with what the customer types.
- Pass a no-reply `reply_to` when replies should go nowhere, such as for a
  code. It must be on a domain the Email channel has an address on. By
  default replies reach the agent as an email conversation.
- With `html=True`, links keep their address only when the domain is on the
  code tool allowed-domains list. Scripts, styles and images are stripped.
  The email has no attachments, no unsubscribe link, and no greeting or
  sign-off added. It is for a message tied to the chat, not a campaign.

## Build the playbook

1. SET the tool's inputs (for example the account email), then RUN it.
2. IF_ELSE on `sent`:
   - true: a SEND or ASK that says the email went out and names the address
     in part, then ASK for the code or carry on.
   - false: tell the customer it could not be sent and take the other route
     from the design. Use `error` to choose wording only when it changes what
     the customer should do (`invalid recipient`: ask for the address again).
3. The "didn't get it" path from the design: re-check the address, RUN the
   tool once more, then the other route. Do not loop the resend.

## Limits that shape the flow

| Limit | Value | `error` when hit |
|---|---|---|
| Emails per conversation | 10 | `conversation send limit reached` |
| Emails per address per day (`to` or `bcc`) | 15 | `recipient daily send limit reached` |
| Emails per agent per day | 5,000, raised by Ada on request | `client daily send limit reached` |
| `bcc` | up to 5 addresses | `invalid bcc recipient` |
| Subject / body | 255 / 20,000 characters | `field too long` |
| No Email channel | - | `email channel not configured` |

An address on the customer's own domain is used only after its DNS records
are verified. Until then mail goes out from the channel's Ada address.

## Test it

- A test run from the code editor fails with a name error, because
  `send_email` needs a live conversation. Test it in a conversation.
- A test run that blocks the tool's external calls skips the send and returns
  `sent: false` with `blocked in simulation`. No limit is used. Write the
  test case's expected outcome for that, or the failure branch looks like a bug.
- A tool set to send for real emails a real address. Use an inbox you own,
  never a customer's.
