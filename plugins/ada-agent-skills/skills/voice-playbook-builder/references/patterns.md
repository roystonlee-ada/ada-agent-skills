# Patterns — the step shapes that solve the checklist

Each pattern is a few steps you compose into `sections` on a changeset. The checklist says
*when* you need one; this file shows *what to write*. Field names follow the live playbook schema. If they disagree, the live
schema wins.

Conventions:
- Every section and step needs its own `id`, in the 24-character hex form the platform uses. Keep ids stable across edits, because `go_to` targets them.
- Reference a variable's value in text as `{{ variable:<id> }}`. A bare name is not substituted.
- `→` below is shorthand. Each line is one step: `SET` = set (exact `value`), `ASK` = ask, `RUN` = run, `IF` = if_else, `GO TO` = go_to.

Every flow needs auth gate + fallback (if it verifies), guard value, guarded run, bounded retry, handoff and closing. The patterns
marked *where needed* (confirm gate, once, checkpoints, silent loop) are for long flows and irreversible writes. They're best
practices that make the flow more natural; use them at your and the builder's discretion.

## The ask every pattern builds on

```json
{"id":"<24hex>","type":"ask","ask_mode":"reasoning","variable_id":"<var>",
 "instruction":"<what to extract; how to phrase the question>",
 "when_to_ask":"always","question_phrasing":"contextual","exact_words":null,
 "accepted_values":["yes","no","HANDOFF_REQUESTED"],"fallback_value":"no",
 "max_reask_attempts":1,
 "voice":{"capture_modes":["conversation"],"confirmation_style":"implicit"},
 "on_human_request":null,"on_off_topic":"stay_in_playbook","on_off_script":null}
```
- Free-text captures (names, references, emails) have **empty** `accepted_values`: the list is a strict allow-list.
- `on_*` fields left `null` inherit the playbook's setting. Set them on purpose (best practices §06).

## Auth gate and fallback: `AUTH_GATE` + `AUTH_FALLBACK`
The auth child only verifies or doesn't verify. It always returns to the parent: any lookup error or failed check sets an
error flag and exits, with no retry and no "having trouble" line. Immediately after the child returns, the parent checks
whether the caller was verified, and owns everything the caller hears either way. The unverified experience is different for
each intent, which is why it lives in the parent, never in the child.
```
Auth child:   RUN lookup (GUARDED_RUN)  →  failed? SET auth_error = "true" → RUN exit
Parent:       RUN   playbook <auth child>
              IF    verified is null  OR  verified is not "<verified value>"  →  GO TO <unverified section>
              … the verified flow
Unverified:   IF    auth_error is "true"  →  SEND exact "I can't look up <X> right now, but <best answer without auth>." → GO TO <closing>
              SEND  exact "I couldn't verify your account on this call, but <best answer without auth>."
              GO TO <closing>
```
- Branch on the verified value itself, not on "auth ran". A caller who failed auth must not hear account details.
- Give the best answer you can without auth: what the caller can do themselves and where (the website page, the email that
  has the link). Some intents can't be answered without auth; say where they can do it instead. Never a dead end.
- When that answer is long, texting a link (Send SMS step) is best practice, not a requirement.
- A read-only failure doesn't offer a transfer. A caller who asks for a person still gets one.
- Live reference: the cancellations build (`examples/subscription-voice-cancellations-v2`: not verified → the self-serve section, two
  exact scripts for "nothing active" and "not verified") and its modular auth (lookup error → `error_fallback` → exit;
  the parent decides what the caller hears).

## Never run an action on a missing value: `GUARD_VALUE`
After any ask whose value feeds an action:
```
IF  v is null OR v is "" OR v is "NONE" (match_case false) OR v is "unknown" OR v is "HANDOFF_REQUESTED"
    →  GO TO <re-ask once, or the other path>
```
`""` is what a backtrack leaves behind. `unknown` / your `fallback_value` is what an "I don't have it" leaves.

## Every API call gets a status check: `GUARDED_RUN`
On the action, map an output `http_status_code` to a numeric (long) variable. Then:
```
SET  status = "599"                      ← sentinel: a call that never writes still fails the check
SET  result = "NONE"                     ← the output the next step reads
RUN  action <id>
IF   status gte "400"  OR  result is null  OR  result is "NONE"  →  <failure route>
```
Check the result as well as the status. A connection failure can clear the status to null, and `null gte 400` is false. With
a status-only check, the caller heard "I couldn't find an account" and then "NONE" read out (seen live).
For a string status variable, use sentinel `"NONE"` and fail unless `is not "200" AND is not "201" AND is not "202" AND is not "204"`.
Async endpoints return 202. Choose the failure route per call: an honest line → handoff, an error flag → exit (the parent
decides what to say), or carry on (enrichment nobody needs). Failure branches only run where the client has status-code output on (the setup check reads it).

**Code and MCP tools (`GUARDED_TOOL`)** return a status field instead. Have the tool return one on every path, bind it to a variable, then:
```
SET  status = "NONE"
RUN  mcp_tool <tool id>
IF   status is not "ok" AND status is not "not_found"  →  <failure route>
```
The same rule holds: clear the result before the run and fail on a null or `NONE` result too.

## Explicit yes or nothing happens: `CONFIRM_GATE` (where needed: irreversible writes)
```
SET   checkpoint = "confirm"                         (if you use checkpoints)
SEND  exact: <the fact the caller must hear, with {{ variable:<id> }}>     (fees, what else gets cancelled)
ASK   confirm   accepted [yes, no, HANDOFF_REQUESTED], fallback "no", when_to_ask always, on_off_topic stay_in_playbook
IF    confirm is "HANDOFF_REQUESTED"  →  GO TO <handoff section>
IF    confirm is null OR confirm is not "yes" (match_case false)  →  SEND exact "No problem — I'll leave everything as it is." → GO TO <closing>
… the irreversible work, inside ONCE
```
Tell the confirm ask that the caller was just told the fact and not to re-explain it.

