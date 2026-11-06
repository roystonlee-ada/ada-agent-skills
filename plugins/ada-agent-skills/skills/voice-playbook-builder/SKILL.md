---
name: voice-playbook-builder
description: >
  Guide an Ada builder through designing, building, testing and shipping a V2
  playbook for the VOICE channel (phone), to Ada's voice best practices. Use
  when someone wants to build a voice playbook for a customer, design a phone
  flow (cancellations, order status), review a voice playbook before it goes
  live, fix a voice agent that loops or keeps transferring, settle what to ask
  the customer before a voice build, test a voice playbook with sims before
  callers hear it, or move an IVR flow into an Ada voice playbook. Also use when
  someone asks why a playbook behaves differently on a call than in chat. For
  chat-only playbooks use author-playbook. Works over adacli or the Ada MCP.
---

# Voice Playbook Builder

Based on Marc M.'s Voice Playbook Builder v1 (Ada, 06/11/2026).

Voice playbooks fail in ways chat playbooks don't. Silence sounds like a dropped call, callers can't scroll back, they wander
off mid-question, and the engine replays and rewinds flows in ways the JSON doesn't show. Most builders find these one at a
time, deep into a build. This skill carries that knowledge so you can do the heavy lifting for the builder:
- ask the design questions;
- propose the flow;
- stage it;
- write and run the tests;
- read the results.

The builder's job is the business decisions and calling in to hear it.

Drawn from live voice builds for subscription businesses (cancellations, authentication, email capture), Ada's Voice Build
Best Practices guide, and how the Playbooks V2 engine behaves on a call.

## 0. Pick the runtime

Each step below names what to do, not a command. Read one file for how:
- Ada MCP tools present (`get_ada_configuration`, `get_test_cases`) →
  `references/runtime-mcp.md`
- `adacli` on the path, or you are inside Ada Architect →
  `references/runtime-cli.md`

If neither is connected, use `setup-ada-mcp` or `setup-adacli` first. Where the
two routes differ, the runtime file says what each can and cannot do and gives
the dashboard step for the rest.

## Before you start

| Needed | How |
|---|---|
| A connection to the builder's agent | The Ada MCP server (`setup-ada-mcp`) or adacli (`setup-adacli`). Both read the live schema, stage changesets and run tests |
| A setup check | The runtime file has the check. It reports client behaviours that change how playbooks act, read from real calls |

Fix everything the setup check flags. Then read the live playbook schema and the improvement guide (the runtime file names
the calls). The live schema wins over anything written here.

## The workflow

### 1. Learn the channel, then design with the builder
Read `references/voice-best-practices.md` first, before you talk design with the builder. It is the voice channel's
nuances (greeting latency, auth levels, email capture, deviations, resume, API errors, SMS, containment), and it is what lets
you advise the builder on the experience instead of only taking notes. Then walk `references/voice-design-checklist.md` with
the builder, phase by phase, before any JSON. Settle:
- the business rules as a decision table;
- exact wording for anything legal or financial;
- how callers are identified and verified, agreed with the customer (checklist §3);
- what happens when each API fails, and what an unverified caller hears;
- the handoff;
- how callers will phrase the request.

**This step removes the trial and error.** The rebuilds in the reference builds each traced back to a checklist item found
mid-build.

Then read the closest build in `examples/` for its shape.

### 2. Set up the pieces
Follow `references/shipping.md` §1–2:
1. Find what already exists: variables, the auth child, the handoff, actions, and what the greeting sets.
2. Create the variables you need. They go live immediately, so prefix them.
3. Stage actions, tools and the playbook on a named changeset.

One changeset for everything, or several, both work.

### 3. Build the flow
Compose the sections from `references/patterns.md`. Each pattern is the fix for a checklist item. The first group goes in
every flow; use the second where the flow needs it, at your and the builder's discretion:

| Pattern | Solves |
|---|---|
| Auth gate + auth fallback | the auth child only verifies; the parent decides what a verified and an unverified caller hears, per intent |
| Guard value | never calling an API with a blank, "unknown" or handoff answer |
| Guarded run / tool | every API call gets a status check and a graceful failure route |
| Email / number asks | spell-back, keypad or SMS capture with the right read-back |
| Bounded retry | ask again, but not forever |
| Handoff / closing | a transfer with context; a clear end to the call |
| *Where needed:* confirm gate + once | irreversible actions run only on an explicit yes, and only once |
| *Where needed:* checkpoints + resume | callers who leave and come back don't restart from step 1 (long flows) |
| *Where needed:* silent loop | multi-item work without the second item getting skipped |

Set the deviation settings on purpose (best practices §06), and write asks with `references/asks-and-confirms.md`. Staging
runs the activation validators, so fix what it rejects. Before each update, read the live playbook and keep anything the
builder changed in the dashboard.

