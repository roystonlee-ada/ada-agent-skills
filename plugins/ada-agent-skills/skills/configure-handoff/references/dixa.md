# Dixa

Docs: `handoffs/dixa/`. Live chat and email handoff. Voice is in
`voice-transfer.md`.

## Setup summary

- Dixa must enable the Ada chatbot feature. Create a chatbot of type Ada at
  Settings > Chatbots (the token shows once). Add yourself to the default queue
  to test.
- Custom attributes (Text or Select, the technical identifier cannot change)
  and tags (must be predefined, names cannot change). Undefined tags are not
  applied.
- The Ada team adds the Dixa Utilities app. Connect it at Platform > Apps with
  the Dixa API key.
- Webhook at Platform > Webhooks to Ada's Dixa webhook (US or EU). It is
  required: without it, agent replies and conversation events do not return.
- Live chat action "Handoff to agent". Required: Ada conversation ID and user
  ID. Optional: Queue ID (default queue if empty), tags, user email (valid, and
  it cannot match an agent's email), names, phone, custom attributes (or a
  Custom Attributes List JSON). Existing contacts are not updated. No block may
  follow the Dixa Utilities block. A widget ID is no longer required.
- Email action "Create a ticket (conversation)". Required: User Email Address,
  Dixa support email, Subject, Message, Language.
- Limits: one Dixa handoff configuration per AI Agent. The customer cannot
  return until an agent claims and ends the conversation. Presence shows after
  the first message. Dixa business hours are not accessible in Ada. Queue
  position messages come from a Dixa automation.
- CSAT back to Dixa needs the wait-for-handoff setting (Ada team), the "Pause
  conversation here until handoff ends" and "Track as Handoff" checkboxes, the
  Human Agent Survey for chat, and two HTTP Request blocks (offer ratings, then
  submit, with matching rating type).
- Metavariables: `agent_system_dixa_user_id`, `_conversation_id`, `_agent_id`.

The docs list no troubleshooting table.

## Symptoms

| Symptom | Likely layer | Check | Fix |
|---|---|---|---|
| Conversation not transferred to Dixa | Connection | The Utilities app is connected with a valid API key, the chatbot of type Ada exists, the feature is enabled. A config change by the Ada team has fixed this before | Fix the failed item. Ask the Ada team |
| Agent replies do not reach the customer | Return path | The webhook exists and points at the right region | Add or fix it |
| Handoff fails or is rejected | Payload | User email is valid and is not an agent's email | Use a customer email |
| Goes to the default queue | Routing | Queue ID in the block | Set it |
| Tags not applied | Field mapping | The tags are predefined in Dixa | Define them |
| Existing contact not updated | Field mapping | Documented: existing contacts are not updated | Update in Dixa |
| Customer stuck after the agent finishes | Return path | The agent claimed and ended the conversation | End it |
| Closed hours | Hours | Ada schedule and timezone. Dixa hours are not readable from Ada | Keep hours in an Ada schedule. Branch on it |
| CSAT not recorded in Dixa | Return path | The two checkboxes, the Ada team setting, both HTTP blocks and matching rating type | Fix each |

## Read and change

- Read: the handoff action block through adacli. The integration is not in
  adacli's map, so use the dashboard. The MCP lists the handoff only.
- Change: the handoff through adacli. Chatbot, attributes, tags and webhook are
  Dixa-side. The Utilities app is the Ada team.
