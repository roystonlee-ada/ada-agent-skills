# Salesforce SMTP Connector (email)

Docs: `handoffs/salesforce/salesforce-smtp-connector.mdx`. Marked early access
and hidden in the docs, so confirm it is enabled for the agent before
promising it. Email only. The block is "Salesforce Email".

## Setup summary

- One Salesforce org per AI Agent. Other AI Agents must sit in the same
  region (up to 20, relayed through a primary).
- The conversation closes after 72 hours with no new email. Closing the Case
  does not end the handoff. Replies on a Case the AI did not create route to
  that Case for 14 days.
- Agents must reply from the Organization-Wide Address that matches the
  bring-your-own address.
- Seven setup steps: integration user, permission set, External Client App
  (Client Credentials, Run As), connect Ada with the My Domain URL, Case
  email setup (Email-to-Case, Case Feed, a verified email domain through a DNS
  TXT record, the Organization-Wide Address), Email Relay plus Email Domain
  Filter, and the Salesforce Email block.
- Ada credentials show once. A regenerated credential gives a five-minute
  grace period.
- A Salesforce sandbox adds `Sandbox:` to subjects.

## Symptoms

| Symptom | Likely layer | Check | Fix |
|---|---|---|---|
| Block falls back and no Case exists | Connection | The inbox toggle, the inbox's own domain, Salesforce availability and API limits | Turn on the toggle. Check Salesforce status and limits |
| Instance URL rejected | Connection | The URL used | Use the My Domain URL ending `.my.salesforce.com`, not the login, test or Lightning address |
| Credentials rejected on Save | Connection | Client Credentials Flow on the app and in OAuth Policies, Run As set | Fix both. A new app needs about five minutes |
| Integration user cannot create Cases | Connection | Permission set license, Case permissions, record type | Grant them |
| Other AI Agents error: wrong region, username or password | Connection | Region, username, password age | Regenerate the password and re-enter within five minutes. If Ada "could not check the password", wait and Save again |
| A Case field is missing in Ada | Field mapping | The integration user's Edit access to it | Grant access. The list refreshes in about five minutes |
| Transcript not in the Case feed | Payload | "Enable Case Feed Actions and Feed Items" | Turn it on |
| End user email is in Ada, not on the Case | Payload | Salesforce was down or over its API limit for about 15 minutes. Ada does not retry | Copy it to the Case by hand |
| No Email action on the Case | Field mapping | The page layout | Add the action to the layout |
| Agent cannot send | Return path | The AI Agent with the From address has an enabled inbox toggle | Enable one |
| End user gets no agent replies | Return path | Deliverability set to All email, domain verified, Email Domain Filter active | Fix each |
| Replies come from a Salesforce address | Routing | Domain and Organization-Wide Address verified, agent chose it as From | Verify, and have the agent select it |
| Agent's name not shown in Ada | Field mapping | The integration user can see user records | Grant visibility |
| Replies missing in a second AI Agent | Routing | It is in the primary's Other AI Agents list with a current password | Add it, refresh the password |
| Reply starts a new thread | Return path | The subject, with only `Re:` added. "Insert Thread ID" in Email-to-Case, or a sandbox, changes it | Keep the subject unchanged |

## Read and change

- Read: the email channel through adacli. The MCP lists channels only.
- Change: the connection in the dashboard (Config > CHANNELS > Email).
  Everything else is Salesforce-side.
