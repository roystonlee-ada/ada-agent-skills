---
name: onboard-agent
description: >
  Walk a person through setting up a new Ada AI Agent, one stage at a time,
  starting from what the live agent already holds. Reads the agent, marks each
  stage (foundation, knowledge, handoff, actions and APIs, channels, custom
  metrics, testing, go-live) Done, Partial or Not started with evidence, asks
  only what the config cannot tell, and hands the next stage to the skill that
  owns it. Use it when someone says "set up my new Ada agent", "I just got an
  Ada instance, what now", "onboard this agent", "what is left before go-live",
  "where are we on setup", "new agent checklist", "which channels should I
  turn on", or "get this agent ready to launch", even if they never say
  "onboard". Not for one change to a live agent (use the skill for that
  change) or for diagnosing a conversation (use diagnose-conversation).
---

# Onboard a new Ada agent

A new agent needs about eight things in a sensible order, and people stall
because they cannot see which are done. The live agent already knows. So
read it first, grade each stage from evidence, and ask only what the
config cannot answer. That also makes the work resumable: the inventory is
the state, so never ask the person where they stopped.

This skill plans and routes. Each stage has a skill that does the work, and
this skill never copies its steps.

## 0. Pick the runtime

Each step below names what to do, not a command. Read one file for how:
- Ada MCP tools present (`get_ada_configuration`, `list_entities`) →
  `references/runtime-mcp.md`
- `adacli` on the path → `references/runtime-cli.md`
- Both present: use the MCP file for step 1, then the CLI file for every row
  the MCP marks Unknown (persona, languages, redactions, channel state,
  article total, handoff platform).
- Neither works: `setup-adacli` or `setup-ada-mcp` first.

## 1. Inventory the live agent (read only)

Read the evidence for all eight stages before you say anything. Open
`references/stages.md` for what proves each status, and the runtime file for
the call that reads it. Make no write in this step.

Grade each stage as Done, Partial, Not started or Not needed, with one line
of evidence (a count, a name, a date). If a route cannot read a stage, grade
it Unknown and name the dashboard page that shows it. Never guess.

Show the result as a short list, one line per stage:
`Knowledge: Partial. One source synced 22/10/2026, no article found for
returns or delivery.` Add the date range and the test-user basis for any
count.

Treat placeholder content as unfinished: sample tools, empty sources, a
company description that reads as behaviour rules. A default agent has a
chat channel, an email channel and a default handoff before anyone sets it
up, so their presence is not progress.

## 2. Ask what the config cannot tell

Ask one batch, only for gaps the inventory left. Offer options where you
can. A value the config holds (name, description, tone, languages, a
connected handoff platform) is not a question: state it in the stage table
and let the person correct it. Never ask "is this right?" about it.

Pick from this list only the items the config left empty:
- What the business does, in one sentence, and the brand tone.
- Which channels to launch, in order: web or app, email, voice, social.
- Which outside systems the agent must reach (orders, bookings, billing,
  CRM), and the two or three tasks customers ask for most.
- Which languages customers write in.
- Which support platform humans work in, and its hours.
- Where the help content lives: a public site, a help center platform, files
  or nowhere yet.

Glossary terms, redactions and wording come later, inside the stage that
needs them, not in this batch.

An answer that says "none" turns a stage into Not needed. Record it.

## 3. Pick the next stage and hand over

Take the earliest stage that is not Done or Not needed. Say which stage, why
it matters and what done looks like (from `references/stages.md`), then hand
it to its skill by name. Hand over one stage at a time.

| Stage | Hand to |
|---|---|
| Foundation | This skill, with a preview (below) |
| Knowledge | `help-center-to-kb-playbooks` for a help center. No help center: dashboard Config > AI AGENT > Knowledge |
| Handoff | `configure-handoff` |
| Actions, APIs, first use cases | `design-conversation`, then `author-playbook`. Tools: dashboard Config > AI AGENT > Tools |
| Channels | `references/channels.md`, then the dashboard step it names |
| Custom metrics | `ada-custom-metrics-setup` |
| Testing | `create-verification-skill`, then `test-and-fix` |
| Go-live review | `ada-promote-changeset` |
| Connection trouble | `setup-adacli` or `setup-ada-mcp` |
| A platform question or error | `troubleshoot` |

If the owning skill is not installed, say so and give the dashboard steps
from `references/stages.md`.

### Foundation edits

No other skill owns these, so this skill does them, in this order:
1. Draft each value from the person's answers. A company description is one
   clear sentence about what the business does. Behaviour rules go in custom
   instructions, not there.
2. Show the current value next to the proposed value for the company
   description, persona and each glossary term.
3. Ask the person to approve. Write only what they approve.
4. Write through the route in the runtime file, then read the value back and
   show it. These writes go live at once and use no changeset, which is why
   the preview comes first.
5. Where a route has no write (see the runtime file), give the person the
   exact text and the dashboard page.

Seed the glossary with brand names, product names and local words the model
would misread. Check redactions against what the business must keep out of
transcripts. Enable only the languages someone on the team can review.

### Channels

Take one channel at a time, in the person's launch order. Content comes
first: Knowledge, tools and a handoff should exist before a channel turns on.
For each channel, `references/channels.md` states what the route can do and
the dashboard step for the rest. Enabling a channel is live, so preview it
and get approval. After it is set up, run a test on that channel before
moving on.

## 4. Come back

Every time the person returns, or a stage skill finishes, run step 1 again.
Confirm the stage you just handed over reads Done from fresh evidence before
you announce it, and then move to the next stage. A stage that slipped back
(a tool broke, a handoff was switched off) is reported as Partial with the
evidence.

## Rules

- Make no write yourself except approved foundation edits. Every other write
  goes through its stage skill, lands on a changeset where one exists, and is
  previewed and approved first.
- Never promote. `ada-promote-changeset` owns that, and the person takes the
  step.
- Never claim go-live from the inventory alone. Go-live is the person's
  decision, so give them the evidence and the open risks.
- Report counts with their date range and say whether test chats are
  excluded.

## References

- `references/stages.md`: why each stage matters, what done looks like, what
  to prepare, what proves the status and who takes over. Open it in steps 1
  and 3.
- `references/channels.md`: per channel, what adacli and the MCP can do, the
  dashboard step for the rest and the limits. Open it for the channel stage.
- `references/runtime-mcp.md`, `references/runtime-cli.md`: the reads and
  writes for each route.
