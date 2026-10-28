# Zendesk Support

Docs: `handoffs/zendesk/zendesk-support.mdx`. A one-time call that creates a
ticket. Email-style: the agent's reply goes to the customer as email, in the
same thread as the AI. Also covered in `channels/email/email-configuration/
email-handoffs/overview.mdx`.

## Setup summary

1. Connect the subdomain and enable Zendesk Support (OAuth).
2. Upload the Ada private app to Zendesk. It needs `ada_subdomain` and
   `ada_cluster`.
3. Add the Ada Configuration Token as an account under Channel integrations
   (Client Token field).
4. Create a Zendesk webhook (POST, JSON, bearer token) to the AI Agent's
   `end_handoff` endpoint, and a ticket trigger "Status changed to Solved" that
   sends the ticket id in the body.
5. Configure the block: Standby Message, Group, Subject, Zendesk Fields, Tags,
   Error Fallback.

Limits: agents must write Markdown. A plaintext fallback is required for
macros. Macro images arrive as attachments. Not available on Social channels.
No typing indicator. With the SMTP Connector, update the "Notify Requestor and
CC's of comment update" trigger to avoid duplicate emails.

The docs list no symptoms. Use these chain checks.

## Symptoms

| Symptom | Likely layer | Check | Fix |
|---|---|---|---|
| No ticket after the handoff | Connection | Integration connected and enabled, app installed in Zendesk, token account added | Redo the failed setup step above |
| Ticket created but the AI stays paused after Solved | Return path | The webhook exists, is active, uses the bearer token, and the trigger fires on Solved | Fix the webhook or trigger |
| Customer receives duplicate emails | Return path | The "Notify Requestor and CC's" trigger, when the SMTP Connector is on | Update the trigger as the docs describe |
| Agent reply arrives from a different address or thread | Return path | Zendesk default support address against the shared address | See `zendesk-smtp-connector.md` |
| Wrong group | Routing | Group id in the block against the Zendesk groups | Pick the right group. Use channel rules so Messaging serves chat and Support serves email |
| Fields or tags missing | Field mapping | Required Zendesk fields, tag values (not labels) | Fill every required field. Use tag values |
| Closed hours | Hours | Ada schedule and timezone, then Zendesk business hours | Add a Scheduled branch with the right message |

## Read and change

- Read and change: adacli has a Zendesk Support block helper, an OAuth
  connect step and an app download. They are newer than some installed
  versions, so check `--help` first. The MCP lists the handoff only.
- Webhook, trigger and app install are Zendesk-side.
