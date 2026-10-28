---
name: ada-report
description: >
  Create an Ada-branded report on how an Ada AI Agent is performing, built from
  real conversations and metrics, and interview the person first if they have not
  said what they want in it. Use it for "make me a report", "how is the agent
  doing", "monthly or quarterly review", "what are customers asking about", "show
  my boss the results", "an EBR or business review", "summarise last month", or
  any request to show an Ada agent's results to someone, even if they never say
  "report". The report draws real chat transcripts and quietly shows how Ada
  works (playbooks, actions, knowledge, handoffs) where the conversation used
  it. Do not use it to diagnose one conversation (diagnose-conversation) or to
  design a new use case (design-conversation).
---

# Ada report

The reader is a stakeholder who has not opened the dashboard. They want to know
what happened, what it means and what to do next. The report shows results from
real conversations, and it teaches how Ada works by pointing at Ada doing it, so
the reader learns the product from their own customers' chats.

## 0. Pick the runtime

Each step names what to do, not a command. Read one file for how:
- Ada MCP tools present (`get_ada_metric`, `get_conversations`) → `references/runtime-mcp.md`
- `adacli` on the path → `references/runtime-cli.md`

## 1. Scope the report

If the ask already names the audience, the period and what to focus on, skip to
section 2. Otherwise interview with `references/interview.md`: one batch of at
most three questions, each with choices and a recommended default. Ask about the
reader's decision, not about data fields.

When no person is available to answer, take the defaults, say so in the report
footer and write the file. Do not wait.

## 2. Pull the evidence

Read in one batch, then read three to five conversations in full:
- Headline metrics for the period and for the equal period before it.
- Topic volumes with how each topic resolves.
- Conversations to quote: one that went well, one that shows the next
  opportunity, one handoff when the report is about handoffs.

Rules for numbers:
- Use *automated resolution* as the headline. Containment counts every chat that
  was not handed off, including ones the customer abandoned, so it flatters.
  Show containment only beside resolution.
- Quote a number only from a pull you read. Compute a change against the prior
  period only when both pulls succeeded.
- A zero from a metrics call is unverified until a second source agrees.
- Name the period and the channels in the report, so nobody compares unlike
  periods.

## 3. Choose the story

A report has a point of view, not a tour of every number.
- **Headline:** one sentence that states the result and the next win.
- **Metrics:** three to six cards, each with what it counts in plain words.
- **Charts:** one or two. Topics by volume is the default. Add a trend only when
  the direction matters to the point.
- **Transcripts:** two to four, from real conversations, each with why it is
  shown. See section 4.
- **Opportunities:** rank by volume times gap. Push toward more end-to-end
  resolution (playbooks and actions), not only more deflection.
- Name a gap as an opportunity ("Ada resolves 21% of order changes today"), never
  as blame. A reader who feels blamed stops reading.

## 4. Show Ada at work

Transcripts are the strongest teaching tool, so draw them as chat bubbles and
mark the moments where Ada did something worth understanding. Follow
`references/ada-in-action.md` for which moment maps to which note. The rules:

- Attach a note only where the conversation really shows the feature. Read the
  events in the transcript. Never add a note for a feature you assume was used.
- Keep it subtle. At most one note per transcript turn, at most four distinct
  features in the whole report, and none above the headline. The note is a small
  line under the reply that opens on click.
- Say what Ada did and why it helps the customer, in the reader's words. Use the
  copy in `references/tips.json`. Do not name internal fields, ids, or models.
- Pair a note with a next step when it points at an opportunity.
- Quote conversations exactly. Do not tidy a reply, because the reader may open
  the same chat in the dashboard. The script masks emails, phone numbers and long
  digit runs. Also remove names and order numbers that identify a person.

## 5. Build

Write the report as a JSON spec (`references/report-spec.md`, working example in
`references/example-spec.json`), then render it:

```
python3 "${CLAUDE_SKILL_DIR}/scripts/report.py" <spec.json> --open
```

The script writes one self-contained HTML file in Ada's brand (light, flat,
Almost White and Dark Charcoal with Lakeside as the one accent) to
`ada-reports/<title>.html`, and prints its path. It prints a `warning:` line for
each problem: a missing field, too many notes, an internal term, blame wording.
Fix every warning and run it again. A report with a warning is not ready.

## 6. Check and hand over

- Reread each number against the pull it came from.
- Open the page, check the transcripts read as the customer saw them, and open
  one note.
- Tell the person the file path, the period and channels used, and any
  assumption you made. Offer one next step, such as "turn the top opportunity
  into a design for review" (design-conversation).
- For a PDF, tell them to print the page from the browser. The print layout
  hides the notes.
- The report holds customer conversations. Do not publish or send it anywhere
  without the person asking, and never to a public page.
