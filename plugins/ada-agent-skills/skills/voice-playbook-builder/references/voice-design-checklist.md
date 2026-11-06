# Voice design checklist — settle these before you build

Walk through this with the builder before writing a single step. Every item is something builders don't think about until
they're deep in a build, then fix by trial and error. Each one says what gets missed, what the caller experiences, and the fix:
a setting, or a pattern in `patterns.md`.

Nothing here is a hard rule. These are guidelines for building a good voice experience, and each section opens with when it
applies, so skip what doesn't fit the build and say why.

Sources: live voice builds for a subscription business (cancel v2, auth + email capture), the Voice Build Best Practices
guide (full text in `voice-best-practices.md`), and how the Playbooks V2 engine behaves. The *why* behind each
row is in `voice-best-practices.md` and `voice-engine.md`; the step shapes are in `patterns.md`.

---

## 1. Before the build — get these from the customer
*When: every build.*

| Settle | Why it can't wait |
|---|---|
| The **business rules as a decision table**: who is eligible for what, what cascades, what needs a human | Every rebuild on the reference builds traced back to a rule found mid-build (add-on cascade, fee disclosure, "has an active membership" gate) |
| **Exact wording** for anything legal, financial or brand-critical (fees, terms, disclosures) | These must be exact `send` messages. Generative wording softened a $25 fee and said "cancelled" before anything ran |
| **APIs that cover the whole journey**, not one step, plus a **read-only lookup** to run first | Read-then-write playbooks fail far less than write-first ones. A missing step means a handoff on every call |
| A **failure policy per API**: retry, alternate answer, or handoff | Otherwise every error becomes a transfer or a dead end |
| **A test record for every row of the decision table** (each status, eligibility case, single and multiple accounts), plus accounts that can go through each irreversible path | Rows without a record only get tested by real callers. Cancels and pauses are single-use per account. Where no record exists, use test numbers a mock maps to scenarios, or a TEST FIXTURE section for your own calls, removed before go-live (`testing.md` §2) |
| **The phone format the lookup API needs** (E.164, digits only, with or without country code) | Capture stays market-neutral; formatting belongs to the API or logic module (`NUMBER_ASK`) |
| **Which handoff, and that it reaches a real queue on voice** | A handoff named `[DEV …]` once connected a sim caller to the real support line |
| **How the playbook should be found**: 8+ real caller phrasings, and the sibling flows it must not steal from | A right playbook for the wrong callers (Membership Details fired on cancel calls) |

---

## 2. The start of the call
*When: the build reads values the greeting sets, sets call-scoped values that must be cleared, or changes the greeting.*

| Builders miss | Caller experiences | Fix |
|---|---|---|
| Actions running before the first word | 3–6 s of silence, "Hello?", hang-ups | Static audio first (disclosure, name); run lookups while it plays; personalisation last |
| The default error fallback on greeting requests | The greeting repeats, or "as chat" is spoken | Edit every greeting request's fallback to continue silently; branch on "is set", not success |
| Variables surviving 24 h from the last call from the same number | A new call skips auth, resumes the old flow, or hits a retry limit it never used | Clear auth flags, tokens, lookups, checkpoints and counters **in the greeting**, never at the top of the playbook: a caller who leaves the playbook and comes back mid-call must resume where they were |
| Saying up front what Ada can do | "Can you do it on this call?" and early agent requests | First line of the playbook: "I can cancel that for you on this call. First I'll verify your identity." |
| Double acknowledgment | A stutter: the voice agent already acknowledged | No acknowledging `send` at the top; pin `acknowledgment_instruction` to `say exactly "Sure."` if it paraphrases |

## 3. Authentication
*When: the flow needs account data or changes an account. Scope it in the design phase with the customer; auth is nuanced and must be secure.*

