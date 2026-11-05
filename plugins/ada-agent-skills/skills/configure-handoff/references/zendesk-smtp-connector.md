# Zendesk SMTP Connector

Docs: `handoffs/zendesk/zendesk-SMTP-connector.mdx`. Lets Zendesk Ticketing
(and Zendesk Support) reply from the same support address in the same email
thread.

## Setup summary

- Scoped per bring-your-own-domain address. Configure at Config > CHANNELS >
  Email, one toggle per inbox. Both Inbound and Outbound need a green check.
- The Zendesk default support address must equal the shared bring-your-own
  address. If it does not, replies fail or appear from the wrong address.
- Keep forwarding on. Launch Controls can route traffic to Zendesk while you
  verify.
- Disable in this order: delete the address and domain in Zendesk first, then
  turn off the toggle. When every toggle is off, Ada rejects agent replies sent
  through the connector.
- Without the connector or the matching block, the AI Agent can reply in an
  escalated conversation.

The docs list no troubleshooting table. Use these chain checks.

## Symptoms

| Symptom | Likely layer | Check | Fix |
|---|---|---|---|
| Agent reply never reaches the customer | Return path | Toggle on for this inbox, Inbound and Outbound green | Fix the failing check |
| Reply comes from another address | Routing | Zendesk default support address against the shared address | Make them equal |
| Reply starts a new thread | Return path | Subject changed, or the ticket was made by a block that does not share threads | Use the Support block, or Ticketing with the connector |
| Agent replies while the AI also replies | Trigger | The Ticketing block pauses the AI, and the connector is on | Add the Ticketing block. Turn the connector on for this inbox |
| Duplicate emails to the customer | Return path | Zendesk "Notify Requestor and CC's" trigger | Update the trigger |
| Replies rejected after a clean-up | Connection | Every toggle off | Turn the toggle back on, then recreate the address and domain |

## Read and change

- Read: the email channel and its settings through adacli (`channels`). The
  MCP lists channels only.
- Change: the toggle and domain in the dashboard. Address and domain
  deletion and the default support address are Zendesk-side.
