Contents: 01 Ground rules · 02 Managing latency in the greeting · 03 Authentication on voice · 04 Failed authentication that still resolves · 05 How and when to capture email · 06 When callers don't answer the question · 07 Resume checkpoints: pick up where the caller left off · 08 API errors in playbooks · 09 Managing latency inside playbooks · 10 Saying things on a call · 11 Choosing glossary terms for voice (Draft) · 12 Texting the caller · 13 Metadata carries over for 24 hours · 14 Callers will phone the SMS number · 15 Good containment vs bad containment · 16 Get ahead of it with the customer · 17 Before launch

Ada voice · implementation guide

# Voice Build Best Practices

How we build greetings, playbooks and handoffs for voice AI agents, and what to settle with the customer before the build. Drawn from live voice builds and the questions that keep coming up.

Based on Marc M.'s Voice Build Best Practices v1.0 (Ada, November 2026).

## 01 · Ground rules

Voice is not chat read aloud. Callers can't scroll back, they can't see a link, they're often already frustrated, and every pause sounds like a dropped call.

- **R1 · Every question costs a few percent of callers.** Each extra question in a flow loses some callers. Ask only what the answer needs. Never re-ask something you already have.

- **R2 · Speak first, fetch second.** Dead air at pickup loses callers. Play static audio right away, and run requests while Ada is talking.

- **R3 · A failure should be invisible to the caller.** A failed API call should change which branch runs. It shouldn't produce an error message, a repeated greeting or a dead end.

- **R4 · Containment only counts if the caller was helped.** A hang-up after confusion is counted as containment. It's actually a failure.

- **R5 · Prefer to text links and long instructions.** A soft rule. Send URLs by SMS where you can. Short instructions can be spoken; offer to text longer ones.

- **R6 · An error is not a reason to hand off.** Voice is an expensive channel. When something fails, route to the next-best answer, and hand off only when a human is actually needed to finish the job.

## 02 · Managing latency in the greeting

The first seconds of a call matter most. If there's silence after pickup, callers say "Hello?", talk over the greeting, or hang up. On one build, many calls ended before the greeting played.

### Order the greeting so Ada speaks before any request runs

> **Avoid — requests block the first word**
> - **sys:** Caller lookup API
> - **sys:** Hours / holiday API
> - **caller:** … 3–6 s of silence …
> - **ada:** Hi, thanks for calling…

> **Do — static audio covers the requests**
> - **ada:** Thanks for calling Example Co. I'm Sam, an AI assistant, and this call may be recorded.
> - **sys:** Caller lookup + hours run while the line above plays
> - **ada:** Thanks for being a member since 2019. How can I help today?

- **The first block is static audio.** Use the AI disclosure, the recording notice and the agent's name. Nothing in it should depend on a variable.
- **Put requests after the first audio block.** Use them for caller ID lookup, hours checks, feature flags and personalization. The disclosure plays while they run.
- **Data that depends on a request goes last.** Personalization ("member since…") belongs right before "How can I help?".
- **Keep the first audio short.** A long opener makes callers talk over it. That has caused a voice-box bug where the call stays stuck in the greeting state.

### Make request failures invisible

- **Edit the error fallback for every greeting request.** By default the fallback can replay the greeting or post a generic error. Point it at a quiet continuation that leaves the variable unset and keeps going.
- **Branch on "is set", not on success.** If the lookup failed, the caller just doesn't get personalization. They shouldn't hear anything about a failure.
- **Watch for data that arrives late.** Amazon Connect sends its contact ID as touch tones, and the last digit lands about 5 seconds into the call. The greeting runs before that. Don't let anything in the first block depend on it.

> **Seen live:** on one build, a greeting API error routed to a fallback that repeated the greeting and said "as chat". It kept happening until the fallback was edited.

### Personalize the greeting when you can

If caller ID matches an account, add one detail that shows Ada recognizes the caller. This reduces "agent please" as a first utterance. Get the customer's legal or security team to approve it, because it plays before the caller is authenticated. Keep it to something non-sensitive like a membership tenure, not balances or order details.

## 03 · Authentication on voice

Authentication is the main limit on voice resolution. Without it there's no account-level answer. But asking for it up front adds friction for callers who only had an FAQ question.

**Principle: least friction for the value.** Ask as little as possible. Auth earns its friction when it unlocks a higher-value answer or action. Some captures are hard on a phone (email addresses, long account numbers, spelled names), so never make one of them the only way in: offer the simplest verification the account data supports first, and keep the hard capture as a fallback.

### Levels of authentication: match the level to what the answer exposes

Segment what the agent can say or do by security level, then pick the lowest level that covers it. Higher levels cost the customer more build work, not necessarily the caller more effort.

