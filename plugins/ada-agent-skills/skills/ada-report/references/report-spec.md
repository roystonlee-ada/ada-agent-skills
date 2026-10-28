# Report spec

The JSON that `scripts/report.py` renders. `example-spec.json` is a complete
working spec: copy it and replace the content.

## Contents
- Top level
- Metrics
- Sections
- Transcripts
- Limits the script warns about

## Top level

| Key | Required | Notes |
|---|---|---|
| `title` | yes | Also the file name. Sentence case |
| `customer` | yes | Shown in the header |
| `period` | yes | Say the dates, for example "1 to 31 October 2026" |
| `headline` | yes | One sentence: the result and the next win |
| `lead` | no | Two or three sentences under the headline. `*word*` makes italics |
| `metrics` | yes | 3 to 6 |
| `sections` | yes | In reading order |
| `next_steps` | no | Short list, last on the page |
| `footer` | no | Defaults to "Prepared for <customer> · <period>". Put assumptions here |

## Metrics

`{"label", "value", "delta", "good", "note"}`. `delta` is text such as "+4 pts".
`good` is `true` (green), `false` (amber) or omitted (grey). `note` says what the
number counts, in plain words.

## Sections

Each section has a `title` and any of these parts, rendered in this order:

- `intro`: one or two sentences.
- `chart`: `{"type": "bars", "title", "unit", "rows": [{"label", "value", "note"}]}`
  or `{"type": "line", "title", "unit", "points": [{"label", "value"}]}`. Two rows
  or more.
- `bullets`: list of strings.
- `transcripts`: list of transcripts, below.
- `opportunities`: `[{"title", "why", "effort", "tip"}]`. `why` holds the evidence
  and is required. `effort` is "Low", "Medium" or "High". `tip` is a tip id.
- `tip`: a tip id shown as a note at the end of the section.

## Transcripts

```json
{"title": "Where is my order?",
 "outcome": "Resolved by Ada",
 "why_shown": "Shows a lookup answered with the customer's own order data.",
 "channel": "Web chat",
 "url": "optional dashboard link",
 "turns": [
   {"who": "customer", "text": "..."},
   {"who": "bot", "text": "...", "options": ["Yes", "No"],
    "image": "optional description of a photo the customer sent",
    "moment": {"label": "Checked the order in your system", "tip": "action"}}
 ]}
```

`moment` goes on a bot turn only. Tip ids and when to use each are in
`ada-in-action.md`. The copy is in `tips.json`.

## Limits the script warns about

- Fewer than 3 or more than 6 metrics.
- More than 4 transcripts, or more than 4 distinct tips.
- A chart with fewer than 2 rows, an opportunity with no `why`, a transcript with
  no `outcome` or `why_shown`.
- An unknown tip id.
- An internal term in visible text (for example "LLM", "prompt", "endpoint").
- Blame wording ("failed", "broken", "bad", "poor", "wrong").
- A bot turn with more than one question mark. Check the quote is exact.

The script also masks emails, phone numbers and long digit runs in transcript
text and says how many it masked.