### 4. Test it on voice
Follow `references/testing.md`:
1. Write test cases on the bot's voice channel and run them against the changeset. Sim callers carry no caller metadata, and
   test-case `variables` only set meta variables, so drive each scenario through those or through what the caller says to a
   mock API, and describe API behaviour in `external_systems`.
2. Cover every decision-table row, the unverified path, an off-topic reply, "I don't know", a request for a person, a
   correction and an API failure.
3. For each run, check that the caller reached the intended steps and heard what you designed. Read the full call, not only
   the grader's summary. Judge by the transcript, not the grader.

### 5. Ship behind a dev gate, then open it up
Follow `references/shipping.md` §3–4:
1. Gate the playbook so only test callers and sims reach it, and promote.
2. The builder calls in to hear each path, with test values set any way that leaves the live build untouched (`testing.md` §2).
3. Open the playbook to everyone, or roll out by percentage.
4. Read the first twenty real calls.
5. To roll back, revert the changeset.

Never promote or start a rollout without the builder's go-ahead.

## Modifying an existing playbook
When the builder brings a live playbook, a call that went wrong, or a change request, skip the design walk-through except for
the parts the change touches:
1. **Read what's live.** The playbook and, if there is one, the call. Work from the live version, never from memory or an
   old export, and keep anything the builder changed in the dashboard. Use `diagnose-conversation` to name the surface that
   owns a problem, then `revise-playbook` for the change itself.
2. **Diagnose before changing.** Match what happened against `testing.md`'s signature table and the checklist. Tell the
   builder what you found and the change in playbook terms, and get their OK.
3. **Check the setup** if this bot is new to you, and read the best-practices sections the change touches.
4. **Stage a modify** on a named changeset: the full sections with step ids unchanged, existing `note` steps sent back in
   place, and the availability rules if the playbook is gated.
5. **Test** the changed path and the paths next to it with sims on the changeset.
6. **Hear it on a real call** only through `shipping.md` §5: a gate on a live playbook also gates every real caller.
7. **Promote** on the builder's go-ahead, read the live playbook back, then read the next real calls.

## The rules that cost the most
1. **Every question is an `ask`.** A `send` never waits; the next step fires while the caller is still listening. To text the
   caller, use the Send SMS step: it asks for consent itself.
2. **If the caller must hear it, it's an exact `send` with the variable in it.** Fees, terms, what else gets cancelled.
3. **Yes/no asks get accepted values; irreversible actions wait for an explicit yes and run once.** A correction later in
   the call re-runs every step after the corrected question.
4. **Never talk inside a loop.** Decide once before it, stay silent, speak one summary after.
5. **Guard the value before every API call; check the status and the result after.** Confirm the client lets your failure branch run.
6. **Clear call-scoped variables when a new call starts, never when the playbook starts.** Values from the last call on the
   same number survive 24 hours, but a caller who leaves the playbook and comes back on this call must resume where they
   were. Put the clearing block in the greeting: stage it on the changeset where the greeting uses the Conversation Start
   protocol, otherwise give the builder the block to add.
7. **Choose the deviation settings per ask.** Stay in the playbook for auth and data capture; exit where another flow should
   take over. The default loses most callers who ask a side question.
8. **Check which bot a tool belongs to.** Every bot's tools carry the same names. Before every call, check you are on the
   builder's instance (the runtime file says how).

## Reference files
| File | Read it when |
|---|---|
| `references/runtime-cli.md` | You are on adacli: commands, scripts, what each does |
| `references/runtime-mcp.md` | You are on the Ada MCP: tool calls, the replacement for each script, what MCP-only cannot do |
| `references/voice-best-practices.md` | **Every build, first**: the voice channel's nuances, so you can advise on the design |
| `references/voice-design-checklist.md` | **Every build, before any JSON**: what to settle and the fix for each item |
| `references/patterns.md` | Building: the step shapes for each fix |
| `references/asks-and-confirms.md` | Writing an ask, a confirmation, an offer, a fallback |
| `references/actions-and-evaljs.md` | Wiring APIs, status handling, EvalJS or code tools as the logic module |
| `references/testing.md` | Test cases, your own calls, the first real calls, debugging a bad turn |
| `references/shipping.md` | Setting up, changesets, the dev gate, rollout, rollback, building in a customer's bot |
| `references/voice-engine.md` | A call surprised you: why the engine replays, rewinds, suspends or speaks filler |
| `references/voice-engine-internals.md` | Debugging a call the engine table doesn't explain |
| `references/resources.md` | Other docs and tools, and which to trust |
| `examples/README.md` | Shipped voice builds to copy from |

## When a call goes wrong
Pull the full call and read what the caller said, what they heard and each variable set, in order. `testing.md` has a table of
signatures and causes; `references/voice-engine-internals.md` has the engine mechanics behind them. For a deeper diagnosis,
run `diagnose-conversation`, then `revise-playbook` for the fix. Most of the time the answer is on the checklist.
