# Where the human replies come from

Read this at step 2. It says how to check that replies exist, what to do when
they do not, and what to ask for.

Contents:
- Check each route before you rely on it
- When the transcript has no human replies
- The helpdesk export request
- The source line for the report

## Check each route before you rely on it

The runtime files say what each route returns. In short:
- Ada stores a human agent's message in the conversation when the handoff
  integration relays messages between the customer and the agent. The MCP shows
  it as a `live_agent_message` entry with the agent's name. adacli shows it as a
  message from the agent. Presence entries record when an agent joined and left.
- A handoff that only creates a ticket or a case, with the work done in the
  helpdesk and no reply sent back through Ada, leaves no human reply in the
  conversation. Open one handed-off conversation and look, rather than assume.

Read one handed-off conversation per integration first, before you size any
cluster.

## When the transcript has no human replies

Check in this order:
1. Another conversation in the same cluster, on a different channel or handoff
   target. Some targets relay replies and others do not.
2. Whether the integration can relay replies back. If it can, that is a setting
   to turn on, and `configure-handoff` owns it.
3. Ask the person for a helpdesk export.

## The helpdesk export request

Ask in plain words. Say what you need and why, and give the join key.

Ask for a ticket or chat export from their helpdesk for the same window,
covering the clusters in the report, with these fields:
- the Ada conversation id, or the handoff time and the customer's contact
  handle, so each row joins to a conversation
- the human agent's messages, in order, with timestamps
- the ticket's subject, category or tags, and its status
- the time it closed, and the resolution or macro the agent used

Ask for 50 to 100 rows per large cluster. Say that personal data should be
removed or masked first, and that you need no more than the text and the join
key.

## The source line for the report

State what the findings rest on, in one line:
- "Based on the transcript: human replies present for N of M sampled handoffs."
- "Based on the helpdesk export supplied on DD/MM/YYYY, N rows joined."
- "Missing: this route returns no human replies for these handoffs, and no
  export was supplied."

When the source is missing, say which candidates would change with it: usually
the information gaps and the fields to collect. Never fill the gap with what a
human agent "probably" said.
