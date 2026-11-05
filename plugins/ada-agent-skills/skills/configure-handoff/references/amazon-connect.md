# Amazon Connect (chat)

Docs: `handoffs/amazon-connect/`. Chat handoff through Amazon Connect Chat.
Voice transfer is in `voice-transfer.md`.

## Setup summary

- A standard SNS topic in the same region as the Connect instance, with an
  access policy that lets the Connect service publish.
- An HTTPS subscription to Ada's webhook (US and CA share one URL, EU has its
  own). It stays "Pending confirmation" until the Ada team confirms it. The
  confirmation token lasts 72 hours. If it expires, delete and re-add the
  subscription.
- An IAM role (recommended): trust policy for the Ada role that matches the AI
  Agent's cluster, not the Connect region, plus a random External ID. Or an IAM
  user with access keys. Permissions include starting a chat contact, starting
  contact streaming, describing a queue, and reading effective hours of
  operation.
- Optional EventBridge rule for queued events into the SNS topic. It gives
  `agent_system_amazon-connect_queue_id` and `_queue_enqueued_at`.
- Chat duration 60 to 10,080 minutes (default 25 hours).
- Block "Handoff to a human agent". Required: `ada_conversation_id`,
  `ada_user_id`, `amazon_connect_contact_flow_id`. Optional: `first_name`,
  `last_name` (default display name "Anonymous"), `attributes` (JSON),
  `transcript_summary`.
- Each handoff creates a new Chat Contact. There is no persistent customer
  profile. Attachments up to 20 MB. The agent ends the contact, or the chat
  duration expires.
- Meta variables: `agent_system_amazon-connect_conversation_id` (the Contact
  ID) and `agent_system_amazon-connect_agent_id`.
- Utility action "Check queue hours of operation" takes `queue_id` and returns
  True or False. It accounts for timezone, overrides and holidays.

## Symptoms

| Symptom | Likely layer | Check | Fix |
|---|---|---|---|
| No contact appears in the agent workspace | Connection | The SNS subscription status is Confirmed | Ask the Ada team to confirm. Re-add it if the 72-hour token expired |
| Handoff fails right away | Connection | IAM role trust policy and External ID, permissions, region of the topic | Fix the role. The trust must name the AI Agent's cluster role |
| Block fails | Payload | `amazon_connect_contact_flow_id` is a valid contact flow id | Use the id of a flow that routes to a queue |
| Contact lands in the wrong queue | Routing | The contact flow that the id names | Fix the flow's queue |
| Customer routed when no agent is working | Hours | The "Check queue hours of operation" result for the queue, then any Ada schedule | Branch on the action's result. Check the queue's hours profile |
| Customer waits after the agent finishes | Return path | The contact ended, or chat duration | Agent ends the contact. Shorten the duration if needed |
| Attachment too large | Payload | The 20 MB limit | Ask for a smaller file |

## Read and change

- Read: the handoff action block through adacli. The integration is not in
  adacli's map, so use the dashboard. The MCP lists the handoff only.
- Change: the handoff through adacli. The SNS topic, subscription, IAM role and
  contact flow are AWS-side. Subscription confirmation is the Ada team.
