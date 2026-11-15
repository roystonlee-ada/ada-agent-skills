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
  Read the target playbook's steps, routing and availability, including the
  playbooks it calls. Check every kind of tool, because each lives in its own list.
- The target instance and channel's start and end settings, greeting and
  supported languages. Read any assigned start or end playbooks. Check the
  actual greeting and ending in a matching transcript, including any survey,
  handoff or exit. Mark settings or behavior you cannot verify as OPEN and
  name the dashboard or transcript check that would settle it.
- The variables that can change the experience, such as language, market
  and country. Check where they come from, what values they carry and when
  they are available. Distinguish an inferred location from a confirmed
  country and a playbook-local value from one shared across the chat.
- The full text of each relevant help article and policy, including sources
  the customer shared, the playbook links to or recent chats used. Check the
  applicable market, language, dates, eligibility, exceptions and boundaries.
  Record each source and which outcomes it supports. Mark conflicting or
  missing rules OPEN and any proposed behavior ASSUMED.
- How often the topic comes up, and how it goes today (a few real
  transcripts). Use real counts.
- A record of a use case already designed for this agent. If one matches,
  this is a change: switch to revise-playbook.
- The agent's voice notes, if any: the reviewer's standing rules for wording,
  form of address, emoji and message length. Follow them in every board.

If the channel is voice (phone), load voice-playbook-builder for the voice design checklist and patterns before you draft the board.
For every other channel on the board, read `references/channel-features.md`.
It says what each channel can show (quick replies, hidden keyboard input,
images), who writes first, and what email adds, each with its docs.ada.cx
source. Design to it, not to memory.

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

Before drafting, map each distinct policy outcome and meaningful edge to a
scenario or a named alternate path. Check policy exceptions and exact
boundaries, missing or conflicting inputs, changes of mind, unavailable
tools, handoffs and repeat entry wherever they can change the outcome. Keep
the coverage map in the board notes. Give every relevant case a path or an
OPEN item that says what is needed to finish it. Group branches that share
an opening under one scenario.

Start each scenario at the real entry point. Show the configured greeting
on a fresh chat where it appears. On mid-chat or repeat entry, start with
the context the customer already has. Show each path through its final
visible outcome. Say in `expect` what a pass looks like in one line. That
line becomes the test case's "good".

Write dialogue and choices in the language the customer sees. Add English
translations for all non-English customer and agent turns, greetings,
choices and visible survey labels, unless the reviewer specifies a different
review language. Put the translation directly below the original as review
copy within the same turn. Keep the meaning, policy details and tone aligned.
See [board format](references/board-format.md) for a complete example.

Design rules. Each one prevents a failure you would otherwise patch later:
- One question mark per bot turn. By default ask one fact per turn. The
  person owns this choice: if they prefer to hear everything needed in one
  message, write one turn that lists every fact still missing, says in a few
  words what each is for, and ends in one question. A long run of single
  questions has no visible end, and a list gives the customer one. Either
  way, ask only for what the customer has not already said. If you disagree,
  say so once in `notes` and design what the person chose.
- Ask a follow-up only once the condition that makes it relevant is
  confirmed. If the customer's case type is unclear, ask which one first
  (as `options`), then ask the questions that type needs.
- If a side question is likely, show how the agent answers it and resumes
  the earlier issue at its next step. Read the whole conversation before
  returning so the bot keeps what it already learned.
- Answer from the article that matches the question. A fact from a
  neighbouring policy that sounds related (a refund window next to a
  reactivation) belongs in a different answer. Put the source in `expect`.
- Say sorry or show care once when the customer shows an inconvenience, and
  again on any later turn that adds more. Reword it each time. A repeated
  stock sentence reads as a script.
- Close at the point the use case calls for. For a complete informational
  answer with a planned exit, give the answer and exit directly. Reserve
  follow-up questions for a decision or fact the customer still needs.
  Show configured CSAT as a separate system event with its visible choices
  and the relevant submit, skip or unavailable outcomes. Distinguish a
  playbook exit, a handoff, and the end of the chat. Use the actual ordering
  and channel behavior where verified, and label proposed or unknown endings.
- When the playbook can be entered twice in one chat, show a repeat path.
  Vary the wording while keeping the same facts and policy. Reuse valid
  confirmed details, check anything that changed or may be stale, and avoid
  repeating actions or surveys unless the design and configuration call
  for them. A new chat follows its own entry rules.
