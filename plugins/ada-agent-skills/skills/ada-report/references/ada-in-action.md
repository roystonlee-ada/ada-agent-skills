# Ada in action: which note goes where

Each note is a tip id from `tips.json`. The copy lives there, so edit it once.
Attach a note only when the transcript shows the signal. Read the signal from the
conversation's events, not from your guess about the setup.

## Contents
- Signal to note
- Writing the moment label
- Notes on opportunities
- What not to do

## Signal to note

| What the transcript shows | Tip id | Moment label (one short line) |
|---|---|---|
| A knowledge search, then a reply built from the article it found | `knowledge` | "Answered from your <topic> article" |
| A playbook starts and the agent follows its steps | `playbook` | "Followed your <task> steps" |
| An action runs and its result appears in the reply | `action` | "Checked <thing> in your system" |
| A handoff event, with collected details passed along | `handoff` | "Passed to a person with the details" |
| A coaching item was applied to the reply | `coaching` | "Applied coaching you added" |
| A standing instruction shaped the tone or a limit | `guidance` | "Followed your standing rule on <subject>" |
| The customer sent an image and the reply used what it showed | `image` | "Read the photo the customer sent" |
| A code tool ran and its value appears in the reply | `code-tool` | "Worked out <value> for the customer" |
| A custom metric verdict is on the conversation | `custom-metric` | "Scored against your <metric name> measure" |
| A topic label is the point of a chart | `topics` | Use on the section, not a turn |

## Writing the moment label

- Describe what Ada did, in the customer's world: "Checked the order in your
  system", not "Called an action".
- Under 8 words. Sentence case. No ids, tool names or model names.
- Name the business thing (the article, the system, the task) the way the reader
  does.

## Notes on opportunities

An opportunity card takes a `tip` when the next step is a feature the reader has
not used yet. The tip answers "what is this, and why would I want it", and the
card text gives the evidence. Pick the tip that is the *fix*, such as `action`
for "customers wait for a person to send a label".

## What not to do

- Do not add a note to every bot turn. Pick the turn where the feature does the
  work.
- Do not add a note for a feature the transcript does not show, even if the agent
  has it configured.
- Do not use more than four distinct tips. The script warns at five.
- Do not turn the note into a sales line. State what it is and why it helps. The
  reader decides.
