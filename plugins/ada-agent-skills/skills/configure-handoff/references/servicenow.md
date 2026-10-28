# ServiceNow

Docs: `handoffs/servicenow/`. Immediate handoff through the ServiceNow Virtual
Agent API v4.1. The Ada team deploys the "ServiceNow Utilities" block and the
outbound webhook secret.

## Setup summary

- Needs ServiceNow admin access, the Virtual Agent plugin, and Integration Hub
  or the messaging plugins.
- Credentials for the Ada team: the instance hostname, OAuth Client ID and
  Secret, App Inbound ID and App Token.
- Block fields: `conversation_id`, `end_user_id`. Extra context variables pass
  through added inputs, with the key names agreed with the Ada team.
- Meta variables: `agent_system_servicenow_conversation_id` and
  `agent_system_servicenow_agent_id`.
- Test in a separate, non-live handoff answer. Ending the conversation in
  ServiceNow returns the customer to the AI.

The docs list no symptoms, and no business-hours or availability guidance.
Use these chain checks.

## Symptoms

| Symptom | Likely layer | Check | Fix |
|---|---|---|---|
| Handoff does nothing | Connection | Plugins installed, OAuth app values with the Ada team are current, the block is deployed | Re-send credentials. Ask the Ada team to confirm the block |
| Block fails | Payload | `conversation_id` and `end_user_id` present | Fill them |
| Context missing in the agent view | Field mapping | Added input keys match what the Ada team mapped | Align the keys |
| Wrong queue | Routing | Routing in Virtual Agent and ServiceNow, not in Ada | Fix in ServiceNow |
| Customer stuck after the agent ends | Return path | The conversation is ended in ServiceNow | End it there |
| Closed hours | Hours | Ada schedule and timezone. The docs give no ServiceNow hours action | Add a Scheduled branch in Ada. Check ServiceNow availability separately |

## Read and change

- Read: the handoff action block through adacli. The integration is not in
  adacli's map, so use the dashboard. The MCP lists the handoff only.
- Change: the handoff through adacli. Plugins, OAuth and routing are
  ServiceNow-side. Utilities block and secret are the Ada team.
