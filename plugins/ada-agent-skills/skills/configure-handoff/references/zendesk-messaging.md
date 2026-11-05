# Zendesk Messaging

Docs: `handoffs/zendesk/zendesk-messaging.mdx`. Handoff block type:
`zendesk_agent_workspace_handoff`. Built on Sunshine Conversations and Zendesk
Agent Workspace.

## Setup summary

- Needs Sunshine Conversations (Web Messenger channel), Agent Workspace, and
  the Ada Sunshine channel integration. Moving from Zendesk Chat needs the
  Ada team.
- Connect at Config > AI AGENT > Handoffs > Integrations > Zendesk Messaging.
- Turn on multi-conversations in Zendesk Admin Center (Channels > Messaging
  and social > Messaging > Manage settings). Without it, customers cannot end
  a conversation cleanly during a handoff.
- Set Ada as the default AI agent for all channels in Zendesk (Admin Center >
  AI > AI agents > Marketplace bots > Manage marketplace bots). Setting it for
  one channel is not enough. Confirm the Default badge.
- A Zendesk trigger that sets the ticket to Solved returns the customer to
  Ada. The customer can also close with the X.
- Block fields: Standby Message, Department, Zendesk Fields (Requester,
  Follower, Assignee, CCs, Share, Status, Type, Priority, Tags), Tags (comma
  separated), and "Keep same Sunshine Conversation".
- A dropdown field needs the tag value, not the label.
- Capture variables `name` and `email` set the requester on the first
  escalation only.
- Identity: use the Ada identity token (recommended) or a Zendesk JWT. If
  authentication fails, the handoff goes on with an anonymous Sunshine user.
  Ada never matches a user from page input or a Capture block.
- Not compatible with Salesforce Chat or another live messaging handoff. It
  works alongside Zendesk Ticketing. With Zendesk Support, use channel
  availability rules: Messaging for chat, Support for email.
- Each escalation creates an "AI agent ticket" through the switchboard. Tickets
  and messaging both count toward monthly active users in Zendesk.

## Symptoms

| Symptom | Likely layer | Check | Fix |
|---|---|---|---|
| Handoff does nothing, no conversation in Zendesk | Connection | Sunshine Conversations configuration exists and the integration is connected and enabled | Complete the Sunshine configuration, then re-test |
| Authorisation error (401) when the department list loads | Connection | Credentials and the Zendesk side that issued them | Re-enter credentials. A 401 is a Zendesk outcome, so confirm the token and its owner in Zendesk |
| Messages reach the AI instead of the agent, or bypass it | Trigger | Ada is the default AI agent for all channels, not one | Set it for all channels in Zendesk |
| More than one Zendesk ticket for one conversation | Trigger | Whether a second handoff block, a repeated trigger or Zendesk Ticketing also ran | Remove the duplicate trigger, or gate it with a variable |
| Customer cannot end the conversation, or the helpdesk session stays open after the customer leaves | Return path | Multi-conversations setting, then the end-conversation trigger | Turn on multi-conversations. Add or fix the Solved trigger. Otherwise Ada engineering holds a known gap, so raise it with the Ada team |
| Customer returns to the AI too early or not at all | Return path | The Solved trigger, and "Keep same Sunshine Conversation" | Fix the trigger. Use the keep option only if the integration returns control |
| Customer sees the wrong agent name or picture, or the ticket shows the wrong customer | Identity | Two identities. The agent the customer sees is set on the Zendesk side (agent profile, brand and channel identity settings). Ada does not set it. ASSUMED: the exact setting, not in the docs. The customer on the ticket is the end user Ada matched by identity token or JWT, then verified email | Fix the agent display in Zendesk. For the customer, fix the token claims (`external_id`, verified email) |
| Requester or fields empty | Field mapping | `name` and `email` captured before the handoff, and the field values filled | Capture earlier. Use tag values for dropdowns |
| Wrong group or queue | Routing | Department in the block, then Zendesk routing rules | Pick the right department. Fix the Zendesk trigger |
| Agents offline, customer waits | Hours | Any Scheduled block and its schedule, then Zendesk agent status and business hours | Add a schedule branch with an email or message path when closed |

## Read and change

- Read: the handoff block, integration state and Zendesk groups through
  adacli. The MCP lists the handoff only.
- Change: the Messaging block and its department, standby message and tags
  through adacli. Credentials through adacli. The Zendesk settings above are
  Zendesk-side.
