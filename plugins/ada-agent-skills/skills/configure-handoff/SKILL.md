---
name: configure-handoff
description: >
  Set up and debug the connection between an Ada AI agent and the helpdesk
  that receives its handoffs: Zendesk, Salesforce, Gladly, Freshchat, Dixa,
  Gorgias, Amazon Connect, Genesys Cloud, NICE CXone, ServiceNow, Help Scout,
  Twilio Flex, email, voice transfer or a custom integration. Walks the chain
  from trigger to return path and stops at the first broken link. Use it for
  "the chat never reaches Zendesk", "handoff goes to the wrong queue",
  "transcript is missing", "fields are empty on the ticket", "agent replies
  don't come back", "customer stuck after the agent leaves", "set up the
  handoff to X", "connect Ada to our helpdesk", "off-hours message is wrong",
  or "handoff worked yesterday". Not for why the agent chose to hand off or
  how often (use review-handoffs). Not for one conversation that went wrong
  inside the agent (use diagnose-conversation). Not for dashboard or editor
  problems or Ada platform settings (use troubleshoot).
---

# Configure a handoff

A handoff has seven links between the customer's message and the person who
answers. Each link can fail on its own and each fails in its own way, so check
them in order. The first failed check names the owner of the fix. Fixing a
later link first wastes time, because it never gets traffic.

## 0. Pick the runtime

Each step below names what to do, not a command. Read one file for how:
- Ada MCP tools present (`list_entities`, `get_conversation`) →
  `references/runtime-mcp.md`
- `adacli` on the path → `references/runtime-cli.md`

If neither is present, send the person to `setup-adacli` or `setup-ada-mcp`.
Both runtimes can read a handoff. Only adacli can change one. The dashboard
step is Config > AI AGENT > Handoffs.

## 1. Name the platform and the symptom

Never assume the platform. Read the live handoffs and integrations, then open
the block each handoff uses. The block type names the platform. Ask the person
only for what the config cannot tell you: which handoff, which channel, and
what they saw. With the MCP only, the block tree cannot be read, so ask the
person for the platform and the block, or point them to the dashboard handoff
page (Config > AI AGENT > Handoffs).

Write the symptom as what the customer or the agent saw: "no ticket", "ticket
with no transcript", "customer stuck", "agent reply never arrived". Do not
write a cause yet.

Open only the file for the platform in use. One handoff can mix platforms,
for example a chat block and an email block behind a channel rule.

| Platform or block | Open |
|---|---|
| Zendesk Chat (live chat) | `references/zendesk-chat.md` |
| Zendesk Messaging (Sunshine, Agent Workspace) | `references/zendesk-messaging.md` |
| Zendesk Support (one-time ticket, shared email thread) | `references/zendesk-support.md` |
| Zendesk Ticketing (Create Ticket action) | `references/zendesk-ticketing.md` |
| Zendesk SMTP Connector (email replies) | `references/zendesk-smtp-connector.md` |
| Salesforce Messaging (MIAW) | `references/salesforce-messaging.md` |
| Salesforce Chat (and the Salesforce Action block) | `references/salesforce-chat.md` |
| Salesforce SMTP Connector (email, early access) | `references/salesforce-smtp-connector.md` |
| Gladly | `references/gladly.md` |
| Amazon Connect (chat) | `references/amazon-connect.md` |
| Genesys Cloud (chat) | `references/genesys-cloud.md` |
| ServiceNow | `references/servicenow.md` |
| Gorgias | `references/gorgias.md` |
| Freshchat | `references/freshchat.md` |
| Help Scout | `references/help-scout.md` |
| Twilio Flex | `references/twilio-flex.md` |
| Dixa | `references/dixa.md` |
| NICE CXone | `references/nice-cxone.md` |
| Email block, or email channel handoffs | `references/email.md` |
| Voice Transfer Call block | `references/voice-transfer.md` |
| Intercom, LivePerson, Kustomer, Talkdesk, or any API-based platform | `references/custom-handoff.md` |

## 2. Walk the chain

Check each link and stop at the first failure. Record the evidence for each
pass, so the person can see what you ruled out.

1. **Trigger.** The handoff must be active, allowed on the conversation's
   channel, and pass its availability rules. The docs allow five active
   handoffs. More than five is a risk to report (seen on a real instance
   above the cap). A handoff action block with Count as Handoff (`is_handoff`)
   off never counts in metrics. The agent picks a handoff by its name and
   description. If the handoff was never offered or chosen, that is
   `review-handoffs` or `diagnose-conversation` work, not this skill. Read the conversation's
   handoff attempt: it shows the target, the outcome and a reason code. If this
   handoff replaced an older one, check four things: the old handoff is still
   active, a playbook step or the error fallback still names the old one, the
   playbook change sits unpromoted on a changeset, or two descriptions compete
   for the same request. Disable the old handoff only after the new one works.
