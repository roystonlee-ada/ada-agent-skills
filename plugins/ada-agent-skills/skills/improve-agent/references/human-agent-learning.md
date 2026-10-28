# Learning from the human agents

When a person closes a handed-off case, their replies show what the agent was
missing. This file says what to read, what to extract, and what to ask for when
the route does not return those replies.

Contents:
- Where the human messages come from
- What to extract
- When the transcript has no human messages
- The helpdesk export request
- What to write in the report

## Where the human messages come from

Check each route before relying on it. The runtime files say what each route
returns. In short:
- Ada stores a human agent's message in the conversation when the handoff
  integration relays messages between the customer and the agent. The MCP shows
  it as a `live_agent_message` entry with the agent's name. adacli shows it as a
  message from the agent. Presence entries record when an agent joined and left.
- A handoff that only creates a ticket or a case, with the work done in the
  helpdesk and no reply sent back through Ada, leaves no human message in the
  conversation. Open one handed-off conversation and look, rather than assume.

Read one handed-off conversation per integration first. Do this before sizing
any human-agent section.

## What to extract

For each cluster, read the human replies in at least five handed-off
conversations, then write down:
- what the human asked the customer for (identifiers, photos, dates, an order
  number): these are the fields the agent should collect before the handoff
- what the human told the customer: facts and steps that belong in an article
  or a playbook step
- what closed the case: a lookup result, an approval, a refund, a code, a link.
  Replies rarely show the back-office lookup itself, so read the sentence where
  the human reports it ("I checked your booking and...")
- how long it took: time from the agent joining to the last human message
- how often the human did no more than the agent could have: those conversations
  are the agent-resolvable share of the cluster

The humans' answers are the source for an article body and for the fields in a
collection step. Quote the facts they gave. Never invent them. Redact personal
data before the text goes in a draft or a report.

## When the transcript has no human messages

Check in this order:
1. Another conversation in the same cluster, on a different channel or handoff
   target. Some targets relay messages and others do not.
2. Whether the integration can relay replies back. If it can, that is a setting
   to turn on, and `configure-handoff` owns it.
3. Ask the person for a helpdesk export.

## The helpdesk export request

Ask for it in plain words. Say what you need and why, and give the join key.

Ask for: a ticket or chat export from their helpdesk for the same window,
covering the clusters in the report, with these fields:
- the Ada conversation id, or the handoff time and the customer's contact
  handle, so each row joins to a conversation
- the human agent's messages, in order, with timestamps
- the ticket's subject, category or tags, and its status
- the time it closed, and the resolution or macro the agent used

Ask for a sample of 50 to 100 rows per large cluster. Say that personal data
should be removed or masked first, and that you need no more than the text and
the join key.

## What to write in the report

State the source of the human-agent section in one line:
- "Based on the transcript: human replies present for N of M sampled handoffs."
- "Based on the helpdesk export supplied on DD/MM/YYYY, N rows joined."
- "Missing: this route returns no human replies for these handoffs, and no
  export was supplied."

When the section is missing, say which recommendations would change with it:
usually the information gap articles and the fields to collect. Never fill the
gap with what a human agent "probably" said.
