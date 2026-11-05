# Custom handoff and platforms without a native integration

Docs: `reference/conversations/custom-handoff-guide.mdx` and the Conversations
API getting-started guide in the same folder. The product docs list no native
integration for Intercom, LivePerson, Kustomer or Talkdesk. Use a custom
handoff, the Email block, or the HTTP Request block for them, and confirm with
the Ada team before promising anything native.

## Setup summary

- A custom integration receives Ada's events by webhook, relays messages
  between the customer and the platform, and hands control back through the
  Conversations API. Ada's demo repository for the Handoffs API shows the
  pattern.
- Create an API key (Config > PLATFORM > API keys).
- Create a webhook endpoint (Config > PLATFORM > Webhooks > Endpoints) on a
  public HTTPS address. Subscribe to `v1.conversation.message` and
  `v1.conversation.handoff.ended`. Use the endpoint's signing secret to verify
  every request.
- The endpoint can be scoped under Channels to the handoff integration
  identifier, or to one custom channel id.
- Process only events that follow a handoff, by checking the
  `handoff_integration` value in the event against the identifier in the
  handoff's start trigger.
- Handle `HTTP 429` with retry. Local development needs a tunnel, since Ada
  cannot reach `localhost`.
- Other routes: the Email block (see `email.md`), or the HTTP Request block to
  create a ticket in an unsupported platform. An HTTP ticket has no live return.
- For a platform with a native page, use that platform's file instead.

## Symptoms

The docs list no symptoms for custom handoffs. Use the chain checks.

| Symptom | Likely layer | Check | Fix |
|---|---|---|---|
| Platform never receives the handoff | Connection | The webhook endpoint is public HTTPS and active, subscribed to the two events, signature accepted | Fix the endpoint, events or secret |
| Receives events for every conversation | Trigger | The `handoff_integration` check, or the channel scope on the endpoint | Filter by the identifier or scope the endpoint |
| Messages relay one way only | Payload | The API key, and the call that sends the agent's message into the conversation | Check the key and the request |
| Customer stuck after the agent finishes | Return path | The integration ends the handoff through the API, and the `handoff.ended` event fires | Call the end-handoff request when the agent resolves |
| Rate limited | Connection | `429` responses | Retry with backoff |
| Platform not listed (Intercom and similar) | Trigger | Whether a native integration exists for the agent | Ask the Ada team. Otherwise build this route or use the Email block |
| Out of hours | Hours | Ada schedule and timezone, then the platform's own hours | Add a Scheduled branch |

## Read and change

- Read: the handoff and its trigger block through adacli. The MCP lists the
  handoff only.
- Change: the handoff through adacli. The API key and webhook are in the
  dashboard under Config > PLATFORM. The receiving service is yours.