| Level | How it works | Unlocks | Caller effort | Customer build |
|---|---|---|---|---|
| **1 · Caller ID match** | The contact center passes caller ID (and profile data) at call start; Ada matches it to an account silently. No match → unauthenticated experience | Personalization, routing, profile-aware FAQs. No account changes or sensitive details | None | Low: pass caller ID and profile data at intake |
| **2 · Two-element match** | The caller gives two of a permitted set (last 4 of card, order number, ZIP, last 4 of SSN or bank, date of birth); an API returns match yes/no | Standard account answers and actions, per the customer's own verification policy | 2 questions | Medium: a match API |
| **3 · One-time code (possession)** | Identify the caller (caller ID or another identifier), send a code by SMS or email, the caller repeats it, an API verifies it. Push or in-app "Yes, it's me" and a sign-in link belong in the same bucket | Sensitive changes and details | Low: repeat a code | Higher: send + verify APIs (or Ada sends the SMS via Twilio when the caller's number confidently matches the account) |

- **Decide per level which data and actions are allowed** after authentication (order details, balances, cancellations), and gate each playbook on that level.
- **A caller ID match alone is not verification** for anything sensitive. Treat it as level 1.
- **Phase it:** start with what the customer can build now, and plan the path to level 3 where the experience calls for it.

### Agree the method with the customer's team

How to identify and verify callers is a consultative decision, not a default. Work it out with the customer's team from what's on their accounts and what each answer exposes, then write the trade-off into the decision table.

- **Start from the account data.** What could confirm it's the right person: phone, email, order details, ZIP, card on file?
- **Ask for the least the lookup needs.** The last 4 to 6 digits of an order number plus a caller ID match may do the job of a full 16-digit number.
- **Check it's unique enough.** "Last 4" can match more than one record in some data. Test it against theirs.
- **Accept a lighter method where the answer allows it.** For a read-only answer, a phone number lookup alone may be secure enough. Agree that explicitly with them.

### Only authenticate when the answer needs it

- **Modular auth:** a separate auth playbook that runs before any playbook that needs it. It always exits back to the calling playbook, whether auth succeeded or failed.
- **Pre-handoff auth:** a light version before transfer. It saves the human agent time and adds some friction that reduces reflexive agent requests. Cap it so it never stands between a determined caller and a human.
- **No auth up front for FAQ callers.** One build tried authenticating first and dropped it.
- **Optional: soft authentication in the greeting.** A silent match (for example caller ID to account) lets Ada personalize the opening. It shows the caller Ada can do more than they expect, which helps head off immediate requests for a human. Use it only when it solves a real problem without adding friction. Never ask an extra question in the greeting just to personalize.

### Order identifiers by cost to the caller

| Step | Identifier | Caller effort | Notes |
|---|---|---|---|
| 1 | Caller ID lookup | 0 questions | Silent. Match rates vary a lot (one build's was low), so measure before relying on it. |
| 2 | Account or phone number | 1 question | Numbers capture well by any method: speech works, keypad (DTMF) helps, and SMS capture works well too. Offer keypad or SMS alongside speech where you can. |
| 3 | Email | 1 slow question | Only when the phone number isn't enough (no match, or no phone on the account). Always allow SMS as a capture option. See Email capture. |
| 4 | One-time code (SMS or email) Preferred | Low | The preferred way to verify once the caller is identified: Ada sends a code, the caller repeats it, an API checks it. Needs send + verify APIs from the customer, or Ada can send the SMS itself via Twilio when the caller's number confidently matches the account. Give callers time to find the code. |
| 5 | Knowledge factor (ZIP, last 4 of card) | +1–2 questions | When a code isn't possible (no phone or email on file, MFA off) or the customer's policy calls for it. |

> **Example · modular auth, caller ID missed — 2 questions**
> - **sys:** Silent lookup by caller ID → no match
> - **ada:** I can help with that. First I need to find your account. What's the email address on it?
> - **caller:** j-a-n-e dot doe at gmail dot com
> - **sys:** Lookup by email → 1 account
> - **ada:** Thanks. To confirm it's you, what's the ZIP code on the account?

- **Already verified on this call? Skip auth.** Check the verified flag at the top of every auth-gated playbook.
- **Already failed on this call? Don't retry.** Go straight to the unauthenticated path or to handoff.
- **Settle the auth API before the build.** Ask for a method that verifies most callers (aim for 80%+). One build lived with a low phone-number match rate until email auth became available.

**Reference — Reference build · modular voice authentication**

1. **Silent caller ID lookup.** If the number doesn't match, ask once for the phone number on the account. That re-ask rescued few misses, so offer email as the next identifier.
2. **Pick the account.** Only active or pending-cancel memberships are offered.
3. **Verify:** a one-time code by SMS. If the account has no MFA factor, fall back to ZIP plus the card on file.
4. **Always return to the parent playbook** (Membership Details, Cancellations v2) with `mfaVerified` set either way. The parent decides what to do with an unverified caller.
5. **Mark the attempt.** `verification_attempt = true` means pre-handoff auth skips re-verifying a caller who already tried.

Day-one lessons: callers repeated the same number that had already missed. Some accounts have no phone at all. Callers need more patience while they find and read out the SMS code.

## 04 · Failed authentication that still resolves

A failed authentication should lead to the next-best outcome, not end the flow. Most callers who fail auth still have a question you can partly answer.

- **Treat failure as a branch.** The auth playbook sets `verified = false` and returns to the playbook that called it. That playbook owns the unverified path.
- **Cap attempts at two** per identifier, then move on. Don't make the caller repeat the same failing input.
- **Tell the caller what you can do, not what failed.** Offer general policy, a self-serve link by SMS, or a handoff that carries what you captured.
- **Pass the attempt to the handoff.** Send verified false, the identifiers tried and the reason, so the human agent doesn't start over.

> **Avoid**
> - **ada:** I'm sorry, I couldn't verify your account. Is there anything else I can help with?

> **Do**
> - **ada:** I couldn't find that account, but you can cancel from your account settings. I'll text you the link now. Or I can connect you with the team.

**Reference — Reference build · membership cancellations v2**

- Verified callers who hit a write failure (cancel-prep or place-cancel errors) go to a handoff with context. That's the error path that transfers.
- Two fixes from the day-one review are on the improvement list:
   - Give unverified callers a short choice instead of a five-step walkthrough: "I can text you the link to cancel online, or connect you with an agent."
   - Base the fallback on what the account looks like, so a caller with no active membership isn't told how to cancel.

## 05 · How and when to capture email

Email is the hardest thing to capture by voice. Addresses aren't real words, they mix letters and digits, and transcription mishears them. It takes a long time and it often fails.

### When

- Capture email only when it's the best identifier available, or you need it for follow-up (for example, a ticket that emails the caller).
- Try silent caller ID, then an account or phone number by DTMF, first.
- If the customer's ticketing system requires an email, ask whether a ticket can be created from the phone number alone before you design an email step.

### How

- **Capture it in a playbook `ask`**, not as an action input. That gives you control over the prompt, the read-back and retries.
- **Ask the caller to spell it.** Read it back in chunks (local part, then domain), not as one fast string.
- **Offer SMS capture as the alternative** when SMS is enabled: "I can text you, just reply with your email." When SMS is off, set the capture option to Speech only so Ada doesn't offer it.
- **Two tries, then a fallback:** a different identifier, SMS, or handoff.

**Reference — Reference build · modular voice authentication · email capture**

Runs only after the phone-number search finds no account. The live `ask`:

- **Instruction:** Ask "To help me find your account, can you spell out your email address?". This is an email address and will need to be stored in the format of an email address (name, at sign, domain). If an input starts with "sms" or "sms:", do not include this in the saved variable; that is a backend indicator that this input was sent via SMS and is not part of the email address. If the customer explicitly asks for a human agent, set to HANDOFF_REQUESTED. If the customer cannot provide a valid email after 2 attempts or refuses, set to NONE.
- **Settings:** `when_to_ask: always` · capture modes `conversation` + `sms` · confirmation style `spell` (always confirm).
- **Next:** member search by email, then back into the normal account checks and verification.

Results since launch, callers whose phone number found no account: verification rose several-fold. Texted emails did not verify better than spoken ones. Gaps found in review: no check for a blank email before the search runs (some searches failed on a blank value), and a handoff request inside the ask can be read back as if it were the email.

## 06 · When callers don't answer the question

Every `ask` step expects a specific answer. On voice, callers often ask for a human, change the subject, ask a question, or answer something else. Playbooks have native settings for the first three under **Advanced settings → Conversation deviation behaviour**. Set them on purpose for the playbook, then override them on the individual asks that need different handling.

### The three deviation settings

| Setting | Options | What the caller gets |
|---|---|---|
| **Customer asks for a human** (`on_human_request`) | **Exit playbook** (default) · Stay in playbook | **Exit:** the playbook ends and the bot's default behaviour takes over, normally its handoff. **Stay:** Ada acknowledges, keeps any answer the caller gave, carries on, and once the question (or the flow) is done asks whether they still want a person; yes hands off. A caller who is clearly escalating is handed off straight away, whatever the setting. |
| **Customer changes topic** (`on_off_topic`) | **Exit playbook** (default) · Stay in playbook | **Exit:** the playbook is suspended and the general agent takes over. It may offer to pick up at the same question, but that's the model's choice. **Stay:** Ada says it will come back to it, finishes the question (or the flow), then asks whether they still want to go into it. |
| **Customer asks a question Knowledge can answer** (`on_off_script`) | **Search knowledge** (default) · Skip knowledge | **Search:** Ada answers from Knowledge and comes straight back to the same question. **Skip:** Ada doesn't answer, and the step moves on with its fallback value (blank if it has none). Some guidance says Skip re-asks; the engine moves on, so check it in a sim. |

**Where you set it decides when a deferred request is handled.** A playbook-level setting means "let me finish this flow": the request waits until the playbook ends. An override on one ask means "let me finish this question": it's handled right after that step.

**Check the settings before relying on them.** The three settings only act independently where the client's combined flow controls are on for the bot. With only the older exit-behaviour switch, ask-level overrides work but playbook-level settings fall back to the defaults. Both default to off. Confirm with Ada support, prove the behaviour in a sim, and read what each ask resolves to (the runtime file has the command).

### Choosing settings for voice

- **Auth and data-capture asks:** Stay in playbook for topic changes and Search knowledge for questions, set on the ask. The caller gets an answer and stays in the flow. On a reference build, with the default Exit, most callers who changed topic mid-flow never came back, mostly during auth. Stay in playbook on these asks is not yet proven on live calls: prove it in a sim, then watch the first real calls.
- **Asks where another playbook should take over** ("I'd rather just cancel" at a pause question): Exit playbook for topic changes. The exit is the handover.
- **Human requests:** Stay in playbook on the auth asks gives "let me finish this question first", which saves the agent time. Keep it on the ask: a playbook-level Stay makes a determined caller wait until the whole flow ends. Either way, make sure the handoff it lands on works on voice, or the caller hears "something went wrong."
- **Skip knowledge** only where a side answer would derail a step that must be answered, and branch on the fallback value the step moves on with.
- **Checkpoints still matter.** A run that ends (a handoff, an exit, an action error) before the caller comes back starts again from step 1. See Resume checkpoints.

### Other answers the flow doesn't expect

| Caller does | What happens by default | Build for it |
|---|---|---|
| Answers a different question ("Can you just do it on this call?") | The model improvises: it offers SMS steps or a transfer the flow didn't intend | Answer the likely question up front in the playbook's opening line, before the first ask. |
| Gives an answer the flow can't use ("I can't get online") | The fallback re-triggers the playbook, and the caller loops | Add a loop guard: a counter that sends the caller to the alternative path after the second pass. |
| Answers yes or no to a question that's ambiguous | Yes and no get read the wrong way round | End the ask with a question where yes has one clear meaning: "Would you like me to connect you with an agent to explore your options?" |

> **Example · cancellation — answer the real question first**
> - **caller:** I want to cancel my membership.
> - **ada:** I can cancel that for you on this call. First I'll verify your identity.

> **Seen live:** in the first calls of the cancel v2 build, callers asked whether the cancel could be done on the call, and some asked for an agent before auth started. A phrase about not being able to get online made the fallback re-fire the playbook repeatedly in a single call. Separately, a stale checkpoint left from a failed handoff resumed straight at the confirm step. Reset checkpoints before any transfer that can fail.

## 07 · Resume checkpoints: pick up where the caller left off

Callers leave a flow mid-way. If the playbook was only suspended (Exit playbook), Ada may pick up at the same question. But if the run ended in the meantime (a handoff, an exit, an action error), the next time the playbook triggers ("OK, let's continue with the cancel") it starts again from step 1. Without checkpoints, the caller hears the intro again and re-answers every question, and each repeated question costs callers (rule R1).

### How it works

1. **Set a checkpoint before each question.** Right before every `ask`, set one variable to that stage's name: `reason`, `selection`, `discount`, `pause`, `confirm`.
2. **Check the checkpoint at playbook entry.** If it's empty, play the normal intro. If it's set, play one short resume line instead: "Let's pick your cancellation back up where we left off."
3. **Re-run the silent prerequisites.** Fetch the token again and keep auth gated on the verified flag, so a returning caller passes through without a second code.
4. **Send the caller to their question.** One if/else chain after the prerequisites: `IF checkpoint = reason → go to reason; ELSE IF selection → …`. No speech in the chain. Answers the caller already gave persist, so the question keeps its context.
5. **Reset the checkpoint at the end of the flow,** so a second task later in the same call starts fresh.
6. **Clear the checkpoint in the greeting,** so the next call from the same number within 24 hours doesn't resume the old flow. See 24-hour metadata.

> **Example · cancel v2 — caller leaves and comes back**
> - **sys:** checkpoint = reason
> - **ada:** Can you tell me why you'd like to cancel?
> - **caller:** Actually, what happens to my tree if I cancel?
> - **sys:** Knowledge answer → playbook exits
> - **ada:** [Answer from the help article]
> - **caller:** OK, go ahead with the cancel.
> - **sys:** Playbook re-enters · checkpoint = reason · auth passes silently · token refetched · jump to reason
> - **ada:** Let's pick your cancellation back up. Can you tell me why you'd like to cancel?

### Rules that keep resuming safe

- **Never resume to a step later than the one the caller's answers support.** On a reference build, a confirm checkpoint left over from a failed handoff jumped straight to the confirm step and cancelled a membership the flow had just refused. Before any transfer that can fail, set the checkpoint back to the last safe question.
- **Resume no further than confirm.** Re-check state before any write. If the membership was already cancelled, skip it and never claim a cancel twice.
- **Track per-item progress** (loop index, fee already disclosed, pause chosen) so a returning caller isn't re-asked about items already done.
- **Test it on purpose:** start the flow, ask an unrelated question to force the exit, then come back. The caller should resume at the same question.

## 08 · API errors in playbooks

Every action in a playbook can fail. Handle each failure in the playbook's own logic. Don't rely on the default error fallback, and don't treat a handoff as the catch-all.

### Decide what each failure costs the caller

| API that failed | Route to | Why |
|---|---|---|
| Auth lookup or verification | Unauthenticated answer | The caller can usually still be helped: general policy, a self-serve link by SMS. Same path as a failed auth. |
| Personalization or enrichment (greeting lookup, "member since") | Continue silently | It's nice to have. The caller shouldn't notice it's missing. |
| Read-only account detail (status, billing date) | General answer + SMS link | Point the caller to where they can see it themselves. Hand off only if they insist. |
| A write or transaction that's partly done (cancel, pause, refund) | Handoff with context | The caller is mid-transaction and only a human can finish it. Pass what was attempted and what failed. |

### Build the check so a failure can't look like a success

- **Set the status variable to a failure value before each call** (for example `599` or `NONE`). If the action never writes a status, the flow still sees it as a failure. A `null` status compared with `>= 400` evaluates to false, so a failed call quietly passes as a success.
- **Accept the whole success range** (200, 201, 202, 204), not one exact code. Asynchronous endpoints often return 202.
- **Refresh tokens before loops.** Fetch the token again at the top of a work loop so a long call doesn't fail halfway through.
- **Every failure branch says something.** Tell the caller what happens next. An empty error branch also blocks the playbook from going live.

> **Avoid — auth API down → handoff**
> - **sys:** Member lookup → 500 → error fallback → transfer
> - **ada:** Sorry, something went wrong. Let me transfer you.

> **Do — auth API down → unauthenticated answer**
> - **sys:** Member lookup → 500 → verified = false
> - **ada:** You can cancel any time from your account settings. I'll text you the link. Would you like me to stay on while you do it?

## 09 · Managing latency inside playbooks

Turns of 5–10 seconds inside playbooks are the most common voice question we get from implementers. There are two ways to fix it: make the wait shorter, or tell the caller there's a wait.

### Put a status message before every long step

Before any API call or chain of steps that takes more than a couple of seconds, say what's happening and roughly how long it'll take.

> **Example — status message, then the wait**
> - **ada:** Let me pull up your membership. This takes a few seconds.
> - **sys:** getMembershipDetails · categorize · branch (≈4 s, covered by interstitial audio)
> - **ada:** I see two memberships on your account…

- **Make sure acknowledgements don't sound like confirmations.** A quick "Got it" before an action has run sounds like it's done. Say "Let me check" until the result comes back.
- **Turn on interstitial audio** so a wait doesn't sound like a dropped call.

### Make the wait shorter

- **Replace LLM reasoning steps with deterministic logic** (if/else, EvalJS). Each reasoning set adds a model turn.
- **Collapse consecutive silent steps.** Fewer steps means less overhead, and playbook compilers help most on playbooks with lots of if/else steps.
- **Don't ask the caller for computed values.** Values like epoch dates, if marked as caller inputs, make Ada try to collect them and read them back digit by digit.

## 10 · Saying things on a call

- **Long instructions:** a single `send` step plays the whole block, and if the caller interrupts, Ada still treats it as delivered. Keep spoken instructions short, or offer to text the full list. Walking a caller through one step at a time would need an `ask` per step, because a `send` doesn't wait for a reply. That approach is unproven: try it in sims before relying on it.
- **URLs:** prefer to text them. Spelled-out URLs ("h-t-t-p-s colon slash slash…") are hard to use. If you must say one, keep it to the short domain and path. Check the persona, custom instructions and knowledge for anything telling Ada to read links aloud.
- **Pronunciation:** set Glossary voice pronunciations for brand names, products and places. Custom instructions don't apply in greetings and handoffs, so write those phonetically.
- **Values from variables and tools:** tell the `send` how to say them. An exact `send` speaks a variable as written, so "1689 Arden Way" comes out as "one, six, eight, nine". Use an instruction `send` that names the format: street numbers as numbers ("sixteen eighty-nine"), dates as month and day, amounts in dollars and cents. If the wording comes from someone else's tool, flag it to them too.
- **Menus:** three options at most per prompt. Callers can't hold more than that in their head.
- **Read-backs:** chunk them and slow them down. The transcript can differ from what the caller actually heard, so listen to the recording when you QA.

## 11 · Choosing glossary terms for voice (Draft)

On voice, glossary terms do two jobs. **Voice detection** helps transcription hear a word correctly. **Voice pronunciation** controls how Ada says it. Only 30 terms per AI agent can have voice detection on, so choose them carefully.

### Know the limits

- **30 terms with voice detection per AI agent.** This is a hard limit with no setting to change it. It comes from the transcription provider, which accepts roughly 20–50 phrases per call.
- **Every user term on a voice term counts toward that budget.** Extra user terms push other terms out without any warning. Keep one user term per voice-detection term.
- **Pronunciation doesn't need voice detection.** You can fix how Ada says any term without using one of the 30 slots.
- **The glossary isn't applied when an `ask` or `set` step extracts a variable.** Don't count on a glossary alias to fill a variable correctly. Handle that in the step's instructions.
- **A term only applies on the turn that contains it.** On a reference build, later turns drifted back to the old product name. Fix the wording in knowledge and playbooks too.

### Decide what each term needs

| Problem | Fix | Uses a voice slot? |
|---|---|---|
| Callers say a word that transcription gets wrong and the call can't continue without it (store names, product names that drive routing) | Voice detection on | Yes |
| The same word is consistently misheard as something else ("Dunedin" heard as "Doomed Inn") | A term with voice detection off and the mishearing as the user term. Set it to Custom translation mode or give it a definition, or it won't match. | No |
| Ada mispronounces a brand, acronym or place name | Voice pronunciation, spelled the way it sounds ("sock" for SOC) | No |
| Callers use a different word than the customer does ("subscription" instead of "membership") | A normal glossary term | No |

### Rank candidates by impact

1. **Test on the live agent first.** Only add a term when the agent actually gets the phrase wrong. On a reference build, most of the proposed terms were already handled correctly. Only a couple were added.
2. **Give voice slots to words that decide where the call goes:** store and location names, product names that route to a playbook, and plan names the caller has to choose between.
3. **Prefer words that aren't in the dictionary.** Common English words are usually transcribed fine. Brand names, made-up product names, and non-English place names (for example te reo Māori in New Zealand) are not.
4. **Leave out words that only appear in Ada's answers.** Those need a pronunciation, not voice detection.
5. **Check the effect afterwards.** Look at transcripts from before and after. The conversation view shows when glossary terms were applied.

### Workflow: find, cut, roll out slowly

**Reference — Step 1 · Find candidates**

Use a glossary-builder skill if you have one. It needs adacli and the Ada MCP. It reads real conversations and knowledge, finds vocabulary gaps (callers say "refund" where the customer says "Travel Credit"), drafts terms with real examples, and runs an approve/decline review in the terminal. If the customer needs to sign off first, it gives you a CSV.
**Reference — Step 2 · Cut the list to terms the agent actually gets wrong**

The builder finds gaps in the wording. A gap doesn't always mean the agent fails. Test each candidate before adding it:

- **Try the phrase on the live agent** (a chat check, or Test AI Agent for voice). Keep the term only if the answer, routing or wording is wrong. On a reference build, few of the proposed terms made the cut.
- **Sort the survivors using the table above:** voice detection, a mishearing alias, pronunciation, or a normal term. Only terms that decide where the call goes get a voice slot.
- **Check for conflicts** with existing terms and knowledge (the MCP glossary conflict guide). A term can pull callers into the wrong playbook.

**Reference — Step 3 · Roll out slowly, review, then make it live for everyone**

**Glossary edits don't go through change sets.** A glossary term goes live as soon as it's saved. Use the term's availability rule as the rollout control instead:

1. **Testers only.** Create the term with an availability rule on your test-user flag (for example `dev_user = true`). Run simulations and test calls.
2. **A slice of live traffic.** Change the rule to a rollout variable set in the greeting (for example, a random bucket covering 10–20% of calls). Leave it for a few days.
3. **Review.** Open conversations where the "I used N glossary terms" event fired, and compare transcripts from before and after. Look for routing regressions, not just wording. On a reference build, a rewritten term once sent the next turn into the wrong playbook. Compare containment and AR by bucket.
4. **Make it live for everyone** by removing the availability rule, or roll it back by deleting the term.

Add terms one at a time, or in small related groups, so you can tell which term caused a change. Never bulk-import a CSV over an existing glossary, because it can drop terms that are already there.

> **Seen live:** one retailer has more store names than the 30 voice slots, many in te reo Māori. The plan was voice detection for the hardest names, non-voice terms for known mishearings, and pronunciations for all 47.

**To confirm:** the 30-term cap (it's confirmed in the product; 50 has also been quoted internally), that glossary isn't applied during variable extraction, and whether glossary terms will be added to changesets.

## 12 · Texting the caller

Ada needs the caller's permission before texting them, and it now asks for it itself, both in the generative state and in the playbook Send SMS step. Your job is to choose where the text comes from, handle each outcome, and not add a second consent question. Texting is still a compliance matter for the customer, so confirm their requirements with their legal team.

### Inside a playbook: use the Send SMS step

A RUN step: pick **Send SMS** in the RUN picker and type the text. The message can include variables. Voice only: on chat it does nothing and the playbook carries on.

- **Consent is built in. Don't add your own question.** Before the first text, Ada asks "I'd like to send you a single, one-time text message. Do I have your consent to send this?" and waits on the step. A playbook that also asks "Want a text?" asks the caller twice.
- **Ada only asks when a text can go out:** a voice call, Agent SMS switched on, a caller number, and a non-empty message.
- **Asked once per conversation.** A caller who already answered the step's question isn't asked again. A yes to the CSAT or media text question, or a yes the AI agent recorded when it texted with its own SMS tool, also counts.
- **Skip the question when you already have a yes:** point the step's optional consent variable at a variable that holds yes. A no from the caller still wins.
- **Branch on the outcome:** the optional result variable gets `sent`, `declined` or `failed` (`failed` includes a caller who never answered). Use it to give a spoken version or an alternative when the text didn't go.
- **STOP line:** the first text in a conversation ends with "Text STOP to stop receiving SMS messages", in the caller's language.
- **Opt-out words:** a caller who replies `STOP`, `UNSUBSCRIBE`, `END`, `QUIT`, `STOPALL`, `CANCEL`, `REVOKE` or `OPTOUT` to a text from the agent's Twilio number is unsubscribed from later agent texts. Don't write a text that asks for a one-word reply from that list ("Reply CANCEL to cancel your booking"), because it unsubscribes the caller instead. With **Use your own SMS channel** on, those replies reach the customer's provider, not Ada, so their team must handle opt-outs. Source: docs.ada.cx, SMS consent and Voice onboarding.
- **Never breaks the flow:** flag off, no number, Agent SMS off or a provider error is logged and the playbook moves on, so branch on the result rather than assuming it sent.
- **Check the setting per bot:** the Send SMS step is off by default. Without it the step does nothing. On one build, before the step existed properly, a playbook said it had sent a text when it hadn't, again and again.
- **Don't put a spoken line straight after the step.** In simulations Ada spoke its own "Okay, I'll send that now", and the builder's next line was clipped to a single letter. Let the step's own confirmation stand, or put a question before your next line. (Observed in simulations, not documented; confirm on a real call.)

> **Example — Send SMS step in a playbook**
> - **ada:** You can track it any time from the link in your order email, or I can text it to you.
> - **sys:** RUN Send SMS "Track your order: {{tracking_link}}" · result → sms_result
> - **ada:** I'd like to send you a single, one-time text message. Do I have your consent to send this?
> - **caller:** Yes.
> - **sys:** sms_result = sent → next question

### Outside a playbook, and other ways to send

| Method | Use when | Consent | Watch out for |
|---|---|---|---|
| **Send SMS step** (default in playbooks) | A playbook sends a specific text at a set point | Built in | Per-bot setting; branch on the result variable |
| **The AI agent's own SMS tool** | Outside playbooks: self-serve links and steps the agent offers in conversation | Built in | You don't control the wording, and the agent sometimes leaves the URL out. Put the link in the knowledge article it answers from. |
| **Twilio Messaging API in an action** | Greetings and handoffs, which have no SMS step | Not built in. Ask first. | The number needs A2P registration; otherwise US carriers block the message while the action still reports success. Check the Twilio logs. |

### Rules

- **Say why before the text is offered.** "The link is easier to use on your phone" gets more yeses than an unexplained question.
- **Never say "I've texted you" before the result is `sent`.** If the caller says no, Ada has stated something false.
- **Plan for a no.** Give a short spoken version (two or three sentences), then an alternative: email if you have it, or a handoff if the task needs it.
- **Landlines and blocked numbers:** the text won't arrive. Ask "Are you calling from a mobile?" before relying on SMS, or check the line type with an API (Twilio Line Type Intelligence is about 90% accurate).
- **Turning SMS off** (Config › Channels › Voice › Configuration, "Allow AI Agent to send and receive SMS") stops every text, makes SMS capture speech-only, and turns off voice CSAT, which is sent by text.
- **Plan for replies and callbacks.** Callers may reply to the text or call the number back. See Callers will phone the SMS number.
- **Settle SMS early in scoping.** Number approval takes time, especially outside the US and Canada. Customers can use their own SMS provider where Twilio rates are too expensive.

**To confirm:** the spoken confirmation after consent and the clipped line after it.

## 13 · Metadata carries over for 24 hours

Metadata from one call is still there when the same number calls again within 24 hours. That's useful for repeat callers. It's dangerous when a critical variable carries over into a new conversation.

| Variable type | Risk if it carries over | Action |
|---|---|---|
| Auth flags (`verified`, `has_active_membership`) | Caller skips auth, or follows the wrong branch, based on the previous call | Null in greeting |
| Tokens, account IDs, lookup results | Actions run against stale or wrong data | Null in greeting |
| Resume checkpoints (`cancel_path_checkpoint`) | A new call resumes partway through the previous call's flow | Null in greeting |
| Retry counters, loop guards | Caller hits a retry limit they never used | Null in greeting |
| Test-number overrides | A real caller gets someone else's account or OTP | Remove before launch |
| Caller name, preferred language | Low risk | Reuse for repeat callers |

- **Clear critical variables at the top of the greeting.** The greeting runs once per call, so it's the one place that separates "new call" from "returning to the flow." Don't clear checkpoints at the top of a playbook, because they have to survive the caller leaving and coming back.
- **Make "returning within 24h" an explicit decision.** If you reuse context ("Are you calling back about your cancellation?"), check it on purpose. Don't let it carry over by accident.

> **Seen live:** a greeting rule that swapped a tester's number for another number was left on. A real verification SMS went to the wrong person.

## 14 · Callers will phone the SMS number

If Ada texts a caller, some of them will call that number back. Plan for it before launch. It matters most on SIP deployments.

- **On SIP, handoffs break.** The customer's contact center sends callers to Ada over SIP with metadata attached: the SIP or UUI headers and the contact ID. A call straight to the SMS number arrives over the public phone network (PSTN) with none of that. Handoffs and tickets that depend on it fail. Transferring the call back over SIP may not work at all.
- **Metrics and costs inflate.** These calls count as voice volume and incur telephony charges.

### Default: set the SMS number to take no calls

In Twilio, leave the SMS number's **voice configuration** empty, or point it at a short message, so it doesn't route calls into Ada. Configure only the messaging side. Do this when you set up the number, not after callers start dialing it.

- **Best:** no voice routing at all, so the number doesn't take calls.
- **If the customer wants callers redirected:** a short recorded message ("This number only sends texts. Please call 1-800-…") and nothing else.
- Check it after setup: call the SMS number and confirm it doesn't reach Ada.

### Other options, if the SMS line has to take calls

| Option | Trade-off |
|---|---|
| Detect the SMS number in the greeting and send the call through the main IVR, so it comes back to Ada with full metadata | Better for the caller. Two calls per contact, so more volume and cost. One build works this way today, and it's inefficient. |
| Handle the call fully in Ada, with a handoff that doesn't need contact center IDs | Needs a handoff path that works without those IDs. |

## 15 · Good containment vs bad containment

Containment counts every call that didn't reach a human. Some of those are callers who gave up. Report and optimize for the good kind.

|  | Looks like | How to spot it |
|---|---|---|
| Good | Question answered, task done, self-serve link sent and confirmed | Automated resolution, CSAT, no repeat call from the number within 24 hours |
| Bad | Caller hung up during dead air, after a loop, mid-auth, or after the silence timeout | Hang-up straight after a long turn, ended on silence timeout, repeat call within 24 hours, no engaged turns |

- Don't raise containment by making the handoff harder to reach. That turns transfers into hang-ups.
- Report containment alongside automated resolution. If containment rises and AR doesn't, the gain is probably hang-ups.

## 16 · Get ahead of it with the customer

Settle these during scoping, before any build work.

### Formats that don't work well on voice

- Email addresses, alphanumeric codes and order IDs with letters. Prefer numeric identifiers: they capture well by speech, keypad or SMS.
- Long step-by-step instructions, URLs, tables, and menus with more than three options.
- Unusual brand, product or place names. Collect a pronunciation list up front.
- Anything that needs the caller to look at something (a card, a text) without time to do it. The max caller silence is 30 seconds.

### What the customer needs to provide

- [ ] An auth method that verifies 80%+ of callers, and its real match rate
- [ ] APIs that cover the whole journey, not just one step. Cancel without refund still sends callers to an agent on one build.
- [ ] A caller ID lookup the customer's legal team has approved for personalization
- [ ] SMS number approval (it takes time, especially outside the US/CA), or a decision to run without SMS
- [ ] Telephony platform and transfer method (SIP or PSTN), plus how context reaches the human agent (SIP header, ticket ID)
- [ ] Business hours, holidays, and whether voice runs 24/7
- [ ] Test accounts that can safely be put through every flow (cancel, pause, refund)

### Set expectations

Phone callers expect a human and often call because self-service already failed. Containment targets on voice should start lower than chat. Background noise, accents and phone-line audio also limit transcription.

## 17 · Before launch

- [ ] Browser testing ("Test AI Agent") shows the caller ID as `client:webrtc-caller`. Swap in a test number for lookups.
- [ ] Any test-number routing in the greeting is removed or limited to known testers
- [ ] Every greeting request has an edited, silent error fallback
- [ ] Critical variables, including resume checkpoints, are cleared in the greeting
- [ ] Each flow resumes correctly after an unrelated question forces it to exit
- [ ] The SMS number's Twilio voice configuration doesn't route calls (test it by calling the number)
- [ ] Max caller silence and long-silence wording are set and tested
- [ ] Each handoff is tested end to end, including the context the human agent sees
- [ ] You listened to recordings, not just transcripts
- [ ] Simulations cover the unverified path of every auth-gated playbook

**Next sections to add:** telephony setup by platform (Genesys, Five9, CXone, Dialpad, Amazon Connect, Aircall), multilingual and dialect setup, and voice proactive outreach.
