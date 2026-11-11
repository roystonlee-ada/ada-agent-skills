# The ranked fix list

The report the person reads. Lead with the list, then the floor, then the
caveats. Dates as DD/MM/YYYY with the time zone.

## Header

```
Window: <DD/MM/YYYY> to <DD/MM/YYYY> (<time zone>), test users excluded.
Conversations N: <n>. Handed off H: <h> (<h/N>%). Containment: <c>%.
Verdicts: preventable <p> (<p/H>%), not preventable <q> (<q/H>%), unclear <u>.
Read pass: <k> transcripts, agreement with the record pass <a>%.
```

## The list

| # | Fix | Cause | Conversations affected | Replay (contained x of y) | Controls | Projected containment gain | Links |
|---|---|---|---|---|---|---|---|
| 1 | Plain name of the change, and its surface | The cause label | c, and c/H as a share of handoffs | x of y on the changeset, round r | resolution held k of k, handoff kept 1 of 1 | low to high points, with the arithmetic | changeset, cases, 2 or more conversations |

- **Conversations affected** is the cause's count over the whole window, not
  the sample.
- **Replay** names the changeset run. Write "not replayed" and the reason when
  step 7 did not run. Never fill it with a guess.
- **Projected containment gain** = 100 x c x r / N, from `improve-agent`
  `references/sizing.md`. With a replay, r runs from a low bound to x/y; use
  the lower bound of a 90% interval for x of y, or (x - 1)/y when y is under
  10. Without a replay, use the sizing defaults and mark them ASSUMED.
- **Links**: dashboard links, written as
  `https://<instance>.ada.support/insights/conversations/<id>`. Mark each
  opened or ASSUMED.

Rank by the midpoint of the projected gain. Gains from fixes that share
conversations do not add. Say which overlap.

## Discarded fixes

| Fix | Cause | Replay | Why discarded |
|---|---|---|---|

"Contained 1 of 5", "resolution control got worse", "must-still-hand-off
control stayed with the agent". Each keeps its case links.

## The floor

| Not preventable because | Conversations | Share of H | Top tasks |
|---|---|---|---|
| Customer asked for a person | | | |
| Policy needs a person | | | |
| Agent lacks system access | | | |

Name the largest system-access task and the API it would need. That is an
integration case, not a fix for this skill.

## Decisions for the person

One line each, with a recommendation and why: promote a kept changeset (hand
to `ada-promote-changeset`), confirm an OPEN policy fact, approve a
handoff-by-design change, or approve the writes a replay needs.
