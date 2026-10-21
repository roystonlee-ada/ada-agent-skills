# Writing metrics the judge can score

Read before you draft wording in `ada-custom-metrics-setup`.

## Contents

- Judge limits
- Wording rules
- Pitfalls seen in production
- Template

## Judge limits

The judge reads the transcript only: customer, AI agent and live agent messages.
It does not see tool calls, playbook steps, retrieved knowledge text, variables or
handoff events. A metric about "used the right knowledge" or "wrote a good handoff
summary" makes it guess from text. Rewrite such a metric around what the customer
could see, or check it another way, such as reading the reasoning log yourself.

## Wording rules

- **Pass on good behaviour.** Every metric passes when the agent did well, so a
  fail always means a defect. Mixed polarity breaks scorecards.
- **One behaviour per metric.** "Accurate and polite" gets two metrics, or neither.
- **Judge the AI agent only.** Say where the judgement stops, for example when a
  human agent joins.
- **Name the exemptions.** List what looks like a fail but is fine, such as
  repeating a question because the customer gave no usable answer, or reading
  details back to confirm them.
- **Give null a meaning.** Null means the metric does not apply, such as no handoff
  in a handoff-quality metric. A metric that is null on over half of chats needs a
  narrower scope (`intent_ids`).
- **Describe what is visible.** "The AI agent told the customer what happens next"
  is checkable. "The AI agent followed policy" is not.
- **Plain, concrete words.** No jargon, and no numbers the judge must compute.

## Pitfalls seen in production

| Pitfall | Effect | Fix |
|---|---|---|
| Name starts with "1." or "2." | Every metric on one voice agent scored false | Plain names, no numbering |
| Fail wording says "handed off" | The metric tracks containment by construction | Judge the timing or quality of the handoff, not its existence |
| Fail on any handoff | Penalises requests that need a person | Make a needed handoff null or pass |
| Weights not summing to 1.0 | Scorecard create returns a 400 | Equal weights, nudge one for rounding |
| More than 20 metrics | Create refused | Plan 8 to 12 and keep headroom |
| Edit to a metric made before the subject field existed | Authoring review fails | Pass `subject: ai_agent` |
| A metric that never fails or always fails | No signal | Rework the wording against the sample |

An edit applies only to chats that end after it. Earlier verdicts stay.

## Template

```
name:             Plain Title Case, no number prefix
pass_description: The AI agent <good behaviour, visible in the transcript>.
fail_description: The AI agent <the defect>, so the customer <consequence>.
null_description: <when the metric does not apply>.
scoring_guidance: Judge the AI agent only, and stop when a human agent joins.
                  <exemptions that look like fails but are fine>.
                  Fail only when <the narrow condition>.
```
