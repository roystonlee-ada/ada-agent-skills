# Gladly

Docs: `handoffs/gladly/`. Chat handoff through a Gladly custom channel. The
Ada team deploys the connector. One AI Agent maps to one custom channel.

## Setup summary

- Enable Custom Channels in Gladly.
- Create an API user with the API User role enabled for agents. Without it,
  agent replies do not reach the customer.
- Collect the Org ID and Org URL, and an API token (shown once). Give them to
  the Ada team.
- Create inboxes, then a custom channel (default inbox, optional Message
  Groups, channel ID from the URL). Add entry points with Exceptions that map
  each to an inbox.
- Add a webhook (region URL, header `X-Ada-Authorization`, events
  `CUSTOM_CHANNEL/MESSAGE_SENT` and `CONVERSATION/CLOSED`).
- Block: "Gladly", action "Handoff to Gladly agent". Required:
  `conversation_id`, `end_user_id`, `user_email`, `entrypoint_name`. Optional:
  `user_firstname`, `user_lastname`, `user_phone`, `group_id`, `group_name`,
  `gladly_note`, `gladly_topic_ids` (invalid ids ignored),
  `gladly_freeform_topic_<name>` (the topic must exist in Gladly).
- Meta variables: `agent_system_gladly_conversation_id` and
  `agent_system_gladly_agent_id`.
- Return: an agent resolves in Gladly, or the customer closes the Ada window.
  By default that closes the Gladly conversation. A Close Chat Message leaves
  it open and posts a note.
- Test in a separate handoff answer. It runs alongside existing integrations
  without downtime.

## Symptoms

| Symptom | Likely layer | Check | Fix |
|---|---|---|---|
| Agent replies never reach the customer | Connection | API User role enabled for agents on the API user | Enable it |
| Handoff creates nothing | Connection | Credentials with the Ada team, webhook present with both events and the header | Re-send credentials, fix the webhook |
| Block fails | Payload | The four required inputs | Fill them. `user_email` and `entrypoint_name` are the usual gaps |
| Lands in the wrong inbox | Routing | `entrypoint_name` against entry points and their Exceptions | Match the name, fix the mapping |
| Topics or notes missing | Field mapping | Topic ids valid, freeform topic exists | Use valid topics. Invalid ones are ignored |
| Custom attributes not visible in the dashboard | Field mapping | They land as an internal note and on the customer record | Look there. Documented |
| Two test chats merge into one Gladly conversation | Trigger | Same email reopens the same conversation | Use a different test email each time |
| Customer waits after the agent resolves | Return path | The conversation closed event, and the Close Chat Message setting | Fix the webhook or the setting |
| No presence message at start | What the customer sees | Presence shows only after the agent's first message | Documented |
| Closed hours | Hours | Ada schedule and timezone, then Gladly availability | Add a Scheduled branch |

## Read and change

- Read: the handoff action block through adacli. The integration is not in
  adacli's map, so use the dashboard. The MCP lists the handoff only.
- Change: the handoff through adacli. Connector, webhook and credentials are
  with the Ada team and in Gladly.
