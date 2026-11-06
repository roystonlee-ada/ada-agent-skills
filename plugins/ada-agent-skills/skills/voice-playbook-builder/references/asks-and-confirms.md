# Writing asks, confirmations, offers and fallbacks

The ask's shape is in `patterns.md`. The checklist §4–6 says which settings every ask needs: accepted values, fallback,
re-ask cap, `when_to_ask`, deviation settings, capture mode, read-back. This file is about the words.

## The instruction
- Describe what to extract and how to phrase the question, not the verbatim question. If it must be verbatim, say "Ask
  exactly: …" and forbid rephrasing. Prefer `contextual` + "Ask exactly" over `exact_words`: `exact_words` has no reasoning
  for unexpected replies, and playbooks built mostly from `exact_words` numbered menus resolve about 15 points less often.
- **`exact_words` doesn't fill in `{{ variable }}`.** The token reaches the caller raw. To ask about a live value, put it in an
  exact `send` first, then a short `ask`.
- **Say what a reply aimed at an earlier question means here.** ("If the caller says they'd rather pause, capture `no`.")
  Otherwise the engine may read it as a correction, jump back and clear later answers (`voice-engine.md`).
- **Say that a partial answer is still an answer.** "I don't have it" writes the fallback at once with no re-ask, and a caller
  spelling an email over three turns can be misread as giving up. Add: "A reply that adds more of the answer is still
  answering; it is unavailable only if the caller clearly says so."
- **An exact reply skips the instruction.** A bare "yes" that matches an accepted value is saved without reading your rules,
  so a rule like "yes here means they want the discount" never applies. Make the accepted values themselves unambiguous.
- **Inside a loop, capture only the latest reply:** "Capture ONLY the value in the customer's most recent reply; do not reuse
  a value given earlier." The extractor reads the whole transcript by default.
- Values the caller may volunteer up front (reference, last name, reason): `when_to_ask: only_when_needed`. Values they can't
  know yet (a code, this specific confirm): `always`.

## Confirming something irreversible
Shape in `patterns.md` (`CONFIRM_GATE`). The words:
- The fact the caller must hear (the fee, what else gets cancelled) is an exact `send` with the variable in it, placed right
  before the confirm. The confirm ask is told: "The caller was just told X; name it, don't re-explain it."
- A choice that changes what you do (one month or two) is its own ask, right before the confirm, and the confirm names the
  chosen value.
- On "why?" or "keep it", the confirm explains once and asks again. It never offers to drop part of the set or claims a mistake.
- Proceed only on an explicit yes. Every default path leaves things unchanged.

## Selection asks (which of several)
- Give the model a menu variable of `name: id (kind)` items. Ids are for mapping only, never spoken. Save comma-separated
  ids, `ALL`, `NONE` or `HANDOFF_REQUESTED`.
- State the business rules the model can't know ("add-ons go with their base when every base is cancelled"; "with two bases,
  never assume which one an add-on belongs to").
- Two items with the same name break everything above. Tell them apart with a date or price in the menu.
- Follow the ask with an exact acknowledgment line. Generative ones drift into claiming progress.

## Offers (retention, pause, discount)
- Gate on facts, not tone: eligibility from the logic module, agents online, and a skip flag for callers who shouldn't hear an offer
  (bereavement, "no offers", a disputed charge).
- Explain the terms in an exact `send`, then a short ask that says "don't repeat the explanation".
- Keep one fixed closing sentence, never rephrased ("Would you like me to connect you with an agent to explore your
  options?"). A rephrase inverted yes and no when the caller came back to it.
- Don't offer what can't be honoured (pausing an add-on whose base is being cancelled).
- If the offer needs a transfer, set the checkpoint to the step re-entry should land on before the handoff.

## Fallbacks
- Key the fallback on what you know: not verified → the self-serve answer; verified with nothing eligible → say so plainly and
  offer to check or transfer; already done (set to cancel) → say so with the date, never redo it.
- One line: what the caller can do and where (`AUTH_FALLBACK` in `patterns.md`). Offer to text the link when the answer is
  long. A read-only failure doesn't offer a transfer; a caller who asks still gets one. A five-step script sounds like "you
  can't help me".
- After the fallback, "it's not working online" goes to that choice, not back into the playbook.

## Handoff wording
- One exact line before the handoff: "I'll connect you with a specialist who can help — transferring you now."
- Give the receiving agent a note: what was tried, what failed, verified or not.
- Check with the bot owner what callers hear out of hours.