- If market matters, prefer the customer's confirmed country for the
  relevant order or request. Use a verified region signal as a suggestion
  and let the customer confirm or correct it. List supported countries,
  with Other last when needed. Use a typed list or a follow-up when button
  limits prevent showing all supported choices. Show what happens for a
  missing, conflicting or unsupported country when it affects the outcome.
- When a system needs a field some customers do not have (an email, an ID),
  design the step for the customer who lacks it, and say what to enter
  instead.
- Constrain the input before you handle bad input. Give choices as `options`
  when there are 2 to 5 fixed answers, or a format hint ("DD/MM/YYYY") for
  free text. Write `options` once, with labels of 20 characters or less
  so they read as short buttons. A typed answer that names
  an option, or carries the detail itself (an email at "Use my email", a
  code at "Enter OTP"), picks that option, so buttons never block typing.
  Which channels draw buttons, which get a plain list to type back, and when
  you may hide typing are in `references/channel-features.md`.
- On a channel where the customer writes first (Email, social, or Web Chat
  with a conversation start event), start every scenario with the
  customer's message. No greeting turn. The first bot turn uses what that
  message, its subject line or its attachment already gave.
- Never ask what the customer already said, and never ask what an action can
  look up.
- Short messages: two or three lines. The answer itself, not only a link.
- Every route to a person says so plainly and carries what was collected.
  Its `expect` says why it goes to a person (policy, no tool for it, the
  customer asked), so the test can check the handoff reason.
- Offer a person only when the customer asks for one or the playbook cannot
  fix the problem. The agent being unable to do one task (cancel an order)
  is not a reason: tell the customer what they can do themselves first. If
  the business has no phone line, a customer asking "who can I call" wants
  the support channels, so list them from knowledge. A customer who only
  prefers a person goes through the pre-handoff triage flow, if one exists.
  A flow that ends in a form or link hands off to the form, not to a person.
- If the flow needs many branches to survive bad input, the question is
  wrong. Simplify the design and say so in `notes`.
- A code tool can email the customer mid-chat (a one-time code, a
  confirmation, a receipt) and report whether it sent. When the flow does,
  the same bot turn says so and names the address in part: "I've emailed a
  6-digit code to j***@example.com. What's the code?" Give it an `edge`
  scenario for "I didn't get it": check the address and spam folder, send once
  more, then offer the other route. A send that fails says so and moves to
  that route at once, so no turn ever claims an email that never left. Never
  show the code in chat. It needs the agent's Email channel set up; if the
  agent has none, say so in `notes`.

Before you show the board, check it. A board that fails any line is not ready:
fix it first, and never show one with a known failure.
- 3 to 6 scenarios, each with `id`, `title`, `kind`, `expect` and `turns`.
- Every policy outcome and material edge is mapped to a full path or an
  OPEN item. Each path shows the entry point and final visible outcome.
- Customer-facing copy and options have aligned review translations where
  needed. The survey and exit are shown with their verified behavior or
  clearly marked assumptions.
- No bot turn asks more than one question. A list of facts inside one
  question is allowed when the person chose it.
- Every `options` list has 2 to 5 labels of 20 characters or less.
- `hide_keyboard` is only on a turn with `options`, on a board whose channels
  all support it (`references/channel-features.md`).
- On Email and social channels, each scenario starts with the customer.
- Every route to a person says why in its scenario's `expect`.
- `work` and `title` are set, and the block is valid JSON.
The runtime file says how to run these checks where a tool does it for you.
Check the rendered board or the runtime’s readable transcript fallback.
Keep alternate endings and translations visible to the reviewer.

`work` keys the board. Keep it the same on every round. Keep the chat reply
to two lines: what the board shows and what you need from them.

## 3. Revise in place until Approve

A reviewer's correction to wording, tone, form of address or message length
holds for every scenario on every board for that agent. Apply it everywhere,
record it once in the agent's voice notes (read them in section 1), and say
so in `notes`. Their answers to "things only we know" go in the same record.

Comments arrive as one message: notes on single turns and an overall note per
scenario. Outside Ada Architect the person types them into the board's comment
fields and pastes what its Copy button gives. Send the whole board again with the same `work`, `round` plus one,
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
