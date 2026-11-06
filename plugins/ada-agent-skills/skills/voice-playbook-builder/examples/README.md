# Examples — shipped voice builds

Start every new build here. Find the closest shipped flow, read its README, copy its shape, then diverge.
A build earns a folder once it is working well for real callers. Nothing made up: every section map, wording and number
comes from the live build, and live findings are added as they come in. Findings are written as lessons, never as measured call counts or rates. Best practices in the reference files are pulled from
these folders; when an example contradicts a reference, the example is newer — fix the reference.

## What to include (one folder per build)

```
examples/<bot>-<flow>-<version>/
├── README.md          what it does · section map · design decisions · must-say texts · what went wrong live
├── sections.json      the shipped sections, ids masked (optional; the README's section map is the minimum)
├── logic/*.js         EvalJS modules with their input/output contract
├── fixtures.md        the row schema + every real-shape fixture (ids masked)
├── sims.json          the test cases (first line, caller goal, criteria, variables)
└── findings.md        what went wrong in the first live calls and what changed, as plain lessons
```

The reference builds tested with meta-variable-gated fixtures inside the playbook. That's one way. Any method works as long
as it leaves the live build untouched and sims can still run (`references/testing.md` §2).

Mask account ids and phone numbers, name no customer, and publish no measured call counts or rates. Never paste conversation ids or customer transcripts.

## How best practices get extracted

Each reference file cites the example it came from. When you add a build, add one line per lesson to the
matching reference and link the folder. If a lesson is new, add it; if it contradicts an old one, replace it.

| Build | Channel | Shape | Proven live |
|---|---|---|---|
| `subscription-voice-cancellations-v2` | Voice | auth child → lookup → one categorizer → offers → confirm → silent cancel/pause loops → one summary | Yes: real cancels, pause and transfers |
| `subscription-voice-email-capture` | Voice | one capture step added to a live auth flow: phone miss → spell or text the email → lookup by email → continue auth | Yes: every phone miss; verification rose several-fold |
