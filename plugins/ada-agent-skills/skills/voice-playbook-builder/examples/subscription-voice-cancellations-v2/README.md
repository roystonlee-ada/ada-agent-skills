# Subscription business - Voice Membership Cancellations (v2)

Shipped to real callers behind a dev/rollout gate. Two builds: a 10-day iterative first build that became unmaintainable, then a
two-day rebuild around one deterministic categorizer and silent loops. This folder documents the rebuild.

## What it does
A verified caller hears their memberships, picks which to cancel, is offered a discount transfer and a pause
once for the whole set, hears the fee and any add-on cascade before confirming, and gets one definitive summary
with real end dates. Unverified callers or accounts with nothing active get a short self-serve fallback.
Already-cancelled memberships are reported as such, never re-cancelled.

## Section map (prod, 13 sections / 150 steps)
| # | Section | Purpose | Talks? |
|---|---|---|---|
| 1 | Authenticate | RUN auth child; not verified → self-serve | child does |
| 2 | Setup | greet or "picking up where we left off"; token once; checkpoint dispatcher | 1 line |
| 3 | Look up | billing API lookup → worklist/menu/state; pending-only → §11; no active → §13 | no |
| 4 | Reason | one ask; silent reason code; silent skip-saves flag (bereavement, "no offers") | 1 ask |
| 5 | Which memberships → Categorize | menu ask (or ALL for one); exact ack; **one categorizer call**; partial add-on → transfer | 1 ask + 1 line |
| 6 | Save offers | discount ask (gated: agents online, eligible, not skipping); pause: exact terms + short ask; non-pausable ask; **re-categorize** | ≤3 asks |
| 7 | Confirm | cascade note (exact) → confirm ask with fee text → proceed only on explicit yes | 1–2 lines + 1 ask |
| 8 | Do the work | exact filler; token refresh; cancel loop (sentinel → prep → sentinel → place); pause loop | 1 line |
| 9 | Say it once | one summary from the result lists | 1 |
| 10 | Anything else + goodbye | ask (always) → exit | 1 ask |
| 11 | Already set to cancel | names + access-through dates; never re-cancel | 1 |
| 12 | Human handoff | exact line → RUN handoff → exit | 1 |
| 13 | Self-serve fallback | two exact scripts (no active / not verified) | 1 |

## Design decisions
- **One categorizer, called twice.** After selection with pause=false; after the pause decision with pause=true. Everything downstream reads its lists. Why: loop collapse and three disagreeing rule engines in the first build.
- **Silent loops, results inside the picker.** `Next SID + record last result` returns the next id or DONE and appends `name~endDate~confirmation` to `cancel_results`. Why: SET accumulators collapse in voice.
- **Fee disclosed inside the confirm ask, cascade explained in an exact note before it.** Why: an LLM ask skipped the explanation on a real call and then retracted the add-on when asked why.
- **Explicit-yes gate** (`is null OR is not "yes"` → leave unchanged). Why: a "No" saved as `false` cancelled a membership in a probe.
- **Sentinel 599 before prep and before place; any 2xx passes; pause accepts 200/201/202/204.** Why: transport failures inherit the previous 200; the async pause code was unknown until a real call (it is 200).
- **Checkpoint before every transfer that can fail**; partial-add-on branch resets to `selection`, discount-yes to `pause`. Why: a stale `confirm` checkpoint cancelled a base the flow had refused.
- **No pause offer when the only pausable rows are add-ons whose bases are all going.** Why: the offer could not be honoured.
- **Add-on rule (from the business owner):** unsure which base an add-on belongs to → transfer; single base or all bases cancelled → cascade.

## Must-say texts (exact)
- Filler: "Great — please give me a moment while I take care of that for you."
- Post-selection ack: "Okay, give me just a moment to get that ready for you."
- Cascade note: "Just so you know — since your {{cat_addon_names}} is an add-on to that membership and can't continue on its own, I'll be cancelling it as well."
- Pause terms (one): "Before I cancel — instead of cancelling, I could pause this membership for up to two months. The pause is free. It simply delays your next renewal payment, starting at the end of your current billing cycle, and your membership picks back up on its own afterwards."
- Partial add-on transfer: "Because you're keeping one of your memberships, I can't tell on my end which one your add-on belongs to — so rather than guess, I'll connect you with a specialist who can take care of this for you. Transferring you now."
- Discount ask must end, verbatim: "Would you like me to connect you with an agent to explore your options?" (yes = connect). Never rephrased.

## Logic modules
`logic/categorize.js` — see file header for the contract. Row schema in `fixtures.md`.

## Checkpoints and re-entry
`cancel_path_checkpoint` ∈ reason | selection | discount | pause | nonpausable | confirm | NONE. Setup's dispatcher is one else-if tree after the token step. Set before the ask it names, and before any handoff.

## Testing
A voice sim suite (fixtures injected via a meta variable), chat probes per change, real payloads through the lookup JMESPath, categorizer runs over real worklists, then real calls: one cancel, one pause, one discount transfer on test accounts. Grader gotchas in `references/testing.md` came from this suite.

## What the first live calls showed
Most callers never verified: the phone-number search found no account, and callers who repeated the same number got nowhere. A few timed out while entering a code. Of the verified callers, some were cancelled by the playbook, some accepted the discount transfer, one held a subscription that the billing API called active but whose renewal date was long past (prep returned 422, so the caller was transferred), and some had no active membership. A large share of calls ended in a transfer. Every billing API call did what it should; the losses came before the flow (verification) and from the fallback wording.
Changes proposed after: exact up-front ack ("I can cancel that on this call"), short choice-based fallback, fallback keyed on portfolio state, loop guard on "can't get online", skip saves for billing disputes, never state refund outcomes.

## Engine findings from a later reread
- **The early "engine rewind" is the backtrack detector.** "I'd rather pause" at the discount ask and "keep the add-on" at the confirm
  were read as corrections to the selection ask; the engine jumped back and cleared everything after it. Our mitigations (each ask
  says what to do with replies aimed at an earlier step; the discount ask repeats one fixed sentence) are the right ones. Still to do:
  `cancel_selection` stores `ALL` — a word a caller says — so if it is ever written by a silent SET, store `SEL_ALL` instead.
- **Rule 4 holds here** because the client has action status-code output on: a real 400 kept the playbook stepping.
  On a client without it, every failure branch in this build would be skipped by a forced handoff.
- **Unquoted exact SETs write on this instance** (`NONE`, `reason`, `selection`, `confirm` all appear in `variable_set`), contrary to
  some guidance that says they write nothing.
- **Off-topic replies are leaking in the auth child**, not in this playbook: "why did you charge me?" at the ZIP ask → `intent_change`
  → suspend → most off-topic events never returned to the playbook, and many ended in a handoff. Candidate
  fix: `on_off_topic: stay_in_playbook` at step scope on the auth asks (untested live).
- **Backtracking is live here:** "I want my membership canceled" at the anything-else ask jumped back to the confirm. There's no
  done flag. A re-run can't cancel more than the caller confirmed: the loop only works through the
  confirmed list, and the billing API returned 422 `NON_ACTIVE_SUB` for a membership that wasn't active. A second cancel on one
  that's already set to cancel hasn't been tested; if the billing API refuses it, the caller hears the "couldn't fully complete"
  line and is transferred after a cancel that worked.

## Open items
Zombie subscriptions (a data fix on the customer's side); continue past a failed membership; duplicate plan names; TTS "1 Months"; reason text occasionally stored without spaces; second categorize call has no status check.
