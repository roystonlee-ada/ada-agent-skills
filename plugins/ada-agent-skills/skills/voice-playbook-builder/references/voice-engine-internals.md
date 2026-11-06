# The voice engine — internals

The detail behind the table in `voice-engine.md`. Open this while debugging a call the table doesn't explain; you don't
need it to design or build.

## The backtrack detector — how it works and what to design for

How it behaves: it is on for every client. The only off-switch is client-wide and off by default, so design for it. There is no
per-playbook or per-step switch.

**When it runs.** On every reply to a non-silent extraction (an `ask`) once anything has been answered, as a second LLM call in
parallel with the extractor. Silent SETs never trigger it. If it says "correction", the extractor's result is discarded.

**What it can jump back to.** A filtered list of earlier steps:
- earlier `ask` steps (answered, or asked and unanswered): **always eligible**
- silent SETs: only when the stored value appears word-for-word in one of the caller's messages ("grounding": token match;
  `true/false/yes/no/y/n/0/1/unknown` never match; digit strings of 6+ match across spacing)
- exact SETs and actions: never

Grounding narrows the list. It doesn't trigger a jump: the model still has to judge that the caller is correcting that step.

**What happens on a jump.** Every answer written by an
extraction from the target onward (asks and silent-SET extractions) is **cleared to an empty string `""`** — not `NONE`, not null.
Exact SETs and action outputs are not tracked, so they survive: a checkpoint or done-flag written by an exact SET is still there
after the jump. Then the flow resumes from the target and **re-runs every later step in order — sends, exact SETs and actions
included**. With a corrected value it is written and the flow resumes after the target; without one, the target question is re-asked.
Right after a jump, interpretive extraction is skipped once (synthetic `did_not_answer`), so the next questions are asked again
even if the caller already answered them. A correction aimed at a parent playbook pops out of the child.
Guards: max 3 honoured jumps per target step per run; a "correction" equal to the stored value is dropped; a corrected value the
caller didn't say is never written.

**Using it on purpose.** A caller who is a step or two past a question can change their answer ("actually my ZIP is 90210") and
the engine handles it — no step needed, and no way to force it. The caller must say it while answering an `ask`.

**Design rules**
| Rule | Why |
|---|---|
| Collect anything a caller may want to change with an `ask` | asks are always eligible; silent SETs mostly aren't |
| Store silent-SET values as tokens no caller would say (`SEL_ALL`, `PATH_CANCEL`, not `ALL`, `cancel`) | keeps bookkeeping off the eligible list |
| No two asks whose answers overlap (selection → a confirm that invites restating the selection) | a restatement reads as a correction |
| Every ask says how to treat replies aimed at an earlier step | the only lever on the model's judgement |
| Irreversible actions only after a final explicit confirm, with nothing editable after it | a jump re-runs intermediate steps, actions included |
| Actions between asks must be safe to re-run (reads yes, writes no), or guarded by a done-flag | same reason |
| Read back corrected values on voice | confirms the jump, and corrections get misheard |

**Seeing it.** In the transcript: the `playbook_v2_step` entry's output carries `"status": "backtrack"` with the model's reason, and
the cleared variables show `variable_set` to `''`. On a reference build this was rare. One case was cancel
v2: "I want my membership canceled" at the anything-else question sent the flow back to the confirmation.

**What follows for the build**
- Treat `""` as unset after anything a caller can correct: `is null OR is "" OR is "NONE"`. `is not NONE` passes on `""`.
- Guard every irreversible action with a done-flag set by an exact SET right after it, checked by an IF right before it. The flag
  survives the jump; without it a backtrack from a later ask re-fires the action (`ONCE` in `patterns.md`).
- Backtracking only works inside a run that's still active. It does nothing for a caller who left the flow and comes back — see
  "Leaving and re-entering a flow" below.

## Leaving and re-entering a flow

The behaviour that costs the most on voice. There are three ways out of a run, and each comes back differently
(how the engine handles exit and suspend):

| How the caller leaves | What the engine keeps | How they get back |
|---|---|---|
| **Off-topic reply** at an ask (`intent_change` / `topic_change`, after the first re-ask) with the default `on_off_topic: exit_playbook` | **Suspend**: run state kept, the general agent answers the side question | On later turns the reasoner gets a `continue_playbook` tool (resume / dismiss) and a prompt to offer resuming "when natural". Resume lands on the same question. It is the model's choice, not guaranteed |
| **Run ends**: complete, `exit`, a handoff (even a failed one), an action error, a human request with `exit_playbook` | **Nothing**: state is cleared | The next trigger starts from step 1. Only your own checkpoint variable can send the caller back to their question |
| **Correction** inside an active run | the run, minus cleared answers | Backtrack (above). Not a re-entry mechanism |

