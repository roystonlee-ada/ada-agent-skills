# Testing a voice playbook

The goal is to hear every path the way a caller will, before a caller does. Work from cheapest to most real:
test cases on the changeset → your own calls → the first real calls. At each step, check the caller got the experience you
designed, not just that the flow finished.

## 1. Test cases on the changeset (Ada MCP)
Test cases simulate a whole call, driven by a caller goal, on the voice channel, against your staged changeset. Nothing live changes.

1. **Create a test case** (the runtime file names the call; read its schema first):
   - `channel_id`: the bot's voice channel. Without it the test runs as chat.
   - `scenario_goal`: the caller, in their words. Say what they give only when asked and what they don't know.
   - `user_message`: their first line.
   - `success_criteria`: outcomes for the caller ("hears the $25 fee before being asked to confirm", "is transferred with a
     reason"), not steps.
   - `variables`: **only meta variables get set.** Ada holds metadata (caller ID and the rest) for real callers, not for sim
     callers, so set the meta values a branch reads here, such as `phone_number`. Variables you created are not applied. To give
     a sim a scenario beyond that, have the mock API map what the caller says to it (a test phone number or account number per
     scenario) and put that value in the caller's goal. If you find a more consistent way to drive sims from native metadata, use it.
   - `external_systems`: how the APIs behave, in plain language ("account 1001 has two memberships, one paused; cancel succeeds
     once per membership"). APIs in mock mode answer from this text. **An API in live mode sends its real request even in a
     simulation**, so check each tool's `simulation_mode` before running anything that writes.
   - `changeset_id`: scope the test to your changeset if it only makes sense there.
2. **Run** the cases against the changeset. The run uses the changeset's versions of everything.
3. **Read** the run. Its `conversation` is what the grader read. It leaves out playbook steps and
   tool calls, so pull the full transcript for anything that looks off.

What sims hide:
- EvalJS actions run for real in sims, so a mock built in EvalJS is real logic and real failures (a connection error) show up.
- Sims fake SMS delivery: the sim caller "reads" a text that may never arrive on a real phone. Prove texts on a real call.
- A dev gate on the caller's phone number keeps sims out too. Run the sims before you add it, or give the gate a condition
  sims can pass (`shipping.md` §3).

Cover: each row of the decision table, the unverified path, an off-topic reply mid-question, "I don't know", a request for a
person, a correction ("actually, it's…"), and an API failure (describe it in `external_systems`).

**Judge by the transcript, not the grader.** The grader also reads internal events. It has failed "never reads an ID" because
an id sat in a variable, and "never says pending" for a pause that legitimately starts next cycle. Treat the sim as a caller,
the grader as a junior reviewer, and the transcript as the truth. Write the key caller line as "Your reply to THAT question
must be exactly: …". Sim callers wander off script otherwise.

After a batch, summarise each run on one screen: pass/fail, the failed criteria with the grader's reason, what was said, and
your variables as they were set (the runtime file has the helper).

### Quick checks in chat
A chat check against the changeset with a test value exercises staged edits in a few seconds (the runtime file has the
command). It's good for logic and wording, and blind to voice behaviour (barge-in, read-backs, keypad, timing).

## 2. Your own calls
Simulations can't do everything: in prod they can't authenticate (the greeting flags them), they skip the forced handoff on a
failed API call, and they don't sound like a phone line. So call in yourself before customers do:
- Promote the playbook behind the dev gate (`shipping.md` §3) so only your test callers reach it.
- **Test values.** Any method works as long as the live build is untouched and the sims still run. Pick per build:
  - *Test numbers or accounts:* where the API is a mock, map each test phone number or account to a scenario. You pick the
    branch by what you say on the call, with no playbook edits.
  - *TEST FIXTURE section:* a first section titled "TEST FIXTURE — remove before go-live" with exact SETs of the values a
    branch reads. Call, change the values, call again. A later step that writes the same variable (the auth child, a lookup)
    replaces the fixture value; set that step's input (a test account id) instead.
  - *Real test accounts:* where the customer has them, they exercise the real APIs too.
- A fixture doesn't stop a real write, so run irreversible paths only on accounts set up for them. Cancels and pauses are usually single-use per account.
- Never speak a test marker ("Test mode…"): it changes how generative steps behave.
- **Listen to the recording**, not just the transcript: clipped sends, long silences and read-backs only show up in audio.
- Check each call in full: did it reach the intended steps, set the
  variables you expected, and end the way you designed?

## 3. The first real calls
Open the gate (or roll out by percentage), then read the first twenty calls. Flag failure phrases, non-2xx statuses, backtracks, off-topic exits and ids read aloud. Read every flagged call with
`--detail`, and a few unflagged ones. In the first real calls of the reference cancellation build every API call was correct and most callers
never verified: the fallback wording was the problem, and no test would have found it.

## Testing the logic module
If the flow decides things in EvalJS or a code tool, test the module with real inputs before wiring it: harvest real API
responses from transcripts (read-only), run every selection pattern and decision mode through it, and accept nothing short of
zero errors. The action test runs an action with literal values and shows what each output would store. See
`actions-and-evaljs.md`.

## Debugging a bad turn
Pull the full transcript. The `playbook_v2_step`
entries carry each extraction's status (`did_not_answer`, `unable_to_provide`, `intent_change`, `backtrack`). For why the engine
did it, see `voice-engine.md`, then `voice-engine-internals.md`. For a deeper
diagnosis run `diagnose-conversation`.

| Signature | Cause | Fix |
|---|---|---|
| Question spoken twice / didn't wait | a `send` asked the question | make it an `ask` |
| Earlier question asked again, later answers cleared to `''` | backtrack: the caller's reply read as a correction | tell each ask what a reply aimed at an earlier question means; no two asks own the same answer (`voice-engine.md`) |
| Playbook stops mid-flow, general agent answers | off-topic reply with `on_off_topic: exit_playbook` | `stay_in_playbook` on that ask, or accept the handover |
| Playbook never resumes after a side question | the agent didn't pick the flow back up | checkpoints; say in general instructions what "carry on" means |
| Fallback written on the first reply, no re-ask | `unable_to_provide` ("I don't have it") | instruction wording; guard the value before the action |
| Same step hit again and again in one turn | an extraction keeps returning a stale value into a loop | latest-reply guard in the instruction, or exit |
| Confirm auto-completes from a selection | "the 3pm one" read as a yes | explicit confirm question; `accepted_values` |
| Hands off after a successful finish | last step is a handoff, not `exit` | end every path in `exit` after the closing line |
| Failure branch never runs, call transfers | the client's action status output is off | setup check; or have the API return 200 with an error field |
| Nothing written for the asked field, flow just leaves | "never mind" handled above the steps | design re-entry; no step can catch it |
