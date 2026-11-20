---
name: author-playbook
description: >
  Build a V2 playbook from an approved design board, save the design's
  scenarios as test cases, stage it as a draft and run every case before
  reporting back. Use it as soon as the chat sends DESIGN-APPROVED, and
  whenever you are about to write or rewrite a playbook's steps. Covers when to
  use a code tool, how to word asks, channel choices, and the test run that
  ends every build. The ada-agent-toolkit skill holds the platform detail; this
  skill holds the method.
---

# Build the playbook from the design

The approved design is the spec. Build the simplest playbook that produces
those conversations, then prove it does. The person should never have to ask
"have you tested it?" or "can I see the conversation?".

## 0. Pick the runtime

Each step below names what to do, not a command. Read one file for how:
- Ada MCP tools present (`get_ada_configuration`, `get_test_cases`) →
  `references/runtime-mcp.md`
- `adacli` on the path, or you are inside Ada Architect →
  `references/runtime-cli.md`

No `/mnt/memory` folder means you are outside Ada Architect. Then the runtime
file says what replaces Approve, the changeset card and the chat blocks.

## Unattended mode

This applies when `/mnt/memory` is mounted and a scheduled loop started you, with
no person in the chat. The loop's first message and an ask ledger script in its
tools folder are the signs. Then:

- Never wait for a design board, `DESIGN-APPROVED`, an Approve button or a person.
  The approval is the ask's answer in the ledger: a row in stage `answered` with
  the chosen option. Build what that option says and nothing wider. If there is no
  such row, stop and record why.
- Do not run `design-conversation`. Take the scenarios from the ask's evidence and
  save them as test cases first, as in step 1.
- Stage the playbook as a draft and run every saved case. Record the build and the
  test run in the ledger as done, waived with a written reason, or not_testable_yet
  with a reason.
- Never promote, revert, delete or ramp. Promote is a guarded step the loop owns,
  and only after the ledger gate clears it. The loop's own rules beat this skill
  wherever they differ.
- Report in the loop's work folder, not in chat.

## 1. Save the scenarios as test cases, first

Before you write a step:
1. List the saved test cases and reuse any that covers the same scenario.
   Never write a duplicate.
2. For each approved scenario, save a case: the customer's first turn, the
   later customer turns, `good` (the scenario's `expect`) and `fail` (what
   would break it). Name each "<Use case>: <scenario>". Saved cases are the
   regression set for every later change, so they come before the playbook.
   Read `references/test-cases.md` before you write the wording, including
   section 5 on wording the judge reads literally. A case's
   `good` and `fail` name something the judge can find in the conversation,
   hold for one outcome, and the customer's turns let the agent reach it.
   Add two or more controls from the nearest existing use cases, named
   "(must not change)".
   For every open ask in the flow, add a case that enters through the menu
   button and answers the ask with free text. Use 3 paraphrases, including
   words that overlap a button label ("show", "yes", "ok"). A scripted tester
   types a clean opener, so only these cases reach the paths a human takes.
   Write criteria for the turn after the ask, and name the surface that must
   answer (playbook step or router, not a custom instruction).
3. Run every case on live only before you build. When a target passes, review
   the test and diagnosis before editing either. If more than half the targets
   already pass, stop and say so. Keep any known candidate failure open.
4. Record the use case so the next session reuses it: its key, the playbook
   names once they exist, and the case ids. Record it again when the
   playbook names are known.

## 2. Design the playbook from the whole conversation

If the channel is voice (phone), load voice-playbook-builder for the voice checklist, patterns and sim testing, and build from it.

Read `references/implementation-strategy.md` first. Read the playbook authoring guide for platform detail (the runtime file
says where it is). Then work from the design, not from the last comment:
- Read `references/playbook-graph.md`. Save the proposed flow graph, node and
  edge tables, and weak-node review before writing steps. Follow each ASK's
  retry and fallback through its downstream consumers and child returns.
- Map each bot turn to one step. One ASK collects one fact. When the board
  has a turn that lists several facts in one question (the person chose it),
  keep that wording in the first ASK and give each fact its own variable, so
  a later ASK is skipped when the reply already filled it. Never write a
  step that asks for facts the customer already gave.
- Write each step's instruction for the turn it produces, in a few lines. No
  rule lists. A step that needs "also include X, unless Y, but if Z" is a sign
  the logic belongs in a code tool or a branch.
