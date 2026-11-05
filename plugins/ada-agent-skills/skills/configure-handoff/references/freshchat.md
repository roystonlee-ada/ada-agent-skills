# Freshchat

Docs: `handoffs/freshchat/`. Chat handoff. Needs an Ada relay app installed in
Freshchat.

## Setup summary

- Needs API access and custom app installation through the Developer Portal.
  Use the `<subdomain>.freshchat.com` address (not Freshdesk), and an API
  token. Note the channel (topic) names and locales exactly.
- The relay app is a `.zip` from the Ada team. Give it a signing secret of 32
  or more characters, publish it as a custom app, and install it with the Ada
  bot handle and the secret. Until it is installed, handoffs open
  conversations in Freshchat but nothing returns to Ada.
- Block "Handoff to a human agent". Required: `ada_conversation_id`,
  `ada_user_id`, `locale` (default `en-us`, must match the channel's locale),
  `channel_name` (exact, default "Chat with us"), `email_address` (lowercase).
  Optional: first and last name, phone, `chat_summary`, `agent_name_override`,
  `keep_agent_conversation_open`, `custom_user_attributes` and
  `custom_conversation_attributes` (flat string-to-string JSON, properties
  defined in Freshchat).
- The channel name is looked up and cached. OPEN: the docs text on cache
  duration and clearing was cut. Ask the Ada team before telling a customer
  that a renamed channel will be picked up.
- A second handoff opens a new conversation seeded with messages since the last
  handoff ended.
- Meta variables: `agent_system_freshchat_conversation_id`, `_user_id`,
  `_agent_id`.
- Utility actions: "Check business hours" (`group_name`, output
  `is_in_business_hours`) and "Get group average first response time" (seven
  days, `-1` if no data).

## Symptoms

| Symptom | Likely layer | Check | Fix |
|---|---|---|---|
| First handoff fails, no conversation | Routing | `locale` matches the channel's locale | Set the right locale. The docs call this the most common cause of a failed first handoff |
| Handoff goes to the wrong channel, or the channel is not found | Routing | `channel_name` is exact. Two channels with the same name use the first match | Rename channels to be unique. Use the exact name |
| Conversation opens, customer never hears back | Return path | The relay app is installed with the right secret and bot handle | Install or fix the app |
| Duplicate users in Freshchat | Field mapping | `email_address` case | Send lowercase |
| Custom attributes not visible | Field mapping | The properties exist in Freshchat | Create them, as flat string pairs |
| "Check business hours" fails with `400` | Hours | `group_name` exists and has business hours assigned | Correct the name. Assign hours to the group |
| After a rename or new channel, still fails | Connection | Cached channel lookup | Ask the Ada team to clear it |

## Read and change

- Read: the handoff action block through adacli. The integration is not in
  adacli's map, so use the dashboard. The MCP lists the handoff only.
- Change: the handoff through adacli. Channels, relay app and attributes are
  Freshchat-side. The `.zip` is from the Ada team.
