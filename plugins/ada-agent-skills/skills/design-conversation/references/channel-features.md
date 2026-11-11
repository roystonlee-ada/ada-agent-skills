# Channel features for design boards

Read this when you draft a board, for every channel in its `channels` list.
Each row is a feature that changes what a sample conversation should look
like, with the published docs.ada.cx page it comes from. Design to the row,
not to memory: a feature that is not in this table is not on the board.

Last checked against docs.ada.cx release notes: 11/11/2026.

## What each channel can show

| Feature | Web Chat and Messaging SDK | Social and SMS (WhatsApp, Messenger, Instagram, LINE, Telegram, Viber, X, SMS) | Email | Source |
|---|---|---|---|---|
| ASK step shows accepted values as quick replies ("Map the answer using reasoning", one variable, 2 or more values) | Yes, in list order | Not supported yet. The agent asks the question and the customer types the answer | Not supported yet: same as social | [Step reference: quick replies for accepted values](https://docs.ada.cx/docs/automation/playbooks/step-reference#quick-replies-for-accepted-values) |
| Quick-reply limits | Up to 10 options. A value or label can be up to 256 characters | n/a | n/a | Same step reference |
| Hide keyboard input on an ASK with quick replies (the customer must tap) | Yes, off by default. The message box returns after a tap | No: the message box stays | No | [Step reference: Ask](https://docs.ada.cx/docs/automation/playbooks/step-reference#ask), [Release note](https://docs.ada.cx/2026-11-05-playbooks-ask-hide-keyboard-input) |
| Progress messages while a tool runs (a short line after 10 seconds, then every 20) | Yes, one AI Agent setting, off by default | No | No | [Step reference: progress messages](https://docs.ada.cx/docs/automation/playbooks/step-reference#progress-messages-while-a-tool-runs), [Release note](https://docs.ada.cx/2026-11-06-progress-messages-while-a-tool-runs) |
| Customer writes first, and the playbook reads that first message | Only when a conversation start event is set | Yes | Yes | [Conversation start events for Playbooks](https://docs.ada.cx/2026-08-04-conversation-start-events) |
| Greeting plays | Yes | Varies by channel | No | [Email onboarding](https://docs.ada.cx/docs/generative/deploy-ada-across-channels/email/get-started-with-email/) |
| Images in a SEND step (JPEG, PNG, GIF) | Yes | Messenger, WhatsApp, SMS | Yes | [Playbooks](https://docs.ada.cx/docs/automation/playbooks) |
| A reply can show an image an action put in a Media Variable | Yes | Where the channel renders images | Where the channel renders images | [Playbook and reply images can be driven by a Variable](https://docs.ada.cx/release-notes/2026/8/3) |
| Customer images read by the agent | Yes | Not listed | Yes, up to 3 per email | SKILL.md section 4 |

## Email details that change the design

- The playbook can branch on the address the customer wrote to
  (`email_recipient_address`), and read `ada_email_subject` and
  `email_has_attachments`. Never ask for what the subject line or an
  attachment already gives. Sources:
  [Bring Your Own Domain](https://docs.ada.cx/docs/channels/email/email-configuration/byo-domain),
  [Using Variables](https://docs.ada.cx/docs/automation/variables/using-variables).
- System mail from a sender on the Trusted senders list reaches the normal
  playbook flow instead of being treated as an auto-reply. If the use case
  starts from such mail (an order system, a form), say in `notes` that the
  sender must be on that list. Source:
  [Trusted senders for email](https://docs.ada.cx/2026-08-12-trusted-senders).

## What this means on the board

- Quick replies: write `options` once. Web Chat and the Messaging SDK draw
  them as buttons. Every other channel gets the question with a plain list
  of the values, with no numbers, and the customer types one back: a typed
  "1" matches nothing. The docs do not support quick replies on those
  channels yet. Keep labels at 20 characters or less so they read as short
  buttons (a design rule; the platform allows 256). A typed answer always
  has to work on every channel except Web Chat with hidden keyboard input.
- Hidden keyboard input: set `"hide_keyboard": true` on a bot turn only when
  every answer is one of its `options` and the board's channels are Web Chat
  or the Messaging SDK alone. Give the customer an option for "something
  else" or a person, since they cannot type.
- Customer writes first: on Email and social channels, and on Web Chat with a
  conversation start event, start every scenario with the customer's message.
  No greeting turn, and no "how can I help?". The first bot turn answers or
  asks for the first fact that message did not give.
- Slow tools: when a step calls an API or code tool that can take more than
  10 seconds, check whether progress messages are on. If they are, show one
  short progress line in that scenario, as a bot turn with
  `"progress": true`, so the reviewer sees the wait. If they
  are off, say in `notes` that the customer sees only the loading animation.
- Email: one bot turn is one email. Keep the one-question rule, but put the
  answer, what happens next and the question in that same email, because the
  customer may not reply for hours.

## Refresh this file

Run this when Ada ships a feature, or before a board for a channel you have
not designed for in a while:

1. Read [docs.ada.cx/release-notes](https://docs.ada.cx/release-notes) from
   the "Last checked" date above to today.
2. Keep only features that change what a customer sees or types in a
   conversation: a new button, card or input type; a channel that gains or
   loses a feature; a new start event; a new variable a step can read.
3. Add each as a table row or bullet with its docs.ada.cx link, and add or
   change the "What this means on the board" line it needs. When a feature
   reaches a new channel, change that cell, and update `BUTTONS` in
   `scripts/board.py` if the board should draw buttons or a list there.
4. Update the "Last checked" date.

Add only what is on a published docs.ada.cx page and is generally
available. Leave out anything the docs mark as Early Access, beta, preview,
limited availability or "contact your CSM to enable", and anything the docs
say is not supported yet. A pull request, an announcement or a feature you
saw working is not enough.