**What actually happens on a reference build** (live calls through cancel v2 and the auth child): **most off-topic events never
came back to the playbook**, almost all in the auth child. Another playbook took the next turn, and many of those calls ended in a
handoff. A few picked up at the same question, and a few restarted from step 1. So the costly failure is not "starts over",
it's "never returns".

**The deviation settings only take effect where the client's switches are on** (the setting is stored either way). With the combined flow controls on, all three settings act independently, at playbook and ask level. With only the older exit-behaviour switch on, ask-level overrides work and playbook-level settings fall back to the defaults. Both default off. Confirm with Ada support; the runtime file shows how to read each ask's resolved values.

**`on_off_topic: stay_in_playbook` does more than re-ask.** It keeps any answer that came with the side question, re-asks the
current question with a promise to come back to it, and stashes the side question. At the scope boundary — after this step when
set on the step ("let me finish this question"), or when the playbook ends when set at playbook level ("let me finish this flow")
— the engine suspends so the general agent answers the stashed question, then **resumes the remaining steps**. A human request
with `on_human_request: stay_in_playbook` is stashed the same way and outranks an off-topic stash.

**Design for re-entry**
- **Auth and data-capture asks: `stay_in_playbook` at step scope.** The side question is answered right after the step, and the
  caller stays in the flow. This targets the auth-child leak above. Untested live — prove it in sandbox with a sim that asks a
  billing question mid-auth.
- **Asks where another playbook should take over** (an offer the caller declines in favour of a different flow): keep
  `exit_playbook`. The suspend is the handover.
- **Every exit path: checkpoints.** Set a checkpoint before each ask and before any handoff or exit that can fail; the dispatcher
  after setup jumps straight to it. Clear it at the end and in the greeting.
- **General Guidelines:** say what "continue" means ("if the caller wants to carry on with their cancellation, resume it"), so
  `continue_playbook` gets called instead of a fresh trigger.

## Exact SET values: what writes

On the reference build, unquoted words write (`NONE`, `reason`, `selection`, `confirm` all appear in `variable_set`). Some
guidance says an unquoted word "parses as a name and writes nothing". Treat that as
instance-dependent: the setup check reports what the target instance does. Where it's unproven, inner-quote string literals
(`"value": "\"NONE\""`).

## Text-to-speech rules

- Plan names carry billing terms: "Tools Add-on 1 Months" is read "one Months". Strip the term for spoken names or instruct "speak plan names naturally, without any billing term".
- Never read ids, subscription numbers or confirmation references aloud. Say "it's in your confirmation email".
- Dates: instruct "speak the date naturally"; the model does this well. Prices: "twenty-five dollars", never "$25 each" unless two or more carry the fee.
- Lists: one short sentence per item so the engine pauses ("You have your All Access Membership. Your U.S. Discovery Membership. And your…").
- Don't double-acknowledge: the engine already acknowledges; a SEND that acknowledges again reads as a stutter.
- Digits captured by voice: the ask's `voice.confirmation_style` (`implicit`/`echo`/`spell`) matters most for codes, emails and names.

## What the bot sets before your playbook runs

The call-start greeting process sets variables your rules and gates depend on: channel, `phone_online`
(agents available), dev/rollout flags, sometimes a verification-attempted flag. Read a few real
transcripts (`variable_set` entries before the first user message) before assuming a variable is yours to set.
In simulations these differ from real calls (no telephony context), which is why sims can't authenticate.

## Knowledge search on multilingual bots

On the default retrieval path, the engine picks the search language by counting enabled articles tagged in the chat's language:
zero means it searches English, one or more means it searches only that language. Enabling a single article in a new language
can make knowledge answers vanish for that language overnight (a knowledge search returns nothing). Before a voice launch in a
second language, check its article count; English-variant locales (en_CA, en_GB, en_AU) are separate tags. This is the default retrieval path's behaviour.

## Dashboard step numbering

The dashboard numbers every row in a section depth-first, including rows inside IF branches and the ELSE
rows themselves. API/export order is top-level only. When someone quotes "step 6.4", map it with the
dashboard's own GO TO labels ("GO TO 8.26 SET pause_months") before arguing about what it does.
