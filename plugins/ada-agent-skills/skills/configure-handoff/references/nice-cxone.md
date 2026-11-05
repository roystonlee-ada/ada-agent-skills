# NICE CXone

Docs: `handoffs/cxone/`. Chat handoff through a Bring Your Own Channel (BYOC)
integration. Voice is in `voice-transfer.md`. Only BYOC is supported.

## Setup summary

- Collect the Business Unit ID and Tenant ID. Register at the CXone developer
  portal for the Admin, Authentication, Real-Time and Digital Engagement APIs.
- Create the BYOC channel integration at ACD > Digital > Bring Your Own
  Channel. It has five URL fields on the cluster base URL (US, EU and Canada
  variants).
- Create the chat channel through the CXone Digital API, not the admin UI.
- Enable channel access for roles at Digital > Roles.
- Create a Studio workflow with a Reqagent action that sets the skill. Without
  it, escalated conversations are never routed.
- Create a close trigger at Digital > Automation Triggers (Case status changed
  to Resolved and Closed, Job URL ending `close-conversation`).
- Custom fields use the field Ident, not the label.
- In Ada: a webhook at Platform > Webhooks to Ada's CXone endpoint, subscribed
  to `v1.conversation.created`, `.ended`, `.handoff.ended` and `.message`. The
  Ada team installs the CXone Utilities app.
- Block "Handoff to agent". Required: Ada conversation ID, user ID, CXone
  Channel Id, User Email Address. Optional: contact attributes list, end user
  attributes list (comma-separated `key: value`), title, default agent
  display name, tags, names, "Don't close CXone conversation", "Fetch Zendesk
  attachments", avatar URL.
- "Check Skill Activity" returns Agents Available, Agents Working, Queue Count
  and Agents Logged in, summed over the skill IDs.
- Limits: one CXone instance per AI Agent, with several channels allowed.
  Presence shows after the first message. Closing in Ada starts a new
  conversation.

The docs list no symptoms. Use these chain checks.

## Symptoms

| Symptom | Likely layer | Check | Fix |
|---|---|---|---|
| Handoff errors with 500 responses from the webhook | Connection | Whether the failure began at a time that matches a platform event. A past case was an Ada engineering fix and handoffs failed during the window | Raise it with the Ada team and give the time window |
| Handoff arrives but is never routed | Routing | The Studio workflow has the Reqagent action with a skill | Add the action |
| Agent cannot see the channel | Connection | Role access at Digital > Roles | Enable it |
| Customer stuck after the agent resolves | Return path | The close trigger exists with the right Job URL and statuses | Create or fix it |
| Custom fields empty | Field mapping | The Ident, not the label | Use the Ident |
| Block fails | Payload | The four required inputs, a valid email | Fill them |
| Closed hours or no agents | Hours | "Check Skill Activity" counts, then any Ada schedule and timezone | Branch on Agents Available. Add a schedule for hours |
| Closing in Ada starts a new conversation | Return path | Documented behaviour | Expect a new conversation |

## Read and change

- Read: the handoff action block through adacli. The integration is not in
  adacli's map, so use the dashboard. The MCP lists the handoff only.
- Change: the handoff through adacli. BYOC, Studio, roles and triggers are
  CXone-side. Utilities app is the Ada team.
