# The eight stages

Contents: how to read a status, then one section per stage (why it matters,
what done looks like, what to prepare, what proves the status, who takes
over). Open this file in step 1 to grade each stage, and again in step 3 for
the stage you hand over.

The order follows Ada's own docs: content first (persona, knowledge, tools),
then the channels that expose it, because a channel with no content answers
nothing. The docs give no single launch checklist, so this list is a working
order, not a gate.

## Status rules

- **Done**: every "done looks like" line holds and the evidence is in the
  inventory.
- **Partial**: some of it holds. Name the missing line.
- **Not started**: none of it holds.
- **Not needed**: the person said the stage does not apply (for example, no
  outside systems to connect). Record it and skip it.
- **Unknown**: this route cannot read the evidence. Name the dashboard page
  that shows it. Do not guess a status, and do not hold up other stages. A
  read that fails with FORBIDDEN or 403 "Feature not available" is Unknown,
  never Not started, because the read did not prove the thing is absent.

A stage is as good as its weakest line. Placeholder content does not count:
a company description that reads as behaviour rules, a tool whose name or
description says placeholder, stub or template, and a knowledge source with
no articles all grade as Partial at best. A company description of more than
one sentence, or a multi-point list, grades Partial: it holds rules or detail
that belong in custom instructions.

## 1. Foundation

Why: every reply draws on the company description, persona, languages and
glossary. A thin foundation makes every later stage look broken.

Done looks like:
- Company description present, one clear sentence about what the business
  does. Behaviour rules belong in custom instructions, not here.
- Agent name, company name, tone and message length chosen.
- Every language the business serves is enabled. English is always on and
  cannot be disabled.
- Redactions reviewed: the built-in rules that fit the business are on, and
  a custom rule covers any identifier the business must keep out of
  transcripts (docs: redactions apply to what end users type, not to
  contact details the agent quotes from Knowledge). A set with only the credit
  card rule on prompts a review question: ask which other identifiers
  customers type (email, phone, order or account numbers) and whether each
  should be redacted.
- Glossary seeded with brand names, product names and local vocabulary the
  base model would misread. On Voice, flag terms for voice detection.

Prepare: one sentence on the business, the agent's name, the brand tone,
the languages and the product or brand terms with their preferred wording.

Reads: company description text; persona (name, tone, message length);
enabled languages; built-in and custom redactions; glossary term count.
Persona, languages and redactions are not readable over the MCP.

Next: this skill, after a preview (step 3). Docs: `setup/persona/personality-setup`,
`setup/persona/best-practices`, `setup/languages/multilingual-support-setup`,
`setup/redactions/redaction-settings`, `knowledge/custom-glossary/overview`.

## 2. Knowledge

Why: Knowledge answers the factual questions, so it is the cheapest
containment. Procedures belong in playbooks, not here.

Done looks like:
- At least one source is connected or authored, and has synced.
- A search for the business's top questions (from the person's answer) finds
  an article for each.
- Re-sync is set for connected sources (daily, weekly or never), so articles
  do not go stale.

Prepare: the help center URL, an export or a connected platform (Zendesk
Guide, Salesforce Knowledge and others); the ten questions customers ask
most.

Reads: knowledge sources and last sync; whether title searches for the top
questions return articles; the article total (CLI only).

Next: `help-center-to-kb-playbooks` when a help center exists. Otherwise the
dashboard: Config > AI AGENT > Knowledge, then Add source or Create article.
Docs: `knowledge/content-ingestion/overview`, `web-import` (100KB per
article, 1,000 articles per web source, 50,000 per agent),
`knowledge-integration`.

## 3. Handoff

Why: the agent will meet cases it must not finish. A handoff that does not
reach a person is worse than none.

Done looks like:
- At least one handoff is active, and it routes to the platform the person
  named.
- That platform's integration is connected (Zendesk, Salesforce, Gorgias and
  others each need their own).
- A real or test conversation shows a completed handoff.
- Off-hours behaviour is decided. Ada holds off-hours schedules (Config > AI
  AGENT > Handoffs, Off hours tab, Schedules), and a handoff branches on one
  with a Scheduled block. Live chat platforms also keep their own hours, so
  the two must agree.

Docs allow five active handoffs at a time, one of which can be the
fallback for off-hours or errors.

Prepare: the support platform, the queue or group that should receive
conversations, support hours, and who owns the connection credentials.

Reads: handoffs and whether each is active; handoff integrations and their
state (CLI); conversations that escalated.

Next: `configure-handoff`. Dashboard: Config > AI AGENT > Handoffs, then the
Integrations tab. Docs: `handoffs/overview`,
`handoffs/handoff-management/overview`.

