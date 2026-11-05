# Twilio Flex

Docs: `handoffs/twilio-flex/`. Chat handoff into Flex through Studio and
TaskRouter. The Ada team deploys the connector and the block. Voice with
Twilio is in `voice-transfer.md`.

## Setup summary

- A Studio messaging flow that routes to Flex.
- A Conversations global webhook (Post-Event URL, with the `onMessageAdded`
  post-webhook) and a TaskRouter event callback (Task Completed only), both
  pointing at the Ada connector endpoint.
- Credentials: Account SID, Flow ID and Auth Token, plus an Ada API key per AI
  Agent and a webhook secret (Config > PLATFORM > API keys and Webhooks).
- Block fields: `conversation_id`, `end_user_id`.
- Meta variables: `agent_system_twilio_flex_conversation_id` and
  `agent_system_twilio_flex_agent_name`.
- Completing the task in Flex returns control to Ada.
- The agent must be set Available in the Flex desktop to receive a test.
- OPEN: the endpoint paths in the docs differ between pages (`twilio-flex`
  and `twilio`). Use exactly the value the Ada team gives for this agent.

The docs list no symptoms, and no hours guidance. Use these chain checks.

## Symptoms

| Symptom | Likely layer | Check | Fix |
|---|---|---|---|
| Handoff never reaches Flex | Connection | The Studio flow routes to Flex, credentials current, the webhooks point at the endpoint the Ada team gave | Fix the flow or the webhooks |
| Message arrives but the agent does not see it | Routing | The TaskRouter workflow and queue, and the agent is Available | Fix the workflow. Set the agent Available |
| Agent replies do not return | Return path | The Conversations global webhook and `onMessageAdded` | Fix the webhook |
| Customer stuck after the agent finishes | Return path | The task is Completed. The callback is for Task Completed only | Complete the task. Fix the callback |
| Closed hours | Hours | Ada schedule and timezone, then Flex and TaskRouter availability | Add a Scheduled branch in Ada |

## Read and change

- Read: the handoff action block through adacli. The integration is not in
  adacli's map, so use the dashboard. The MCP lists the handoff only.
- Change: the handoff through adacli. Studio, TaskRouter and webhooks are
  Twilio-side. Connector and block are the Ada team.