- General instructions hold only what is true for every step: tone, scope
  and data limits. They go into every step's prompt, so a rule for one step
  goes in that step, and branching goes in IF_ELSE or a code tool. A reasoning
  SET instruction follows the same few-lines rule as ASK and SEND.
- No playbook text explains its own history: no "added because", fix or
  workaround notes, ticket ids or "SCOPING NOTE" blocks. The reasoner reads
  every word on every turn. The reason belongs in the changeset and the task.
  Run `scripts/check_playbook_text.py` on the draft before you stage and fix
  every FAIL in the text, not in the check.
- Choices: give an ASK `accepted_values` when the design shows `options`, and
  give every value a `quick_reply_labels` label of at most 20 characters, each
  one different. Buttons show on Web Chat and the Messaging SDK only. The docs
  say other channels are not supported yet, so the question must also work
  when the customer types the answer. Keep a status value such as
  `did_not_answer` out of the list unless a branch needs it, and label it when
  one does. Run `scripts/check_quick_replies.py` on the draft before you stage.
  Read `references/quick-replies.md` for the rules and the fixes.
- Reuse their existing actions. Never invent one. If the design needs data no
  action returns, say so plainly and stop.
- Branch with IF_ELSE on variables, two or three levels at most.
- Before you stage, read `references/build-pitfalls.md`. It lists the build
  mistakes that broke live playbooks (copying a variable, empty `else`
  branches, go-tos after an insert, `only_when_needed`, short-code matching)
  and the safe way to build each.

## 3. Choose the implementation

Read `references/implementation-strategy.md` before choosing steps or tools.
It is the shared strategy for author-playbook, revise-playbook and test-and-fix.
Record selected and rejected options, evidence and acceptance checks.

When the design emails the customer mid-chat, also read
`references/code-tool-email.md`.

When a code tool must check a sensitive variable (an ID, a date of birth, a
code), also read `references/code-tool-sensitive.md`.

## 4. Push back on patches

When asked for a change that adds a rule to a step to fix one case, look at
the whole flow first. If the case shows the question or the flow is wrong,
fix the design: change the board, get it approved, rebuild. Say why in one
sentence: "Adding 'also ask for the time' to the date question makes it ask
two things at once. I've made the time its own question instead."

## 5. Stage, test, report. Every time.

Refresh the graph from the persisted draft after staging. Link affected ASK
paths to cases and annotate exercised edges after authorized tests, following
`references/playbook-graph.md`. Report unresolved risks and untested edges.

1. Stage it as a draft linked to the approved design (its `work` key). A
   draft with no approved design is not allowed. It needs no diagnosis: the
   approved design is the reason for the change.
2. Check routing for every case's opening message against the draft. Fix
   routing before running full cases.
3. Pin test: run the plainest target case on the draft alone. If it fails the
   way live did, review the failure before making another edit. When the
   trace confirms a step setting decided the outcome, fix that setting. Rule text in an
   instruction does not override a saved value, a fallback, an
   accepted-values list or a stay-in-playbook setting.
4. Run every case on the draft and on live. Sort each failure with the table
   in `references/test-cases.md`: got worse, same on live, case wrong, works
   in part, not reached. Follow the
   [test failure review](../diagnose-conversation/references/test-failure-review.md)
   before changing the agent or a case. Show the results as the required last
   message: one row per case,
   with live, draft, a one-line note and a link to each conversation, plus
   counts by kind ("targets fixed 4 of 6, controls worse 0 of 8").
5. Compare the draft conversations with the approved board. Say plainly where
   a conversation differs from the design, even when the judge passed it.
   For a scenario that ends with a person, check the handoff's `reason_code`
   against why the design sends it there. Leave a handoff step's reason empty
   so Ada assigns one after save. Set `reason_code` and a one-line `reasoning`
   on the step only when the recorded reason is wrong, because Ada never
   overwrites a reason you set.
6. Only then say what the evidence supports. The person decides on Promote.

## Knowledge in a reasoning SET

For a reasoning SET that needs a fact from Knowledge, read
`references/knowledge-set.md` before authoring or revising it. This includes
extracting a policy value into a variable, not only writing a customer reply.
For code tool comparisons or restoring an earlier version, use
`troubleshoot` and its code tool version history runbook.