## Irreversible work runs once: `ONCE` (where needed: writes the API would repeat)
Needed when running the write twice would do it twice (a payment, a refund, a credit). Where the API refuses a repeat, a re-run can't double the write, so the flag
is optional; the cost of leaving it out is that a re-run hits the refusal and the caller hears the failure line. Check
which kind your API is before deciding (one action test on a test account that's already been through it).
```
IF   done is "true"  →  GO TO <after the work>
…    the cancel / payment / change (each call wrapped in GUARDED_RUN)
SET  done = "true"
```
A correction later in the call re-runs every step after the corrected question, actions included. The exact-SET flag survives that.
Clear the done flag in the greeting with the other call-scoped values, or the next call within 24 hours skips its own work.

## Callers who leave and come back: `CHECKPOINT_ASK` + `RESUME_DISPATCHER` (where needed: long flows)
Use this when restarting from step 1 would cost the caller (long flows, anything after auth). Skip it for short flows.
```
SET  checkpoint = "<name>"      ← before each ask, and before any handoff or exit that can fail
ASK  …
```
After setup (auth passed, tokens fetched), one dispatcher jumps to the saved question:
```
IF checkpoint is "reason"  → GO TO <reason ask>
ELSE IF checkpoint is "confirm" → GO TO <confirm ask>
```
Clear the checkpoint (`SET checkpoint = "NONE"`) at the end of the flow **and in the greeting**. The first step after a
resume can be an instruction `send`: "In one short sentence, say you are picking up where you left off."

## Multi-item work without skipping: `SILENT_LOOP` (where needed: several items)
Decide everything once before the loop (one EvalJS or code-tool call). Inside the loop, nothing is spoken.
```
SET   index = "0"
RUN   picker action (writes the next item, or "DONE")      ← step P
IF    picked is "DONE"  →  GO TO <one spoken summary>
RUN   the work for this item  (GUARDED_RUN)
SET   index = {{ variable:<index> }} + 1
GO TO step P
```
At most 5 items per turn: the engine stops a `go_to` target after 5 visits in one turn.

## Ask again, but not forever: `BOUNDED_RETRY`
```
SET   tries = {{ variable:<tries> }} + 1
IF    tries gte "<limit>"  →  GO TO <other path>
SET   value = "NONE"
SEND  exact "I didn't find that one — let's try again."     (optional)
GO TO <the capture ask>      ← that ask must be when_to_ask "always"
```

## Emails and numbers: `EMAIL_ASK` / `NUMBER_ASK`
- Email: `voice.capture_modes ["conversation","sms"]`, `confirmation_style "spell"`. Add to the instruction: "A reply that adds
  more of the address is still answering; it is unavailable only if the caller clearly says so." Strip an `sms:` prefix.
  Ask for an email only when the phone number isn't enough.
- Number: `capture_modes ["conversation","dtmf"]`, `confirmation_style "echo"`. Keypad digits arrive as `dtmf:1234`, so name
  that form in any instruction that reads digits.
- Phone numbers must work in any market. Capture exactly as said, digit by digit, keeping a leading + and the country code;
  re-ask when anything was unclear; never validate by counting digits. Formatting belongs to the API: ask the builder what
  format their lookup needs. The instruction that worked:
  > Ask exactly: "What's the phone number on your account?" Capture the phone number from the caller's most recent reply
  > exactly as they said it: digits only, keeping a leading + and country code if they give one. Convert the spoken digits
  > one at a time, in order ('oh' is 0, 'double five' is 55); never drop, add or reorder a digit. If any part was unclear,
  > don't guess: ask the caller to say the whole number again, or key it in. Keypad digits arrive as dtmf:5550123; save
  > just the digits. A reply that adds more digits is still answering. If the caller says they don't know it, don't have an
  > account, or won't give it, capture NONE.

## Texting the caller: Send SMS
```json
{"id":"<24hex>","type":"run","target_type":"sms","message":"<text>","result_variable_id":"<var>"}
```
It asks for consent itself, so don't add your own "want a text?" ask. Branch on the result (`sent` / `declined` / `failed`).
Don't speak straight after it. Needs the Send SMS step turned on for the bot.

## Handoff: `HANDOFF_SECTION`
```
SET   handoff_note = "<what was tried, what failed, verified or not>"     (if the handoff passes context)
SEND  exact "I'll connect you with a specialist who can help — transferring you now."
RUN   handoff <id>
```
Terminal: nothing after it runs. Set the checkpoint before jumping here from anywhere that can fail.

## Clear end: `CLOSING`
```
SET   checkpoint = "NONE"         ← before the ask: it can exit the playbook
ASK   anything_else  accepted [yes, no, HANDOFF_REQUESTED], fallback "no", when_to_ask always, on_off_topic exit_playbook
IF    anything_else is "HANDOFF_REQUESTED" → GO TO <handoff>
IF    anything_else is "yes" → SEND instruction "Say you're happy to help and ask what they need." → RUN exit
SEND  exact "Thank you for calling."
RUN   exit
```

## Test values while you build
Any method that leaves the live build untouched and still lets sims run (`testing.md` §2): test numbers or accounts that a
mock maps to scenarios, or a first section titled **"TEST FIXTURE — remove before go-live"** holding exact SETs of the
variables a branch reads. Remove test values before you open the gate. In sims, test-case `variables` set meta variables only.
