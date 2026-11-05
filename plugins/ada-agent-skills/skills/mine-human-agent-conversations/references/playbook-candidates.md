# The record and the candidate card

Read the record at step 3 and the card at step 7.

Contents:
- The record, one per conversation
- The candidate card
- Sizing the card

## The record, one per conversation

Write these fields from the human replies. Leave a field blank rather than
guess it.

| Field | What to write |
|---|---|
| Customer ask | The task in plain words, from the customer's first message |
| Human asked for | Each identifier, photo, date or number the human requested, in order |
| Human checked | The record or system the human looked at, taken from the sentence where they report it ("I checked your booking and...") |
| Rule applied | The condition and the decision, in the human's own reasoning |
| Human told the customer | The facts and steps they gave |
| What closed it | A lookup result, an approval, a refund, a code, a link, or nothing |
| Time to close | From the first to the last human message |
| Judgment | Yes when the human weighed an exception, a tone or an authority. No when they followed a fixed rule |
| Human agent | The name or id, so you can check the path holds across people |

Replies rarely show the back-office lookup itself, so the sentence that reports
it is the evidence. A reply that only says "done" names no system: leave
"Human checked" blank.

## The candidate card

One card per candidate, in plain words:

- **Name:** the task, as the customer would say it.
- **Size:** conversations in the window and their share of all handoffs.
- **Resolvable share:** "k of n sampled followed the path with no judgment call".
- **Rung:** answer, collect, look up or resolve (SKILL.md step 5).
- **The path:** the modal sequence from step 4, in four to six lines.
- **What to build:** the article, the collection step, the action with its inputs
  and outputs, or the playbook. Say what the agent can do on day one if the
  action takes time to build.
- **Fields to collect:** the details the humans asked for first.
- **Policy to confirm:** each rule the humans applied, who owns it, and OPEN
  until they confirm.
- **Stays human:** the exceptions and judgment cases, with their count.
- **Already exists:** what you searched and found at step 6.
- **Evidence:** two or more conversation links you opened, shaped
  `https://<instance>.ada.support/insights/conversations/<id>`. Mark each opened
  or ASSUMED.
- **Next skill and test seeds:** the hand-off, plus the three conversations
  (modal path, exception, must stay human).

## Sizing the card

Conversations that could move = cluster size × resolvable share. Show a range,
because n is small: use the low and high ends of what the sample supports, and
write the arithmetic. Say "estimated", and never promise the lift. Overlapping
candidates share conversations, so their sizes do not add.
