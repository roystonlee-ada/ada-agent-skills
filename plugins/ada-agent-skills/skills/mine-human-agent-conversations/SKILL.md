---
name: mine-human-agent-conversations
description: >
  Mine the conversations that human agents closed after an Ada AI Agent handed
  off, to find what a playbook, article or action could take over, and write
  each find as a playbook candidate with its evidence. Use it for "what are our
  human agents handling that the agent could", "mine the live agent chats",
  "learn from what the humans say", "find playbook ideas in the handoffs or
  tickets", "which playbooks should we build next", "how do agents resolve X",
  or when someone shares a helpdesk export of agent replies. Each candidate
  carries a size, the path the humans follow, what to build and conversation
  links. For handoff counts by reason alone use review-handoffs. To rank every
  signal across the agent use improve-agent. To design a use case already
  chosen use design-conversation.
---

# Mine human-agent conversations for playbooks

A human agent's replies are the closest thing the customer has to a spec for
the agent. They show what the human asked for, which system they checked, which
rule decided the case, and what closed it. They also hold judgment calls that
should stay human. Read the replies as a spec, size every candidate from the
whole population, and keep the two kinds apart.

## 0. Pick the runtime

Each step below names what to do, not a command. Read one file for how:
- Ada MCP tools present (`get_conversations`, `get_conversation`) →
  `references/runtime-mcp.md`
- `adacli` on the path → `references/runtime-cli.md`

This skill only reads, so it works on a read-only instance. Saving test cases
at step 7 does not.

## 1. Scope the population

- One agent, one window: 28 days, never before 07/10/2026 (handoff reasons start
  that day). Exclude test users.
- The population is the handed-off conversations. Count them by topic or intent
  for the whole window. That count is the size of every candidate. A sample sizes
  nothing.
- If `improve-agent` or the person gave you clusters, use them and skip the
  topic split.

## 2. Check that the replies exist

Open one handed-off conversation for each handoff target before you size
anything. Ada stores a reply only when the handoff integration relays it, so a
ticket or case handoff can show none. `references/replies-source.md` says how to
check, what to do when there are none, and the helpdesk export to ask for.

Say in one line what the rest rests on: the transcript (N of M sampled handoffs
had replies), a helpdesk export, or nothing. Stop for any target with no
replies and no export.

## 3. Read the replies

For each of the largest clusters, read the human replies in at least 8
handed-off conversations (5 when `improve-agent` called you). Spread the sample
across at least two human agents and two weeks, because one person's habit is
not a rule. Fill the record in `references/playbook-candidates.md` for each
conversation. Keep facts and numbers, and leave out personal data.

## 4. Find the modal path

For each cluster, write the sequence of steps most of the humans followed:
what they asked, what they checked, what rule they applied, what they told the
customer, what closed it. Then say how many of the n followed it, and list the
variants and exceptions.

- The share that followed the path with no judgment call is the resolvable
  share. Report it as "k of n", never as a bare percentage.
- If the path differs by human agent, no rule exists yet. That is a policy
  question for the customer, not a playbook.

## 5. Place each cluster on a rung

| What the humans did | Rung | What to build |
|---|---|---|
| Told the customer a fact or a procedure | Answer | A knowledge article, or a playbook step when it is a procedure. Take the facts from the replies |
| Asked for the same details before anything else | Collect | A collection step before the handoff, so the person starts with the fields |
| Checked a record in a system and reported it | Look up | An action that reads the system. List its inputs and outputs |
| Applied a rule and changed something (refund, rebook, reset) | Resolve | A playbook with an action that writes. The policy owner confirms the rule and its limits |
| Used judgment, made an exception, or gave empathy or authority | Stay human | Nothing to automate. Improve the handoff summary and report it as the floor |

Recommend the highest rung the replies support. An article for a cluster where
the humans looked up a record and changed it fixes the question and leaves the
task with a person.

## 6. Check what already exists

Before you call a candidate new, check for the same task in knowledge, playbooks,
tools and coaching. List what you searched. If the agent already has a playbook
for it and still hands off, the candidate is a fix, so send it to
`diagnose-conversation`. If the tool already exists, the rung is cheaper than it
looks.

## 7. Write the candidates, then seed the tests

Write one card per candidate with the template in
`references/playbook-candidates.md`. Rank by conversations that could move:
cluster size times resolvable share, shown as a range with the arithmetic. A
card needs two or more conversation links you opened. A cluster without them is
a data gap: list its size and what is missing. Never fill the gap with what a
human "probably" said.

When the person picks candidates to build, name three conversations for each:
one on the modal path, one exception, one that must stay human. Draft them as
test cases with `author-playbook/references/test-cases.md` section 8. The draft
tool is the only route that screens personal data, so never paste a human's
reply into a case.

## 8. Hand off

Name the next skill and stop. This skill stages and saves nothing without a yes.
- `design-conversation`: a new playbook. Give it the card as the brief.
- `revise-playbook` or `diagnose-conversation`: the playbook exists and still
  hands off.
- A knowledge edit: an answer-rung candidate.
- `configure-handoff`: the handoff does not carry the fields the humans asked for.
- `improve-agent`: the person wants these candidates ranked against every other
  fix.

## Rules

- Redact names, contact details, order numbers and credentials from every quote
  and every report. Quote a rule or a number only when you need the exact words.
  Otherwise say what the human said in your own words.
- A rule a human applied is a hypothesis about policy. Mark it OPEN until its
  owner confirms, and never write it into a playbook as settled.
- Report what the route cannot show, and what would change if the data were
  there.
