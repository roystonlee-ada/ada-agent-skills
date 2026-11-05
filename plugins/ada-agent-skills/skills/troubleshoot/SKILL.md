---
name: troubleshoot
description: >
  Answer questions about how the Ada platform itself works and how to change
  its settings safely, for questions that are not about one conversation.
  Use it for "how do I change the sender address on our Ada email channel
  without downtime", "set up SSO for our Ada dashboard", "rotate our Ada API
  key", "who can use our Ada MCP server", "our Ada webhook stopped firing",
  "our Ada knowledge source will not sync", "which websites can embed our Ada
  chat", "export or delete end-user data in Ada", "find the Ada audit log",
  "which Ada region is this instance in", or "what can I stage on a changeset
  and what goes live at once". Every answer states the downtime risk and the
  rollback, and cites a doc or code source. Not for one conversation (use
  diagnose-conversation), handoff connections (use configure-handoff),
  promote or rollout (use ada-promote-changeset or ada-rollout-changeset), or
  general code, network or browser debugging, which has nothing to do with
  Ada.
---

# Troubleshoot the Ada platform

Platform settings sit outside the agent's content. Most of them (email,
team, SSO, API keys, webhooks) go live the moment someone saves them and no
changeset covers them. A wrong answer here can lock the team out or drop
customer email, so every answer carries its downtime risk, its rollback and
its source.

## 0. Pick the runtime

Each step below names what to do, not a command. Read one file for how:
- Ada MCP tools present (`list_entities`, `get_ada_configuration`) →
  `references/runtime-mcp.md`
- `adacli` on the path → `references/runtime-cli.md`

If both exist, use the MCP for reads. Open the CLI file when the question
needs team, API keys, snapshot or knowledge sources, which the MCP does not
cover.

## 1. Classify the question

Name the topic in one line, then check it is a platform question.

Route away when it is:
- One conversation, a wrong answer, a loop or an "internal error" →
  `diagnose-conversation`.
- A handoff connection or integration (Zendesk, Salesforce, email handoff
  recipient), or messages that reach the helpdesk but not Ada, or the reverse
  → `configure-handoff`. Ask which helpdesk and which direction.
- Taking a staged changeset live, or a sampled rollout →
  `ada-promote-changeset` or `ada-rollout-changeset`.
- Code, network or browser debugging with no Ada setting behind it → not this
  skill.

If the question needs an instance and none is named, ask which one. Never
guess an instance, and never read a customer name off a question into an
answer.

## 2. Find the source

Check in this order and stop at the first source that answers:

1. Product docs (docs.ada.cx). Read the page the runbook names, or search
   the docs for the topic.
2. Code, when the docs are silent or two pages disagree. Say so and cite the
   code path.
3. The runbook in the index below. A runbook is a worked answer built from
   sources, not a source itself. Check its "Source" line still holds.

Open only the matching runbook. Do not read the whole library.

| Topic | Runbook |
|---|---|
| Change the email channel's sender or support address | `references/runbooks/email-sender-address-change.md` |
| Bring your own email domain, DNS, extra inboxes | `references/runbooks/email-byo-domain.md` |
| Email spam, blocked and trusted senders, verification mail | `references/runbooks/email-spam-and-blocked-senders.md` |
| SSO setup and changes | `references/runbooks/sso.md` |
| Team members, roles, access, adding a user | `references/runbooks/team-roles-access.md` |
| Who can use the Ada MCP server, tool permissions | `references/runbooks/mcp-server-access.md` |
| Session timeout and session limits | `references/runbooks/session-timeout.md` |
| Rotate an API key | `references/runbooks/api-key-rotation.md` |
| Webhooks stop, add, rotate secret, replay | `references/runbooks/webhooks.md` |
| Knowledge source will not sync (integration or web import) | `references/runbooks/knowledge-sync-failures.md` |
| Embed script, allowed websites, widget will not load | `references/runbooks/embed-allowed-websites.md` |
| Data retention, deletion of end-user data | `references/runbooks/data-retention-deletion.md` |
| Export conversations or messages | `references/runbooks/data-export.md` |
| Audit log: who changed what | `references/runbooks/audit-log.md` |
| Find the instance and region | `references/runbooks/instance-and-region.md` |
| Changesets: what can be staged, revert | `references/runbooks/changesets-staging-revert.md` |
| Move a Zendesk token connection to OAuth | `references/runbooks/zendesk-token-to-oauth.md` |
| Playbook editor will not load or open | `references/runbooks/playbook-editor-wont-load.md` |

If no runbook matches, answer from the docs or code with the same answer
template and write "no runbook yet" in the answer. Do not borrow a nearby
runbook's steps.

Two topics are not in the docs. For a change of login email or for billing,
write "OPEN: not in the product docs" and tell the person to ask Ada
support. Do not guess a path.

## 3. Answer in one template

Use this shape for every answer, in this order:

- Preconditions: the role, access and facts the person needs before step 1.
- Steps: numbered, each one doing one thing, with the dashboard path or the
  runtime file's read.
- Downtime risk: "none expected" plus the reason when that applies, or the
  window and who it affects. Never leave it blank.
- How to verify: one observable result that proves the change worked.
- Rollback: the exact way back, or "no rollback: restore from the values
  recorded in step 1".
- Source: the doc path or code path for each claim that matters.
- OPEN or ASSUMED: one line for anything not verified. Mark an inference as
  ASSUMED. Mark a gap in the docs as OPEN.
- If the checks pass and it still fails: say it may be a platform defect, and
  tell the person to raise it with Ada support with the instance, the time,
  the ids and the checks already run. Say what stays broken until then. Many
  platform tickets end in an Ada-side fix, and no runbook step reaches it.

Run read-only checks first on the live instance where a route can read the
setting (the runtime file lists which). A live read beats the docs for what
is configured now. The docs still own what a setting does.

State a limit only if a source states it. The docs disagree in places (for
example, the EU domain form and whether API keys expire). Report both and
mark OPEN.

## 4. Changes need approval and a backup

The skill never makes a change on its own. Before any change:

1. Say whether the change can be staged on a changeset or is live-only.
2. Record the current values by hand (the runtime file says where to read
   them). A snapshot covers content config only, so it is not a backup for
   the settings in the table below.
3. Show the change and get the person's yes. Then make it, then verify.
4. Never promote. Hand a staged changeset to `ada-promote-changeset`.

| Where the setting lives | Staged on a changeset? | Backup before changing |
|---|---|---|
| Playbooks, knowledge articles, custom instructions, coaching, processes, actions, MCP tools and connections | Yes | The changeset itself, reverted from the Change sets page |
| Topics, intents, custom metrics, scorecards, glossary, variables, knowledge sources, test cases | No, live at once | Snapshot export, or note the old value |
| Channels and email, team and roles, SSO, session limits, API keys, webhooks, allowed websites, retention | No, live at once, dashboard or API only | Record the old values by hand |

A direct edit in the dashboard (Knowledge, Playbooks pages) does not appear
on the Change sets page. Do not tell the person to revert it from there.

## Reference files

- `references/runtime-mcp.md`: open for the MCP reads, the changeset tools
  and the list of what the MCP cannot reach.
- `references/runtime-cli.md`: open for the adacli reads and writes, the
  snapshot export and the list of what the CLI cannot reach.
- `references/runbooks/`: open the one matching file from the index above.
