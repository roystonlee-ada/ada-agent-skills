# Gorgias

Docs: `handoffs/gorgias/`. Email-style ticket handoff. The Ada team deploys the
Gorgias Utilities app. Action integration id seen in live handoffs: `gorgias`,
with a Gorgias utility app.

## Setup summary

- A dedicated Admin API user (Settings > REST API: username, key, base
  subdomain).
- A Gorgias Rule that excludes tickets tagged `ada_handoff` from auto-merge.
  Without it, Gorgias can merge an Ada ticket into an existing open email
  ticket for the same user and break message delivery.
- Block "Handoff to a human agent". Required: `ada_conversation_id`,
  `ada_user_id`. Optional: `user_email`, `user_first_name` and
  `user_last_name` (used only for new customer records), `team_name` (must
  match an existing team), `subject` (defaults to "Conversation with" plus the
  email or User), `tags` (`ada_handoff` always added), `language`,
  `chat_summary`, `keep_agent_conversation_open`. Custom fields use
  `custom_field_<id>` keys, which the Ada team exposes.
- Meta variable: `agent_system_gorgias_conversation_id` (the ticket ID).
- Return: the agent marks the ticket Done. Gorgias API rate limits can delay
  relay and ticket creation.
- Utility actions: "Is in Business Hours" (returns `true` when no hours are
  configured) and "Get Median First Response Time" (7 days, value in seconds).

The docs list no troubleshooting section. Use these chain checks.

## Create-ticket action (observed on a real instance)

A second Gorgias action creates a ticket and does not open a live chat.
- Inputs seen: `customer_email`, `subject`, `chatter_transcript` and `tags`.
  `chatter_transcript` comes from a metadata action that runs first. Output: a
  ticket id.
- Common pattern: live chat in hours, ticket off hours, split by a Scheduled
  block.
- A ticket has no return path. Ada learns nothing when the agent replies or
  closes it. That is by design, so do not report it as a broken link.
- Checks:
  - The subject is not a fixed string. A static subject makes every ticket
    look the same in the queue.
  - The subject holds no customer name and no conversation id.
  - The customer message promises a timeframe. "Shortly" is a promise with no
    time. Name the real reply window.

## Symptoms

| Symptom | Likely layer | Check | Fix |
|---|---|---|---|
| Customer messages stop reaching the agent, or replies go missing | Return path | The auto-merge exclusion Rule for the `ada_handoff` tag | Add the Rule |
| Ticket not created | Connection | The API user credentials, rate limits, the utilities app deployed | Re-send credentials. Wait out rate limits. Ask the Ada team |
| Ticket in the wrong team | Routing | `team_name` matches an existing team exactly | Use the exact name |
| Name or email wrong on an existing customer | Field mapping | Names apply to new customer records only | Documented. Edit the customer in Gorgias |
| Custom field empty | Field mapping | The `custom_field_<id>` key and the id the Ada team exposed | Ask the Ada team for the id |
| Handoff says open when closed | Hours | "Is in Business Hours" returns `true` when no hours are configured | Configure hours in Gorgias, then branch on the result. Add an Ada schedule if wanted |
| Customer waits after the agent resolves | Return path | The ticket status is Done | Mark it Done |

## Read and change

- Read: the handoff action block through adacli. The integration is not in
  adacli's map, so use the dashboard. The MCP lists the handoff only.
- Change: the handoff through adacli. The Rule, API user and team names are
  Gorgias-side. Utilities app and custom field ids are the Ada team.
