# Salesforce Chat and the Salesforce Action block

Docs: `handoffs/salesforce/salesforce-chat/` (block, action block, user setup,
configuration) and `handoffs/salesforce/overview.mdx`. adacli integration name:
`salesforce-chat`. Synchronous live chat (Salesforce Live Agent). The Action
block is a separate, async API tool for cases and leads.

## Setup summary

Chat:
- In Salesforce: a chat deployment (host URL, deployment ID, organization ID),
  the My Domain URL, a connected app (consumer key and secret), OAuth
  policies ("All users may self-authorize", "Relax IP restrictions", "Refresh
  token valid until revoked"), routing and queues, and a chat button.
- In Ada: link the Salesforce account at Config > AI AGENT > Handoffs >
  Integrations, then Finish.
- The chat button ID picks the queue. The Off Hours dialog runs when no agent
  is online or the queue is full.
- The Create Contact and Create Case checkboxes match on name and email.
  Variables map to the default custom live chat transcript fields.
- The customer cannot end the agent chat. The transcript holds only what was
  said up to the transfer.

Action block (cases and leads):
- Config > AI AGENT > Handoffs > Integrations > Salesforce > Configure, with a
  username, password, security token and subdomain.
- The Salesforce user needs API Enabled, Case and Lead Read and Create, a
  default Case record type, field-level Edit and Read access, and a password
  that never expires.
- Actions: Create, Update, Delete and Lookup Case, Create and Update Lead,
  Search Contact by Email.

The docs list no symptoms. Use these chain checks.

## Symptoms

| Symptom | Likely layer | Check | Fix |
|---|---|---|---|
| Chat never reaches an agent | Connection | OAuth policies on the connected app, the link state in Ada, the deployment ID | Correct the policies or relink |
| Worked yesterday, fails today | Connection | The reason code on the conversation's handoff attempt first. Then the connected app's OAuth policies (self-authorize, relaxed IP, refresh token valid until revoked), consumer key and secret, the integration user's password and security token, that the integration user is still active (ASSUMED: a deactivated user breaks the link until it is reactivated and relinked), and a sandbox refresh | Fix what the reason code and the checks point to, then relink in Ada. Ask the Salesforce admin what changed since yesterday. A credential that expired or a policy that tightened is the usual answer |
| Off Hours dialog shows during staffed hours | Hours | Chat button ID, queue capacity, agents online on that button, then any Ada schedule | Fix the button or queue. Check the schedule timezone |
| Wrong queue | Routing | The chat button ID | Use the button for the right queue |
| Custom fields not filled on the chat | Field mapping | Each custom field is mapped one by one, and its Salesforce field exists | Configure each field in the mapping. Fields are set per custom field |
| Contact or Case not created, or duplicated | Field mapping | The two checkboxes, and name and email captured | Capture both. Fix the checkboxes |
| Sales handoff creates no lead | Payload | The Create Lead action inputs and the user's Lead permissions | Fix inputs and permissions. Some cases needed a config change by the Ada team |
| Action fails with an authentication error | Connection | Password expired, security token reset | Reset the token or password, then update Ada |
| Action cannot write a field | Field mapping | Field-level Edit access for the user | Grant it |
| Transcript stops early | What the customer sees | Documented: only up to the transfer | None |

## Read and change

- Read: the handoff block through adacli. `salesforce-chat` is a mapped
  integration name for reading its state. The MCP lists the handoff only.
- Change: the handoff through adacli. adacli cannot configure the Salesforce
  integration, so use the dashboard. Connected app, deployment, button and
  queues are Salesforce-side.
