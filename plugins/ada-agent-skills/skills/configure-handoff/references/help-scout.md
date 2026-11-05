# Help Scout

Docs: `handoffs/helpscout/`. Email-style conversation handoff. The Ada team
does the backend. A "Help Scout Utilities" app then appears in Config > Apps.

## Setup summary

- A dedicated mailbox, with Default Assignee "Person Replying" and Default
  Status Active.
- An OAuth2 app (App ID and Secret, shown once). The redirect URL is the AI
  Agent URL.
- A webhook to Ada's Help Scout callback (US and CA, or EU), with a signing
  secret of 32 or more characters. Subscribe to Conversation Agent Reply and
  Conversation Status Updated. Scope it to the mailbox and set it Active.
- Connect and Save the "Help Scout Utilities" app in Config > Apps.
- Block action "Handoff to a human agent". Do not use the "(legacy)" action.
  Required: `ada_conversation_id`, `ada_user_id`, `mailbox_id`, `subject`.
  Optional: `user_email` (highly recommended, otherwise an anonymous
  customer), `user_phone`, `user_first_name`, `user_last_name`, `tags`
  (unknown tags are skipped with no failure), `first_message`, `note`,
  `keep_agent_conversation_open`, `agent_name_override`. Custom fields need
  numeric field IDs added by the Ada team.
- Meta variables: `agent_system_helpscout_conversation_id`, `_customer_id`,
  `_agent_id`, `_agent_email`.
- Return: the handoff ends only when the conversation status is Closed.
  Pending, Active or Spam keep Ada paused, unless
  `keep_agent_conversation_open` is set. There is no Beacon. Presence shows
  only after the agent's first reply.

The docs list no symptoms. Use these chain checks.

## Symptoms

| Symptom | Likely layer | Check | Fix |
|---|---|---|---|
| Customer stuck, Ada stays paused | Return path | The conversation status is Closed, not Pending or Spam | Close it. Use `keep_agent_conversation_open` only on purpose |
| Agent replies never reach the customer | Return path | The webhook is Active, scoped to the mailbox, subscribed to both events, with the matching secret | Fix the webhook |
| Handoff does nothing | Connection | OAuth app credentials, Utilities app connected in Config > Apps | Reconnect. Ask the Ada team for the backend |
| Anonymous customer on the conversation | Field mapping | `user_email` is set | Pass it |
| Tags missing | Field mapping | Tags exist in Help Scout | Create them. Unknown tags skip silently |
| Custom field empty | Field mapping | Numeric field ID from the Ada team | Ask for the id |
| Wrong mailbox | Routing | `mailbox_id` | Use the dedicated mailbox |
| Closed hours | Hours | Ada schedule and timezone. The docs give no Help Scout hours action | Add a Scheduled branch. Say when a reply comes |

## Read and change

- Read: the handoff action block through adacli. The integration is not in
  adacli's map, so use the dashboard. The MCP lists the handoff only.
- Change: the handoff through adacli. Mailbox, OAuth app and webhook are
  Help Scout-side. Backend is the Ada team.
