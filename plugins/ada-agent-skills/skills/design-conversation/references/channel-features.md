# Channel features for design boards

Read this when you draft a board, for every channel in its `channels` list.
Each row is a feature that changes what a sample conversation should look
like, with the published docs.ada.cx page it comes from. Design to the row,
not to memory: a feature that is not in this table is not on the board.

Last checked against docs.ada.cx release notes: 07/11/2026.

## What each channel can show

| Feature | Web Chat and Messaging SDK | Social (WhatsApp, Messenger, Instagram, LINE, SMS) | Email | Source |
|---|---|---|---|---|
| ASK step shows accepted values as quick replies | Yes | Not listed yet. Show options as a plain list to type back | No buttons. Write the choices into the reply | [Ask steps can show accepted values as quick replies](https://docs.ada.cx/2026-08-11-playbooks-ask-quick-replies) |
| Hide keyboard input on an ASK with quick replies (the customer must tap) | Yes, off by default | No: the message box stays | No | [Release notes, 04/11/2026](https://docs.ada.cx/release-notes) |
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

- Quick replies: write `options` once. The board draws buttons on Web Chat and
  a numbered list on social channels, so one design serves both. A typed
  answer always has to work on every channel except Web Chat with hidden
  keyboard input.
- Hidden keyboard input: set `"hide_keyboard": true` on a bot turn only when
  every answer is one of its `options` and the board's channels are Web Chat
  or the Messaging SDK alone. Give the customer an option for "something
  else" or a person, since they cannot type.
- Customer writes first: on Email and social channels, and on Web Chat with a
  conversation start event, start every scenario with the customer's message.
  No greeting turn, and no "how can I help?". The first bot turn answers or
  asks for the first fact that message did not give.
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
   reaches a new channel, change that cell, and update `SOCIAL` in
   `scripts/board.py` if the board should now draw buttons there.
4. Update the "Last checked" date.

Add nothing that is not on a published docs.ada.cx page: an early-access
feature, a pull request or an announcement is not enough.
