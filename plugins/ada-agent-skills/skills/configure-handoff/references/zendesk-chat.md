# Zendesk Chat

Docs: `handoffs/zendesk/zendesk-chat/` (configuration, handoff setup, handoff
usage). Handoff block type: `zendesk_live_agent`. Synchronous: a live agent
answers in Zendesk Chat.

## Setup summary

- Needs the Zendesk Chat Enterprise plan, and a department or an Agent
  Workspace group to route to.
- Operating hours live in Zendesk (Settings > Account > Operating Hours).
- Create an API client in Zendesk. Its ID and secret go into Ada. The secret
  shows once. The redirect URL comes from Ada.
- Add the bot agent by signing in as a Zendesk Administrator or Owner.
- Capture variables must be named exactly `name`, `email` and `phone`, as
  lowercase global variables. Keep Email validation on `email`.
- "Automatic ticket creation" must be on in Zendesk, or no ticket is created.
- Zendesk Authentication is optional. On an authentication error the error
  fallback runs.
- Up to 10 subdomains can connect (Config > Apps > Zendesk). OPEN: the docs
  also state a 3-subdomain limit on the overview page. Confirm with the Ada
  team before promising more than three.

## Symptoms

| Symptom | Likely layer | Check | Fix |
|---|---|---|---|
| Chat ends at once with "Conversation ended" | Connection | The API client ID or secret expired or was deleted in Zendesk | Regenerate the client in Zendesk (Settings > Platform > Zendesk Live Chat) and re-enter it in Ada. If it still fails, allow the AI Agent URL in Zendesk |
| Department is visible but cannot be changed | Connection | Credentials stale | Refresh the credentials |
| Customer gets the off-hours dialog | Hours | Zendesk operating hours, then agent availability in the department, then any Ada schedule branch | Fix hours or staffing in Zendesk. The Off Hours dialog runs when no agent is online or hours are closed |
| Name, email or phone empty in Zendesk | Field mapping | Variable names are exactly `name`, `email`, `phone`. `email` kept Email validation | Rename or re-capture. A switch to Text validation can leave the wrong value |
| No ticket created | Field mapping | "Automatic ticket creation" in Zendesk | Turn it on in Zendesk |
| Customer dropped mid-chat | Return path | Mobile device sleep, private browsing, or leaving the page | The docs call mobile disconnects intended Zendesk behaviour. No Ada fix |
| Chat ends after 20 seconds to 2 minutes | Return path | Customer window out of focus, or 20 minutes idle | Documented limit. Tell the customer, or use Zendesk Messaging |
| Customer cannot end the agent chat | Return path | Documented limit | Agent ends it. Blocks after the Live Agent block then resume the AI |
| Chat triggers, agent surveys or ratings do not work | Trigger | Documented as unsupported | Use another mechanism, or Zendesk Messaging |
| File upload fails | Payload | Defaults allow JPEG, PNG, GIF, PDF and TXT, 20 MB, one at a time | Match the Zendesk file upload config |

Only one agent can join a conversation.

## Read and change

- Read: the handoff's block tree, the integration state and the Zendesk
  departments through adacli. The MCP lists the handoff and its active flag.
- Change: the handoff through adacli. Credentials through adacli or the
  dashboard. The API client, operating hours and ticket creation setting are
  Zendesk-side.
