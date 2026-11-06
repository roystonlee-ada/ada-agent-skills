# Subscription business - email capture fallback in voice auth

**Status:** live, inside the modular voice auth child, section Membership Identification.
A pattern example, not a whole build: one capture step added to a live flow and reviewed on real callers.
No sections file here — the playbook is co-edited in the dashboard; export it fresh before changing anything.

## What it does
When the caller's phone number finds no account, Ada asks them to spell the email on the account (or text it), looks the
member up by email, and continues auth from there instead of asking for another phone number.

## The step
- Trigger: first phone-search miss (`account_search_count` → 1) and `email_cap_rollout == "A"` (A/B variable; B = ask for another
  10-digit phone; B was dropped quickly).
- `SET email_search = True` → `ask email_to_verify` with `voice.capture_modes: conversation + sms`, `confirmation_style: spell` →
  RUN the email version of the member search → loop back to the account checks.
- SMS replies arrive as a `user_message` starting `sms:`; the playbook strips the prefix, so the saved variable can't tell spoken
  from texted. Measure the split from transcripts.

## The live ask
Instruction: *Ask "To help me find your account, can you spell out your email address?". This is an email address and will need to be
stored in the format of an email address (name, at sign, domain). If an input starts with "sms" or "sms:", do not include this
in the saved variable, that is a backend indicator that this input is sent via sms and is not part of the email address. If the customer
explicitly asks for a human agent, set to HANDOFF_REQUESTED. If the customer cannot provide a valid email after 2 attempts or refuses,
set to NONE.*
Settings: `when_to_ask: always`, capture `conversation` + `sms`, `confirmation_style: spell`. Not set: `fallback_value`,
`max_reask_attempts`, `on_off_topic` (worth setting in the next revision).

## What changed for phone-miss callers
- Verification for callers whose number found no account rose several-fold once the email step existed. Containment did not move noticeably.
- The loss now sits **after** the lookup, at the second factor.
- Many of the callers who verified did so by ZIP plus last-4 of the card rather than by code, because MFA was disabled or the email matched more than one account.
- On the ZIP path, callers dropped between giving a ZIP and giving a card. Some runs called the verify action with a blank
  last-4 (a 400). Few callers refused outright. After a ZIP mismatch the playbook exits silently, with no retry.
- A small audit of mismatches found no transcription errors. The commonest cause was an email that matched an account with **no
  memberships** (often trial callers). Others were callers unsure of their card, or likely the wrong one of several accounts.
- Texted emails did not verify better than spoken ones.

## Lessons (each now a rule in the skill)
- **Guard every captured value before the action that uses it.** Some email lookups returned 422; every audited one ran with a
  BLANK email (the ask ended unset; the playbook only checked `HANDOFF_REQUESTED`/`NONE`). Same bug on the card digits (blank
  runs happened, plus "I don't know" → `unable_to_provide` → verify ran anyway). → `GUARD_VALUE` in `patterns.md`: never call an action
  with a value the caller didn't give.
- **`HANDOFF_REQUESTED` is not data.** Accepting a handoff inside the email ask spelled "HANDOFF_REQUESTED" back to the caller as
  their email.
- **The parent playbook can exit mid-ask** after the caller gives the email (off-topic handling) → decide `on_off_topic` per ask.
- **Copy that assumes a path goes stale.** The email-miss and cancel v2 self-serve lines still say "based on your phone number"
  after the email path.
- **Fix the second factor next.** Retry once after a ZIP mismatch; a zero-membership account should get "I don't see an active
  membership on that account", not a verification failure.
- **Security:** in one call, Membership Details said "verification is complete" and read memberships after a
  FAILED ZIP/card check. Every auth-gated playbook must branch on the verified flag itself, never on "auth ran".

## Measuring it
Search voice conversations where the `email_search` variable is True (the runtime file has the search command), then read the
transcripts and count `user_message` text matching `^sms:` for the spoken/texted split. Filter gotchas: `error_fallback = True`
is set by ANY later auth failure, so it can't measure lookup errors (use the action's behaviour profile); `accounts_found`
values are floats (`"0.0"`, use BEGINSWITH) and later playbooks can overwrite them.

Variables: `email_cap_rollout`, `email_search`, `email_to_verify`, `account_search_count`, `accounts_found`, `error_fallback`, `mfaVerified`.
