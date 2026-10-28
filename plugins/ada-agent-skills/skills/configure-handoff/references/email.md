# Email handoffs

Docs: `handoffs/handoff-management/blocks/email-block.mdx` and
`channels/email/email-configuration/email-handoffs/` (overview, handoff
scenarios, attachment handling). Action integration id seen in live handoffs:
`email`. Covers the Email block and email-channel escalation to any platform.

## Setup summary

- The Email block sends one email. Required: Recipient, Reply-To, Subject,
  Content. Optional: BCC, CC, Content Type (`text/plain` or `text/html`),
  Reply-To Name, Sender Name. Set a Fallback Answer.
- The recipient must not be an address configured as a channel on this AI
  Agent, or the reply routes back to Ada.
- On an Email channel, compare the options:
  - Zendesk Support: same thread, same address.
  - Zendesk Ticketing: same thread only with the SMTP Connector.
  - Salesforce Case: new thread, agents reply from another address.
  - Email block: new thread. The platform may need email-to-ticket rules.
- Use system (purple) variables in the handoff blocks. Common ones: `email`,
  `name`, `first_name`, `last_name`, `ada_email_subject`, `email_attachments`.
  `email_attachments` must be mapped for Zendesk Ticketing, Salesforce and the
  Email block. Zendesk Support passes attachments itself.
- Build a dedicated email handoff gated by `channel = Email`. Turn on "Track as
  handoff" for reporting.
- If a ticket already exists from the Email API, updating it depends on the
  platform's API. Zendesk updates over HTTP do not share the thread. Replies to
  an updated Salesforce Case start a new thread.

## Symptoms

| Symptom | Likely layer | Check | Fix |
|---|---|---|---|
| Email handoff sends nothing | Payload | All four required fields set, recipient valid | Fill them. Edit the fallback answer so it says what happened |
| Agent reply comes back to Ada | Routing | Recipient is a configured channel address | Use an address that is not a channel on this AI Agent |
| Transcript or fields missing | Field mapping | Variables in Content, and a Fetch Chat Metadata block upstream for a transcript | Add them. The Email block takes up to three recent end user messages as a summary |
| Attachments missing | Payload | `email_attachments` mapped | Map it. Only Zendesk Support passes it by default |
| Customer's reply starts a new thread | Return path | Which block, and whether the SMTP Connector is on | Use Zendesk Support, or Ticketing with the connector |
| Ticket or lead not created from email | Field mapping | The platform's email-to-ticket rule | Add the rule on the platform side |
| Out of hours | Hours | Ada schedule and timezone | Add a Scheduled branch that says when a reply comes |

## Read and change

- Read: the handoff action block through adacli. The MCP lists the handoff and
  channels.
- Change: the block through adacli. Mailbox rules and addresses are
  platform-side. Domain and inbox toggles are in the dashboard (Config >
  CHANNELS > Email).
