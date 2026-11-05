---
name: create-verification-skill
description: >
  Generate a project-local verification skill (named verify- plus the subject) that defines
  what "this works" means for one Ada agent use case, code tool, config change
  or reported number, and a repeatable way to prove it. Use for "create a
  verification skill", "how do we verify X", "define done for this build",
  "make a check we can re-run", or when a new use case, code tool, knowledge
  or coaching change, or metric claim has no proof beyond a one-off test. Use
  it at the start of any new use case, before the playbook is written. Adapted
  from pstack's create-verification-skill.
---

# Create a verification skill

Define what "works" means as its own artifact, then script a repeatable check
for it. A one-off test proves one change once. A verification skill proves the
use case after every later change, and the next person can run it cold.

The generated skill is read mid-task by an assistant that has never seen this
agent. Write it for that reader.

## 0. Pick the runtime

Each step below names what to do, not a command. Read one file for how:
- Ada MCP tools present (`get_ada_configuration`, `get_test_cases`) →
  `references/runtime-mcp.md`
- `adacli` on the path, or you are inside Ada Architect →
  `references/runtime-cli.md`

## 1. Pick the subject

One subject per run, on one instance. Pick the row that fits.

| Subject | What the customer meets | The check drives it with |
|---|---|---|
| Agent use case (playbook, coaching, knowledge) | A conversation | Saved test cases run on live, then on a staged draft, then a backtest on past conversations |
| Code tool or action | A value inside a conversation | Sample inputs, including empty and edge ones, then one run inside a test case |
| Reported number | A figure someone quotes | A recompute from the platform, with the filter and time window stated |
| Page or file you hand over | A rendered document | Open it as the recipient would, use every link and button, recompute every number it quotes |

If the work spans several rows, pick the primary one. List the rest as separate
cases in the generated skill.

## 2. Interview the instance, not the person

Answer these from the configuration, the design, the ticket and the
conversations. Ask only what you cannot observe.

- **Done:** what outcome would the customer call a success? If no one wrote it
  down, mark it OPEN. Do not invent it.
- **Expected:** when a customer or reviewer will grade the case, quote their
  expected-result text and its source in each criterion. A criterion built from
  our own reading of a spec can pass while the grader's expectation fails. If
  the design deviates from their wording, log an assumption and show them the
  gap before the case reaches their grading page.
- **Stage:** where does the change live before customers see it? A changeset
  draft, never live. A change that cannot be staged cannot be verified here.
  An instance often holds several drafts. List them, read each one's diff, and
  pick the draft whose change touches what the case checks. A draft's name can
  disagree with its diff, so trust the diff. If none matches, or two do, say so
  and ask. Never create a draft just to have one.
- **Drive:** what runs the scenario? Name the real commands or tool calls from
  the runtime file. Do not guess a command shape.
- **Observe:** what evidence exists? Conversation links, reasoning logs, test
  verdicts, query output with its filters.
- **Isolate:** can a test touch real customers? A test must not start a real
  handoff, send a real message, or charge, cancel or delete anything. If the
  only path does, stop and say so.

If the baseline is broken (the draft will not stage, the test quota is spent,
the session is expired), fix it or report it exactly before you generate
anything. A skill written against a broken base teaches wrong steps.

## 3. Generate the skill

Write `verify-<subject>/SKILL.md` in your assistant's project skills folder
(`.claude/skills/` in Claude Code, `.agents/skills/` in Codex), unless the
person names another folder. Give it `name: verify-<subject>` and a
`description` that names the use case, the instance and when to use it.
Without frontmatter the skill never registers. Use these sections, each filled
from the interview, with no placeholders:

- **Stage:** the exact steps that put the change in a testable state, and how
  to tell it is ready. Ready means the draft exists and the test quota covers
  the run. If the draft already exists, the step is "confirm it", not "create
  it".
- **Doctor:** one read-only check that answers "is this worth testing?" Right
  instance, right draft id, session valid, and a test quota of at least twice
  the runs you plan. Run it first whenever anything looks off.
- **Drive:** the real commands or tool calls, with this use case's case ids and
  draft id.
- **Evidence:** what each proof captures. Set the standards:
  - Capture the customer's path, not an internal shortcut.
  - Link 2 to 3 conversations per finding, and mark each opened or ASSUMED.
  - Run each target case on live first. A case that already passes on live is
    a wrong case, so fix it before you trust a draft pass.
  - If the case fails on live and on the draft, report that. Either the draft
    does not fix the case or the case is wrong. Say which you think and why.
    Never turn it into a pass.
  - A pass on one run is weak. Repeat the cases that matter for a pass rate.
  - A test run is not a dry run. Read the run's list of action calls to see
    which ones reached real systems, and say so in the evidence.
- **Controls:** cases that must not change, named "(must not change)", taken
  from the nearest working use cases. They count toward the run budget. Run at
  least one when the budget allows, and say when it does not.
- **Cleanup:** remove drafts and test cases this run created and nobody asked
  to keep. Never remove the evidence, and never remove a draft or case that
  existed before the run. If the run created nothing, say so and delete
  nothing.
- **Report:** a table of case, live, draft and a one-line note, failures first.
  An unreachable case says what was attempted and what was missing. Never
  report a skipped case as verified some other way.

## 4. Seed the case map

Create `verify-<subject>/cases/README.md` and one file per behavior the
customer cares about. Start with the top 3 to 5, from the design and the known
failure modes. Follow `references/case-map-example.md`: an index, then one file
per case with four sections (`Sub-cases`, `How the customer reaches it`,
`Driving it`, `Gotchas`).

If a precondition is missing (no such order in the test data), the case reports
a failure and the reason goes in `Gotchas`. Never weaken a case to make it
pass.

## 5. Prove the generated skill before you hand it over

Run its own instructions once, end to end: stage, doctor, drive ONE mapped
case, capture evidence, clean up. Confirm the evidence still exists afterwards.
Fix what fails, and clean up after each failed attempt. A generated skill that
was never run is a draft. If you proved it in a stand-in, such as a sandbox
instance, list the steps the stand-in did that the real instance will not, and
mark them unverified.

Offer to re-run the map whenever the use case changes. Suggest a schedule only
if the person asks.
