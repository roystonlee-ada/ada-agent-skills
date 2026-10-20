---
name: design-conversation
description: >
  Design a new use case as sample conversations the person reviews and approves
  before anything is built. Use it whenever someone wants the agent to handle
  something new ("I want the agent to handle refunds", "can we automate name
  changes", "build a flow for X"), or when you notice that intent, even if they
  never say "playbook". Also use it inside revise-playbook when the goal of a
  use case changes. Produces an ADA-DESIGN block that the chat draws as a design
  board, revised in place until the person presses Approve. Do not use it for a
  one-line wording or routing fix to an existing playbook.
---

# Design the conversation first

The person owns what their customers should experience. You own how to get
there. So the first thing they review is the conversation itself, never a
written plan, a list of steps or a playbook. They read it as their customer
would, comment, and approve. Only then does anything get built
(author-playbook).

## 0. Pick the runtime

Each step below names what to do, not a command. Read one file for how:
- Ada MCP tools present (`get_ada_configuration`, `get_conversations`) →
  `references/runtime-mcp.md`
- `adacli` on the path, or you are inside Ada Architect →
  `references/runtime-cli.md`

No `/mnt/memory` folder means you are outside Ada Architect. Then the runtime
file says what replaces the board, Approve and the memory notes.

## 1. Learn just enough

Before you ask anything, read what already exists, in one batch. This is
read-only: change nothing while you learn.
- The playbooks, actions, code tools and knowledge that touch the topic.
  Check every kind of tool, because each lives in its own list.
- How often the topic comes up, and how it goes today (a few real
  transcripts). Use real counts.
- A record of a use case already designed for this agent. If one matches,
  this is a change: switch to revise-playbook.

Then ask only what you cannot work out, at most two questions, with choices:
the goal in the customer's words ("what should a customer who asks this get
back?"), and the one rule you cannot see in their setup (a cut-off, who
qualifies). Do not ask about steps, fields or settings. Do not interview.

When the person dictates the steps themselves, those steps are the spec.
Turn each one into customer turns. Where a step leaves something out (what
happens at a boundary, what the customer sees after a handoff, a wording the
person did not give), fill the gap with the sensible choice and say so in
`notes`: "You didn't say what happens at exactly 24 hours, so I put it with
'more than 24 hours'. Change it on the board if that's wrong." Never ask the
person to confirm, correct or complete their own steps. The board is how they
confirm.
Put each question in the choices block only. Repeating it in prose makes
the person answer the same thing twice.

## 2. Draft the board

Write 3 to 6 scenarios in one ADA-DESIGN block:
- `main`: the customer gives what is needed and gets the outcome.
- `edge`: the cases that really happen. A detail missing from the first line,
  a wrong or unreadable value, the record not found, the customer changing
  their mind, a request for a person. Pick the ones this use case meets, not
  a fixed list.
- `image` where a photo or screenshot helps (section 4).

Each scenario is a full conversation, written from the real config: the
greeting style, the action's real fields, the knowledge as it reads today.
Say in `expect` what a pass looks like in one line. That line becomes the
test case's "good".

Design rules. Each one prevents a failure you would otherwise patch later:
- One question per turn, one fact per question. If the person asks for
  several things to be collected in one message, push back in `notes` and say
  why: "Asking for the order number, email and photo at once makes replies
  hard to read and easy to get half right, so I kept them as three short
  questions." Then design it the better way. They can overrule you.
- Constrain the input before you handle bad input. Give choices as `options`
  when there are 2 to 5 fixed answers, or a format hint ("DD/MM/YYYY") for
  free text. Write `options` once, with labels of 20 characters or less:
  WhatsApp and Messenger cut longer button labels. A typed answer that names
  an option, or carries the detail itself (an email at "Use my email", a
  code at "Enter OTP"), picks that option, so buttons never block typing.
  Text-only channels, or social channels without rich buttons, get the
  options as a plain list to type back.
- Never ask what the customer already said, and never ask what an action can
  look up.
