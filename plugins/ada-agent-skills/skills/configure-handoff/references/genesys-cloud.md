# Genesys Cloud (chat)

Docs: `handoffs/genesys/`. Chat handoff through a Genesys Open Messaging
integration. Voice is in `voice-transfer.md`.

## Setup summary

- Needs a Genesys Cloud CX 1 Digital Add-on II, CX 2 Digital or CX 3 Digital
  license, the region key mapped to a domain, and an Inbound Message flow.
- Set the Open Messaging Threading Timeline to 0 minutes (Admin > Message >
  Threading Timeline). Otherwise a new handoff can merge into a previous
  conversation.
- An integration role with the long permission list in the docs (routing,
  messaging integration, architect flow, process automation).
- An OAuth client (Client Credentials, authorized roles, divisions). Note the
  Division ID if access is restricted.
- The Ada team installs the integration. It creates an Open Messaging
  integration named after the AI Agent.
- Then the customer associates that address with the Inbound Message flow at
  Admin > Orchestration > Routing > Message Routing. Without it, no handoff
  routes to a queue.
- Block "Handoff to a human agent". Required: `ada_conversation_id`,
  `ada_user_id`. Optional: `first_name`, `last_name`, `email_address`,
  `custom_attributes` (JSON), `transcript_summary`, `agent_name_override`.
  Use the "(legacy)" action only if the docs for your agent say so.
- Read custom attributes in Architect with Get Participant Data. Named fields
  take precedence.
- The agent resolves by wrapping up the conversation. Transfers between agents
  and queues keep the handoff.

## Symptoms

| Symptom | Likely layer | Check | Fix |
|---|---|---|---|
| Handoff arrives but no queue picks it up | Routing | The Open Messaging address is associated with the Inbound Message flow | Add the association in Message Routing |
| New handoff lands in an old conversation | Trigger | The Threading Timeline | Set to 0 minutes |
| Handoff fails at once | Connection | OAuth client, role permissions, division | Fix the missing permission or division |
| Custom data missing in the agent view | Field mapping | `custom_attributes` as JSON, read in Architect with Get Participant Data | Fix the JSON and the flow read |
| Customer waits after the agent leaves | Return path | The agent wrapped up the conversation | Wrap up in Genesys |
| Closed hours | Hours | Ada schedule and timezone, then the schedule in the Genesys routing flow. The docs give Ada no hours action for Genesys | Add a Scheduled branch in Ada. Fix the hours in Genesys |

## Read and change

- Read: the handoff action block through adacli. The integration is not in
  adacli's map, so use the dashboard. The MCP lists the handoff only.
- Change: the handoff through adacli. Role, OAuth client, flow and routing are
  Genesys-side. Install is the Ada team.
