# Test cases that can fail for the right reason

A test run is only as good as its cases. In one week of Architect sessions,
a third of failed draft cases failed because the case was wrong, not the
playbook. Check each case before it is saved, and check the result before
you report it. Both author-playbook and revise-playbook use this page.

## 1. Write what the customer sees

The judge reads the conversation and the reasoning log, so a criterion must
name something it can find in one of them.

- Name the observable: a message the customer reads, or the step that ran
  ("the Route to Handoff step runs", "the customer is told a person will
  join"). "Starts a transfer" is too loose. Entering a playbook called "Live
  Agent Request" is not a transfer, and a judge will count it as one.
- One scenario, one outcome. If a case asks the agent to "ask for the route
  once" and also "not transfer", split it when the design allows a later
  transfer. Two criteria that cannot both hold fail every run.
- `good` and `fail` describe the same decision from both sides. Write `fail`
  as the nearest wrong behaviour, not as the opposite of everything.
- The customer's turns must let the agent reach the outcome. If `good` needs
  the agent to know a cabin class, a `then` turn has to supply it.

## 2. Mark each case target or control

- **Target:** a scenario the change should alter. It must fail on live today.
- **Control:** a scenario the change should leave alone. It should pass on
  live today. Take some from the nearest neighbours: cases that share the
  change's wording, playbook, trigger phrases or articles. A change most
  often breaks the conversations next to it.

Name controls with "(must not change)" so the person can see which is which.
A revision keeps its old cases as controls and adds new ones as targets.

## 3. Run live first, before you build

Run every case on live only: `ada-test <instance> --cases <ids>` with no
`--changeset`. This costs one call and tells you three things:

| Live result | What it means | What to do |
|---|---|---|
| Target fails | The case reproduces the problem | Keep it |
| Target passes | The case is wrong, or the problem is not what you think | Read the conversation, fix the case or the diagnosis before building |
| Control fails | A control is already broken or its wording is wrong | Fix the case, or take it out of the control set and say so |

If more than half the target cases already pass on live, stop. The change
would have nothing to fix. Tell the person and go back to the diagnosis.

## 4. Read the result before you report it

The same configuration gives a different verdict on borderline conversations
about half the time. One run is not proof either way. A case that swings
between runs is a sign its criterion is loose or wrong (section 7), not a
fact about the bot to accept.

- **Pin test first.** After staging, run the single plainest target case on
  the draft: `ada-test <instance> --cases <one id> --changeset <id> --no-live`.
  If it fails the way live did, the edit is not working. Run `ada-why` on it
  before you touch the config or run the rest.
- **Read the log for every failure.** `ada-why <instance> <conversation id>`
  shows which step decided the outcome. Quote the step setting that decided
  it: accepted values, re-asks, fallback value, stay-in-playbook, branch
  condition. If a step setting decided it, rule text in an instruction will
  not change the result. Change the setting or the branch.
- **Sort each failure before you report it:**

| Kind | Test | What to say |
|---|---|---|
| Got worse | Passed on live, fails on draft | The change did it. Look here first |
| Same on live | Fails on both | Not the change. Report it as its own item and do not edit the draft for it |
| Case wrong | The judge's reason contradicts the conversation, or the criterion cannot hold | Reword the case, name the old and new wording, rerun that case |
| Works in part | The draft fixes some turns, misses a branch, value, language or channel | Say which part is missing, then fix that part |
| Not reached | The conversation never got to the changed step | Check routing and exits with `ada-why` first |

- **Rerun a case once** on the draft when the judge's reason does not match
  the transcript. Change config only after the same failure shows twice.
- **Report counts by kind:** "targets fixed 4 of 6, controls worse 0 of 8,
  2 cases reworded". A bare "5 of 14 pass" hides which failures are yours.

## 5. Wording the judge reads literally

The judge applies the words of a criterion, not the intent behind them. In an
audit of a 44-case suite, 2 criteria shared by about 30 cases caused a quarter
of all failed checks, and by a hand read about half of those were the judge
misreading a fair bot reply. Write each criterion so a literal reader agrees
with you.

- **Define the unit.** "Asks at most one question" failed a bot that asked
  "from where to where?", because the judge counted two questions. Say what
  counts as one ("a route, from and to, is one detail") and what does not ("a
  closing 'anything else?' is not a question for this check").
- **Allow the first ask.** "Does not ask for what the customer already gave"
  failed the first, legitimate ask for a detail the customer had not stated.
  Write "never asks again for a detail the customer stated or said they do not
  know. The first ask for a missing detail is fine."
- **Write shared criteria once, carefully.** A check copied onto every case
  turns one misreading into dozens of failures, and it makes the whole suite
  look worse than the playbook is. Do not paste a design principle
  ("no re-asks", "one question a turn") into every case verbatim. Put it on
  the cases where it is at stake, and word it as a test.
- **Cut "may".** A judge grades an optional behaviour as required. Drop it,
  or write it as a condition: "if it asks, it asks once".
- **One criterion, one fact.** "Says A, but also B, because C" fails without
  saying which part broke. Split it. Two criteria that check the same fact
  pass and fail together, so one miss counts twice. Merge them.
- **Ask for the claim, not the exact reason.** Demanding a given phrase fails
  a correct answer worded differently. Write "says X, and gives the reason in
  its own words (the first flight that...)".
- **Check each target against the real source.** Run the tool or read the
  table before you write a figure, a total or a link into a criterion. A
  criterion that asks for "a total" fails when the source holds a per-piece
  rate, and one that asks for two links fails when one link already is both.
- **Agree with the playbook and with its sibling criteria.** If the playbook
  quotes both options and a criterion demands asking first, no run can pass.
  Where the design leaves a choice open, accept both behaviours until the
  owner decides.
- **Condition what the customer only gives when asked.** If a scenario holds
  back a detail, write "if the customer has given X, then...", so a bot that
  never asks is not failed for a comparison it could not make.

Before you trust a suite, check it:

1. Compare per-criterion pass rates on live and draft. A criterion that fails
   on both in every run is suspect. One that fails on many cases in the same
   way is wording.
2. Read the transcripts behind the failures of each shared criterion, not only
   the judge's reason.
3. Do not settle it with a second automated grader or a triage label alone.
   Both leaned the wrong way in this audit: one called almost every failure a
   real defect, the other called half of them met, including a bot that fell
   back to a topic menu three times. Use them to find what to read.
4. Report two counts: failures that are real defects, and failures from
   wording. Reword first, rerun, then judge the playbook.
5. Measure a wording fix by the failed checks on the criteria you edited, not
   by the number of runs that pass. In the audit, those criteria fell from 14
   to 4 failed checks of 22 on the draft, yet runs passing stayed at 58 of 88:
   a fresh run resamples the bot and the judge, and the remaining failures
   were scattered real defects. A forecast of the new pass count from the old
   runs was an upper bound and came out wrong.

## 6. Start at the greeting

A real customer meets the greeting first. Harnesses and simulated testers
often send the first message straight to the agent, so a case can pass there
and fail for a person. A button tap and a typed reply also route differently:
a typed "Show all my activity" read "show" as "show me how".

- Write each case from a real chat that starts at the greeting, and put the
  opening move on the case: the button to tap, or "type this at the greeting,
  do not tap first". "Start by saying X" alone leaves the tester guessing.
- Cover tap-then-type and type-at-the-greeting as separate cases for every
  open ask.
- Show the tester the full flow, greeting to last check.
- Record how the run reached the case. A harness run that skips the greeting
  is not a pass for the greeting path, and the page must not call it tested.

## 7. A fail at the end of a run is a finding

Never close a failure as noise, flaky or non-determinism. Sort it:

| Fail is | Evidence | Fix |
|---|---|---|
| The agent | Wrong, missing or dead-end reply, or no return to the task | Fix the playbook. The case stays failed |
| The rule | A correct reply fails it, or the same transcript grades differently on a re-grade | Reword the criterion (sections 1 and 5), rerun |
| A blind check | The judge cannot see a button, card or picture | Add a fixed check |
| The tester | The simulated member looped or skipped the question | Fix the script |

A case that swings between runs has a loose rule first ("if it swings so
much, chances are it's our test criteria", the owner, 04/11/2026). Allow
flexibility: no exact 1:1 reply, as long as the points are captured. A correct
answer without the return to the task is a failed check, not a pass by
comment. A case never counts as passed by default or because it was not run.
Report counts by kind, and take no rate such as "1 in 5" as acceptable without
the owner's yes.

## 8. Seed a case from a real conversation

A case drafted from a real conversation holds the real first message, the
variables, the tool results and the path the agent took. Use it for a bug (the
failed chat), a change set (chats that touch the changed step) and a playbook
migration (chats the old version handled). Draft one conversation per call.

The draft tool saves nothing. Take its `instructions` field as the procedure
for writing, previewing, saving and running the case, because the steps follow
the client's current field rules. The route files name the tool and command.
The sections above still decide whether the case is any good:

- **Agree the outcome with the person first.** The draft shows what the agent
  did, not what was right. For a failed chat, the criterion is what the customer
  should have got, in the person's words. Never copy the agent's behaviour into
  a criterion: the case would then pass on the bug.
- **Mark it.** A case from a failed chat is a target and must fail on live
  (section 3). A case from a chat that resolved well is a control.
- **Draft only.** Write every value from the draft. `get_conversation` and
  `conversations get` return the customer's own words, so use them to
  understand the chat and never to fill a field.
- **Read the preview for personal data.** Screening swaps names, emails, phone
  numbers and order numbers for fakes of the same shape and drops credentials,
  but it can miss a detail, and saving does not screen again. Replace what is
  left by hand.
- **Check the opening.** An empty `first_message` means the customer sent no
  text, often because they tapped a button. Ask for the opening move and record
  it as section 6 says.
- **Check variables marked as the customer's current value.** They can differ
  from the value during the chat. A variable that a mocked tool's lookup needs
  must stay out of the case, or the lookup is skipped.
- **Leave an empty variable out of the case.** A preset of `""` is not null,
  so every `is null` branch is skipped and the case tests a path no real chat
  takes.
- **Describe the external systems from the draft.** Each tool call the chat made
  becomes plain text: the records, their identifiers, the values returned and
  each error. A call the text does not describe fails the run with
  `simulation_not_covered`. That is a wrong case (section 4), so fix the
  `external_systems` text and leave the agent alone.
- **Set every tool the chat called to mock in simulations before the first run.**
  A tool set to live sends real requests. Code tools, MCP tools and HTTP Request
  blocks also run for real unless blocked, and a blocked call fails a case that
  needs it. Read `simulated_call_counts` on the first run. A live call means the
  tool is not mocked: stop and tell the person which one. `test-and-fix`
  `references/safe-to-run.md` holds the hold rule.
- **Search for a duplicate first.** If a saved case already tests the outcome,
  show it and ask before saving another.
