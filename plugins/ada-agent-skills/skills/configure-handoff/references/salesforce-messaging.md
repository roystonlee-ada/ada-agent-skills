# Salesforce Messaging (Messaging for In-App and Web)

Docs: `handoffs/salesforce/salesforce-messaging/` (five pages). Action
integration id seen in live handoffs: `salesforce2`, often with a Salesforce
Messaging utility app. Needs the Ada team to deploy the connector.

## Setup summary

- Salesforce side: Messaging for In-App and Web, Enhanced Omni-Channel
  Routing, a routing configuration, a queue with the Messaging Session
  object, an Omni-Channel Flow, a Messaging Channel that uses the flow,
  Messaging added to the Service Console, the Ada domain added to the CORS
  Allow List and Trusted URLs, and a Custom Client Deployment (pre-chat
  active, Display Frequency "Every Session"), activated and published.
- Give the Ada team the Organization ID, the Developer Name and the Instance
  URL from the Code Snippet.
- Customer side: a webhook (Platform > Webhooks) subscribed to
  `v1.conversation.created`, `.ended`, `.handoff.ended` and `.message`,
  pointing at the Ada connector URL for the AI Agent's cluster.
- Block: "Salesforce Messaging Utils" in the Handoff to Support answer.
  Required `conversation_id` and `end_user_id`. Pre-chat fields map by the
  Parameter API Name (the `id`), added by the Ada team. The docs say to place
  no block after it, because blocks after it are not shown after the handoff
  (`salesforce-messaging-handoff-setup`, step 5). Set a Fallback Answer.
  Observed on a live instance: standby messages and a CSAT survey sat after
  the pause action, and the chats still completed. OPEN: what happens to
  blocks after the utility block (shown, skipped or run late). Keep the doc
  rule when you build, and test one real chat before you call such a layout
  broken.
- Availability (optional): an External Client App (Client Credentials, Run As),
  an Autolaunched Flow using "Check Availability for Routing", and two Ada
  HTTP Request blocks (token endpoint, then flow endpoint).
- Queue position needs "Queue Wait Time and Position" on the Messaging
  Channel and a republished deployment. Salesforce supports queue position or
  estimated wait time per channel, not both. The banner shows only in
  Messaging and legacy Chat widgets.

The docs list no symptoms. Use these chain checks.

## Symptoms

| Symptom | Likely layer | Check | Fix |
|---|---|---|---|
| Handoff opens nothing in Salesforce | Connection | Deployment published and active, the Ada domain in CORS and Trusted URLs, Organization ID and Developer Name given to Ada | Fix the Salesforce setting, then ask the Ada team to confirm the connector |
| Worked yesterday, fails today | Connection | The reason code on the conversation's handoff attempt first. Then the deployment's published and active state, the Ada domain in CORS and Trusted URLs, the webhook and its four events, the External Client App credentials if availability checks are on, that the Salesforce user behind the connection is still active (ASSUMED: a deactivated user breaks it until reactivated and reconnected), and a sandbox refresh | Fix what the reason code and the checks point to. Ask the Salesforce admin what changed since yesterday, such as a republish, a rotated credential or a refresh. Ask the Ada team to confirm the connector |
| Bot works in a sandbox but breaks after a sandbox refresh | Connection | Sandbox refresh wipes the connector setup | Redo setup. Ask the Ada team to reconnect |
| Pre-chat fields empty | Field mapping | Parameter API Name against the id Ada holds | Ask the Ada team to add or correct the mapping |
| Wrong queue | Routing | Omni-Channel Flow, routing configuration, queue with the Messaging Session object | Fix the flow or queue |
| Agent replies do not reach the customer, or the chat never closes | Return path | The webhook exists with all four events | Add the webhook and events |
| Block fails and the fallback shows | Payload | `conversation_id` and `end_user_id` set, and any block after it (docs say none, live chats completed with some) | Fix the block |
| Customer waits with no agents | Hours | Ada schedule and timezone, then the availability flow result, then Omni-Channel presence | Fix the flow or add a schedule branch |
| No queue position shown | What the customer sees | Wait time and position setting, republished deployment, widget type | Turn it on and republish |

## Read and change

- Read: the handoff action block through adacli. The integration is not in
  adacli's map, so use the dashboard for its state. The MCP lists the handoff
  only.
- Change: the handoff through adacli. Webhook and deployment are
  Salesforce-side. Utility app and pre-chat fields need the Ada team.