2. **Connection and credentials.** The integration must be connected, enabled
   and unexpired. Expired or deleted API clients, rotated tokens and a missing
   relay app or webhook are the most common cause of "worked yesterday".
3. **Field mapping and payload.** Inputs reach the platform only if the block
   fills them. Look for required inputs left empty, variable names that do not
   match what the platform expects, a tag or field entered by label instead of
   by key, and a transcript variable that was never fetched. Each variable an
   input names must exist in the variable list. Check that each JSON input is
   valid and has the shape the field expects (an object, not a string or a
   list).
4. **Routing and queue.** Check the department, group, queue, channel or skill
   the block names, and the routing rule on the platform side that turns the
   incoming item into work for a person.
5. **Business hours and availability.** Two layers decide this. Check Ada
   first: a Scheduled block in the handoff content branches on an Ada
   schedule, and the schedule has a timezone, day and time rules and holiday
   exceptions (Config > AI AGENT > Handoffs > Off hours > Schedules). A wrong
   timezone and a missing exception are common. The off-hours text must match
   the schedule, and the two branches of a Scheduled block must differ. Ada has
   no other hours setting. The CLI runtime file shows how to read the schedule.
   Then check the platform: operating hours, queue hours, agent status and
   capacity live there. Some platforms expose hours to Ada through a utility
   action. The platform file says which.
6. **What the customer sees.** The standby message (500 characters at most),
   the off-hours dialog, the error fallback and each block's fallback answer.
   An error fallback handoff runs when a handoff block fails. A customer who
   sees the wrong text is a wording or fallback problem, not a connection
   problem. A branch no option reaches is dead.
7. **Return path.** Ada must learn when the agent finishes. This needs the
   platform's close event, a webhook or relay app that reaches Ada, and a
   status the platform actually sets. Without it the customer waits, or Ada
   stays paused.

When a platform file lists no symptoms, run the chain above and the platform's
setup summary as the checklist.

If every link checks out and it still fails, it may be an Ada-side defect. Tell
the person to raise it with Ada support with the instance, the time, the
conversation ids and the checks already run. Say what stays broken meanwhile,
such as tickets not created or messages missing.

## 3. Fix on the right surface

Handoff blocks and integration credentials are not changeset entities. A
change applies to live conversations the moment it saves, in both runtimes. So
treat every write here as live:

1. Back up the current handoff or integration state to a file first.
2. Show the person the exact change, before and after.
3. Apply it only after the person says yes.
4. Read it back and confirm it saved.

Say which kind of change it is:
- **Handoff content or availability rules** (description, tags, rules,
  message tree). Live on save. A new handoff starts disabled, so build it
  disabled and enable it only after approval. The cap of five active handoffs
  applies when it is enabled.
- **Integration credentials and connection.** Live. Never write a secret into
  chat, a file in the repo or a note. Name the role ("the API token for the
  helpdesk") and have the person enter it in the dashboard or an environment
  variable.
- **Platform-side settings** (helpdesk triggers, routing, webhooks, roles).
  Not Ada. Give the person the exact setting and the owner on the platform
  side.
- **A playbook that routes to a handoff.** This is a changeset entity. Stage
  it, test it, and hand the promote step to `ada-promote-changeset`.

You never promote. If a step needs a dashboard action that neither runtime
offers, give the person the dashboard path.

## 4. Verify safely

Never open a real handoff to a live queue to test. A test ticket in a live
queue pages a person, and a live chat can be claimed by a real customer's
agent. Climb this ladder and stop at the lowest rung that answers the
question:

1. **Read-only checks.** Integration state, handoff config, platform
   settings, and the outcome of recent real handoff attempts. Most diagnosis
   ends here.
2. **Simulation.** Simulated conversations replace the handoff block with a
   mock, so no helpdesk is contacted. A simulation proves the trigger, the
   wording and the branch. It cannot prove the connection.
3. **A real test, with the person's go-ahead.** Pick the safest target in this
   order: a test queue or department in the helpdesk, a test user and test
   brand, then one test in a quiet hour with the queue owner told first.
   Agree who closes the test ticket afterwards.

The interactive chat and the dashboard Test handoff button run as a real
chatter, not a simulation. Treat both as ASSUMED unsafe: they may reach the
live helpdesk.

After any real test, read the conversation's handoff attempt and confirm each
link: arrived, routed, transcript and fields present, reply returned, closed.

## 5. Report

- Platform and handoff, with the channel.
- The first failed link, the evidence, and who owns the fix.
- Each link ruled out, in one line.
- The change you propose, marked live-only, with the backup you took.
- The test rung you used and what it proved. Mark anything unverified OPEN or
  ASSUMED.
- Next skill, if one applies: `review-handoffs`, `diagnose-conversation`,
  `revise-playbook`, `ada-promote-changeset`, `troubleshoot` (dashboard,
  editor or Ada platform settings).