- Short messages: two or three lines. The answer itself, not only a link.
- Every route to a person says so plainly and carries what was collected.
  Its `expect` says why it goes to a person (policy, no tool for it, the
  customer asked), so the test can check the handoff reason.
- If the flow needs many branches to survive bad input, the question is
  wrong. Simplify the design and say so in `notes`.

```
<<<ADA-DESIGN>>>
{"work": "damaged-item-refund",
 "use_case": "damaged-item-refund",
 "title": "Damaged item refund",
 "goal": "A customer with a damaged delivery gets a refund or replacement in chat, without waiting for an agent.",
 "round": 1,
 "channels": ["Web chat", "Messenger"],
 "notes": ["I kept the order number and the photo as two questions, so each reply is easy to read."],
 "scenarios": [
   {"id": "main", "title": "Main path", "kind": "main",
    "expect": "Order found, photo read, refund offered in under five turns, no handoff",
    "turns": [{"who": "customer", "text": "My blender arrived cracked"},
              {"who": "bot", "text": "Sorry about that. What's your order number?"},
              {"who": "customer", "text": "48213"},
              {"who": "bot", "text": "Thanks. Could you send a photo of the damage?", "options": ["Send a photo", "I can't take one"]},
              {"who": "customer", "text": "", "image": "Photo of a blender jug with a crack along the base"},
              {"who": "bot", "text": "I can see a crack along the jug's base. Would you like a refund or a replacement?", "options": ["Refund", "Replacement"]}]},
   {"id": "no-order", "title": "Order not found", "kind": "edge",
    "expect": "Asks once more, then offers a person, never loops",
    "turns": [{"who": "customer", "text": "my order came damaged"}, {"who": "bot", "text": "Sorry about that. What's your order number?"}]}]}
<<<END-ADA-DESIGN>>>
```

Before you show the board, check it. A board that fails any line is not ready:
fix it first, and never show one with a known failure.
- 3 to 6 scenarios, each with `id`, `title`, `kind`, `expect` and `turns`.
- No bot turn asks more than one question.
- Every `options` list has 2 to 5 labels of 20 characters or less.
- Every route to a person says why in its scenario's `expect`.
- `work` and `title` are set, and the block is valid JSON.
The runtime file says how to run these checks where a tool does it for you.
A design that is never drawn as a board is not ready for review.

`work` keys the board. Keep it the same on every round. Keep the chat reply
to two lines: what the board shows and what you need from them.

## 3. Revise in place until Approve

Comments arrive as one message: notes on single turns and an overall note per
scenario. Send the whole board again with the same `work`, `round` plus one,
and `changed` on each scenario you changed, saying what changed in one line.
Answer a question in `notes`. Do not restate the board in chat.

If a comment would make the experience worse (three questions in one turn, an
answer the agent cannot know), say so in `notes`, show the version you
recommend, and let them choose. If two comments conflict, ask which wins.

Never build, stage or write anything before they press Approve. Reading is
fine; saving a test case, staging a change or editing a playbook is not. The
runtime file says how you learn that they approved. Then follow
author-playbook.

## 4. Photos and screenshots

Ada's AI agent reads an image a customer sends and writes an image
description: the visible text, what it shows, and quality problems (blur,
glare, cropping). Playbook steps can use that description. It is read on
Messaging and Email only (PNG, JPEG, GIF, HEIC, plus WebP on Messaging, up to
3 images per email). PDFs and video are not read, and sensitive documents can
be withheld by image redaction settings.

Suggest a photo path when the image carries facts that save typing or show
something words cannot, and something else checks them:
- an order or booking number read off a receipt or confirmation, then looked
  up by an action;
- damage on an item, reviewed by an agent before a refund over a limit;
- an error message on a screenshot, matched to the right help.

Push back when the design would trust the image as proof. The agent reads
what an image shows. It does not check whether it is genuine, edited or
AI-generated. An ID, a bank transfer slip, a medical note or a receipt that
alone unlocks money or account access needs the customer's usual
verification: an API check, or a person. Say this in `notes` in one sentence
and design the check in.

Always give a typed path too, for the customer who cannot send a photo, and
for channels that do not read images.