| Builders miss | Caller experiences | Fix |
|---|---|---|
| Auth that costs more than it unlocks, or one hard capture as the only way in | Callers fail or drop out of auth; the call never gets past FAQ answers | Least friction is the default. Auth earns its friction when it unlocks a higher-value answer or action. When the capture is hard on a phone (email addresses, long account numbers, spelled names), offer a simpler verification first (caller ID, keypad digits, ZIP, last 4) and keep the hard capture as a fallback, never the only route |
| Asking for auth when the answer doesn't need it | Friction for FAQ callers | Auth only in playbooks that need account data (modular auth child) |
| Deciding how to identify and verify without the customer | A flow that is either too strict for the data (callers can't pass) or too loose for what it exposes | Make it a consultative conversation with the customer's team, not a default. Start from what's on the account and what the answer exposes. Could the caller's phone number alone be secure enough for a read-only answer? Would the last 4–6 digits of an order number plus a phone match work instead of a full 16-digit number? Is "last 4" unique enough in their data? Agree the trade-off with them and write it into the decision table |
| Picking an auth level without a reason | Too much friction for simple answers, or too little security for changes | Match the level to what the answer exposes (Ada's voice auth levels model): **1** caller ID match → personalization/routing only · **2** two-element match (e.g. ZIP + last 4) → standard account answers · **3** one-time code by SMS/email (or push "yes, it's me") → sensitive changes. Decide which data and actions each level unlocks; gate playbooks on it |
| Identify, then verify | Slow, failing auth | Identify: caller ID (silent) → account or phone number (speech, keypad or SMS) → email only if the phone isn't enough. Verify: **one-time code is preferred**, texted or emailed to the phone number or email **on file in the customer's system**, never to the number that's calling (caller ID can be spoofed), and checked through the customer's API → knowledge factors when a code isn't possible. Don't build a code flow of your own; advise the customer on the best path their systems support |
| Treating failed auth as the end | "I couldn't verify you. Anything else?" | Failed auth is a branch the parent owns, different for each intent: the best answer without auth (what they can do and where), a texted link if the answer is long (`AUTH_FALLBACK`) |
| Re-verifying a caller who already passed or failed on this call | The same questions twice | Check the verified / attempted flags first (`AUTH_GATE`) |
| Gating on "auth ran" instead of "verified" | Account details read out after a failed check (seen live) | Every auth-gated playbook branches on the verified value itself |
| Patience for codes | Timeouts while the caller finds the text | Give time; tell them the code is on its way; one retry |
| (Optional) personalising the opening | Callers ask for a human straight away, not expecting much | A silent match (caller ID → account) can show Ada knows them and head off "agent please". Only when it solves a real problem without friction; never an extra greeting question just to personalise |

## 4. Asking questions
*When: every build.*

| Builders miss | Caller experiences | Fix |
|---|---|---|
| Asking a question with a `send` | "Asked me twice", "didn't wait for my answer" | Every question is an `ask`. A `send` never waits |
| Unset re-ask cap | The same question four times | `max_reask_attempts: 1` (free text) on every ask |
| No fallback | A caller who never answers carries an old value into the branch | `fallback_value` on every ask you branch on (NONE / no / NOT_X) |
| Yes/no without accepted values | "No" saved as `false`, branch checks `no`, membership cancelled (seen live) | `accepted_values: yes / no / HANDOFF_REQUESTED` |
| Instruction rules on exact answers | A bare "yes" ignores your polarity rule | An exact match skips the instruction; make the question unambiguous ("Would you like me to connect you with an agent…?") |
| "I don't know" | The fallback is written at once, no re-ask; the next action runs on nothing | Guard the value before any action (`GUARD_VALUE`); say partial answers still count |
| Calling an API with an empty answer | 400s/422s; "verification failed" for a caller who just didn't know | `GUARD_VALUE` before every `RUN` that uses a captured value; exclude `HANDOFF_REQUESTED` |
| Emails | Long, misheard, repeated spelling | Only when the phone number isn't enough; always allow SMS capture (`EMAIL_ASK`: spell-back + SMS); strip the `sms:` prefix in the instruction; two tries then another path. Reference: the auth email ask in `examples/subscription-voice-email-capture` |
| Numbers | Misheard digits (less common than people expect) | Any method works: speech is fine, keypad helps, SMS capture works well. `NUMBER_ASK` offers keypad + speech with an echo read-back; add `sms` to capture modes where SMS is on. Keypad arrives as `dtmf:` text |
| Confirmation style | Read-backs that are too slow or too risky | implicit (names, yes/no) · echo (dates, amounts) · spell (emails). A code the flow checks itself needs no read-back: a wrong code gets a retry |
| `when_to_ask` | "Anything else?" reused an earlier "yes" and skipped | `always` for anything that must be asked fresh; `only_when_needed` for things callers volunteer |

## 5. Callers who don't answer the question
*When: every build with asks. The resume rows matter most in long flows.*

| Builders miss | Caller experiences | Fix |
|---|---|---|
| Deviations at an ask: a topic change, a question, a request for a person | Default `exit_playbook` suspends the flow on a topic change; most never come back (seen on a reference build, mostly mid-auth) | Set the three deviation settings (Advanced settings → Conversation deviation behaviour) for the playbook, and override on the asks that differ. Auth and data capture: `on_off_topic: stay_in_playbook` and `on_off_script: search_knowledge` on the ask. Where another flow should take over: `exit_playbook`. `on_off_script: skip_knowledge` moves on with the fallback value, so branch on it. These act independently only where the client's combined flow controls are on (confirm with Ada support); check each ask's resolved values (the runtime file has the command) |
| Asking for a person mid-ask | Bot-level handoff; "something went wrong" if it isn't wired for voice | `on_human_request`: `exit_playbook` hands to the bot's handoff (make sure it works on voice); `stay_in_playbook` on an ask finishes that question, then confirms and hands off. Clearly escalating callers are handed off either way. Or capture `HANDOFF_REQUESTED` in accepted values and route to your own handoff section |
| Callers who leave and come back | The playbook starts from step 1: intro and every question again | Checkpoint before each ask (`CHECKPOINT_ASK`), `RESUME_DISPATCHER` after setup, clear at the end and in the greeting |
| A fallback that re-triggers the playbook | The same script again and again in one call ("I can't get online") | After a fallback, offer a choice (text the link / connect to an agent) and act on it |
| Corrections ("actually, my ZIP is…") at a later question | The engine jumps back, clears later answers, and **re-runs every step after it, actions included** | Collect correctable values with asks; run irreversible work inside `ONCE` (done flag); treat `''` as unset |
| Two questions whose answers overlap | False "corrections" that clear the flow | Keep confirms about confirming; each ask says what a reply aimed at an earlier question means |

## 6. Confirming and doing irreversible things
*When: the flow changes something (cancel, pause, payment, update). Skip for read-only flows.*

| Builders miss | Caller experiences | Fix |
|---|---|---|
| Proceeding on "not no" | Hesitation treated as consent | `CONFIRM_GATE`: proceed only on an explicit yes; everything else leaves things unchanged |
| Facts inside a generative confirm | The fee or cascade skipped, then retracted when asked "why?" | The fact the caller must hear goes in an exact `send` before the confirm; the confirm is told not to re-explain |
| A transfer that can fail, then re-entry | A stale checkpoint jumped to the confirm and cancelled something the flow had refused | Set the checkpoint to the safe re-entry step **before** any handoff or exit |
| Running the same write twice | A correction later in the call re-fires the cancel | `ONCE` around the irreversible block |

## 7. APIs and waiting
*When: the flow calls any action or tool.*

| Builders miss | Caller experiences | Fix |
|---|---|---|
| A call with no status check | "Done!" when nothing happened, or a dead end (a null status passes `gte 400` as false) | Every API call gets a status check followed by a graceful route: `GUARDED_RUN` (sentinel before, any-2xx range check after; async endpoints return 202). Code and MCP tools return a status field instead: `GUARDED_TOOL`. Live examples: the reference auth child (status ≥ 400 → set `error_fallback` → exit; the parent decides what the caller hears) and cancel v2 (sentinel 599 → honest line → handoff) |
| The client setting behind failure branches | Failure branch never runs; the call transfers. Sims hide it | The setup check reads it from real calls (status-code output) |
| Choosing the failure route | Every error is a transfer | Choose per call. Auth failed → set an error flag, return to the parent, unverified answer · enrichment → continue silently · read-only → general answer + texted link (Send SMS step) · partial write → handoff with context |
| Dead air behind silent steps | Caller thinks the line dropped | One short exact `send` before slow work ("Let me pull that up, this takes a few seconds."); never "done" before the result |
| LLM steps for logic | Slow turns, inconsistent decisions | Decide once in a deterministic action (EvalJS / code tool); exact sends speak its output |
| Talking inside a loop | Second item skipped, "cancelled both" | `SILENT_LOOP`: decide before, say nothing inside, one summary after; ≤5 items per turn |

## 8. How it sounds
*When: every build.*

| Builders miss | Caller experiences | Fix |
|---|---|---|
| Lists in one utterance | A breathless run-on | Compose in the action: count in words, "First, … Second, …", `...` between items |
| Product names with symbols or terms | "U, dot, S, dot", "one Months" | Speech-normalise names in the action ("U S", "six months"); verify in a real voice sim |
| Text from a variable or a tool, spoken as written | "1689 Arden Way" read as "one, six, eight, nine"; dates and amounts read like data | Tell the `send` how to say it. Use an instruction `send` that names the spoken format: "say the street number as a number (sixteen eighty-nine)", "dates as month and day (October twelfth)", "amounts in dollars and cents". An exact `send` speaks a variable literally. If the tool belongs to someone else, flag its wording to them as well |
| URLs and long steps | Spelled-out links nobody can use; a block of steps nobody can follow | Soft rule: prefer to text URLs; keep spoken instructions short and offer to text longer ones. A one-step-at-a-time walkthrough needs an `ask` per step (a `send` doesn't wait for a reply) and is unproven, so test it in sims first |
| Reading ids or references | Digits nobody needs | "It's in your confirmation email" |
| Menus | Callers can't hold more than three options | Three at most per prompt |
| Two exact sends back to back | The first gets clipped | Put an ask or a slow action between them, or merge them |
| Ending abruptly | Caller unsure the call is over | `CLOSING`: one "anything else?", then a clear goodbye |

## 9. Texting the caller
*When: the flow texts the caller (links, SMS capture).*

| Builders miss | Caller experiences | Fix |
|---|---|---|
| Adding a consent question before the Send SMS step | Asked twice: the step asks for consent itself | Use the playbook **Send SMS** RUN step and let it ask. Don't add your own "want a text?" ask. Skip its question only via its consent variable when you already hold a yes |
| The step quietly not sending | "I've texted you" when nothing went | It never stops the flow: the step turned off (a per-bot setting), no number, Agent SMS off, a no or a provider error are all logged and skipped. Set its result variable (`sent` / `declined` / `failed`) and branch on it |
| A spoken line straight after the step | The line gets clipped (Ada speaks its own "Okay, I'll send that now") | Let the step's confirmation stand; if you need to speak next, make it a question. Observed in sims, confirm on a real call |
| A caller who says no | Nothing they can use | On `declined`/`failed`: a two- or three-sentence spoken version, then email or a handoff |
| Landlines and blocked numbers | A text that never arrives | Ask "are you calling from a mobile?" or check line type before relying on SMS |
| Texting from greetings or handoffs | No SMS step there | Twilio Messaging API in an action, with your own consent ask; the number needs A2P registration |
| Callers phoning the SMS number back | Broken handoffs (no SIP metadata), inflated volume | Leave the SMS number's voice config empty; test by calling it |

## 10. Handoffs and finishing
*When: every build.*

| Builders miss | Caller experiences | Fix |
|---|---|---|
| A handoff the agent can't act on | The agent starts over | `HANDOFF_SECTION` with a note variable: what was tried, what failed, verified or not |
| Steps after a handoff | They never run (handoff is terminal) | Put everything before it; checkpoint first |
| Making the handoff hard to reach | Transfers become hang-ups ("bad containment") | Don't. Report containment with automated resolution; if containment rises and AR doesn't, it's hang-ups |

---

## Before launch

- [ ] Every item above settled, or deliberately skipped with a reason
- [ ] Test values are gone (TEST FIXTURE section, test-number mappings)
- [ ] Sims cover each decision-table row, the unverified path, an off-topic reply, "I don't know", a request for a person, and a correction
- [ ] Each flow resumes correctly after an unrelated question forces an exit
- [ ] Each handoff tested end to end, including what the agent sees
- [ ] Test-number overrides removed or limited to known testers; critical variables cleared in the greeting
- [ ] You listened to recordings, not just transcripts
- [ ] Promoted behind a dev gate first; read the first 20 real calls