## 4. Actions, APIs and first use cases

Why: knowledge answers questions, tools finish tasks. This stage is where an
agent moves from deflection to resolution (a refund issued, a booking
changed), so aim for end-to-end, not a handoff with context.

Done looks like:
- Every system the person named has an enabled tool: a web action (API
  tool), a code tool or an MCP tool, with working authentication.
- At least one playbook uses those tools for a use case the person chose,
  with sample conversations the person approved.
- Tool calls succeed in tests (error rate low in the first week of traffic).

Not needed is valid when the person names no outside systems and wants
knowledge-only answers for now. Ask once, then record it.

Prepare: for each system, its API documentation, a test credential, and the
two or three tasks customers ask for. Docs warn there is no read-only key
type for Ada's own API, so give tools the narrowest access the outside
system offers.

Reads: tools by type and enabled state; MCP server connections and their
status; playbooks and whether they are enabled.

Next: `design-conversation` for each first use case, then
`author-playbook` for the approved design. Tool setup has no owning skill:
dashboard Config > AI AGENT > Tools (add a tool, Manage tokens for auth).
Docs: `automation/actions/overview`, `automation/code-tools/create-a-code-tool`,
`automation/mcp-tools/connect-a-server`.

## 5. Channels

Why: a channel is where customers meet the agent. Each has its own setup,
limits and launch control, so settle them one at a time.

Done looks like, per channel the person wants:
- Enabled, and installed or connected where the channel needs it (embed
  script, DNS records, phone number, social account).
- A test passed on that channel.
- For Email, launch controls set deliberately (docs default to the agent
  answering 100% of mail).
- Real, non-test conversations arrive on it.

Prepare: the list of channels in launch order, a developer for web or app
installs, DNS access for email, and licences for voice and social.

Reads: channels and their enabled state (CLI) or traffic by channel (MCP).

Next: `references/channels.md` for each channel's route and dashboard step.
Docs: `channels/overview`.

## 6. Custom metrics

Why: CSAT covers a small share of chats. A custom metric gives every ended
chat a verdict, so you can see which fixes move outcomes.

Done looks like:
- At least one active metric the business would act on, and a scorecard if
  the person wants one view.
- The metric has graded conversations (a pass rate exists).

Prepare: the two or three behaviours that matter (for example, never
promises a refund the policy does not allow), and who acts on a failing
verdict. A metric only grades chats that end after it is active, so set
this up before launch if the person wants a baseline.

Reads: custom metrics and their state; scorecards; a pass rate for a
recent window. If the read returns FORBIDDEN or 403 "Feature not available",
grade the stage Unknown and name Analytics > Metrics. The error text can say
adacli is out of date. That is misleading, so do not act on it.

Next: `ada-custom-metrics-setup`. Dashboard: Analytics > Metrics > New.
Docs: `optimization/performance/custom-metrics`.

## 7. Testing

Why: a test proves a use case once. Saved test cases prove it after every
later change.

Done looks like:
- Saved test cases cover each use case the person plans to launch, on the
  channels they plan to launch.
- The latest run of every case passed.
- The runs happened after the most recent promoted change.

Prepare: the scenarios the person is most afraid of, one per use case, and
the persona of the customer who would raise it.

Reads: saved test cases and their last run time; latest run result per case;
the daily run quota.

Next: `create-verification-skill` to define what "works" means for a use
case, then `test-and-fix` to run and repair. Dashboard: Simulations (add and
run cases) and the Test AI Agent button (a quick chat or voice check).
Docs limits: 1,000 test cases and 3,000 runs per day, up to 40 turns each,
chat, email and voice only. Docs: `optimization/testing/simulations/overview`,
`optimization/testing/interactive-testing`.

## 8. Go-live review

Why: this is the person's decision, so give them the evidence in one
place.

Done looks like:
- Stages 1 to 7 are Done or Not needed.
- No changeset the person meant to ship is still waiting in Testing.
- The person has approved launch scope: channels, traffic share, owner for
  the first week.
- Real conversations are arriving.

Prepare: a launch window, a rollback plan (a promoted changeset can be
reverted for 90 days), and who watches the first day.

Reads: changesets by status; non-test conversation volume; the other
stages' statuses.

Next: `ada-promote-changeset` for any pending changeset. After launch,
`review-handoffs` and `ada-custom-metrics-loop` keep improving the agent.
Docs: `optimization/change-sets`.

## Connection and platform questions

- No tool or command reaches the agent: `setup-adacli` or `setup-ada-mcp`.
- A question about how the platform behaves, or something that errors:
  `troubleshoot`.
