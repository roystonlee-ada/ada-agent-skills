# Map the flow and review weak nodes

Use this review in author-playbook, revise-playbook and test-and-fix. A graph
helps find paths a happy-path transcript misses. It does not prove how the
runtime will interpret an answer. Use the chosen runtime reference to read
configuration and traces; do not infer platform semantics from a diagram.

For each intent in the approved scope, also read
`references/intent-state-health.md` in author-playbook. Compare the intent's
required business states and transitions with the implemented graph, including
state hidden in guidance, knowledge, flags and prior turns. Save that coverage
overlay beside the graph. Apply the same check when entering from revise-playbook
or test-and-fix; inferred states do not become generated or exercised edges.

## 1. Save a graph with its source

Before authoring, map the approved design as a proposed graph. Before revising
or diagnosing a test failure, map the current persisted playbook. Label each
graph with the playbook identity, source revision or changeset, capture date,
channel, and whether it represents design, live configuration or a draft.
Keep design and runtime graphs separate. Use real step identifiers from the
export; for a proposed step use a clearly marked temporary identifier.

Save a readable Mermaid flowchart and the node and edge tables beside the
use case's existing work artifacts, in its approved storage location. The
diagram can group sections for readability, but the tables retain every step
and edge in scope. Do not put internal identifiers in customer-facing wording.

For a new playbook, map the whole use case. For an existing one, include the
entry, affected steps, all their possible continuations and exits, and the
writers and readers of variables they change. Include parent and child call
and return boundaries. Inspect the whole playbook for incoming paths; do not
cut the graph off at the reported ASK. Mark any omitted portion explicitly.
An inaccessible child, unknown condition or undocumented runtime transition
is OPEN, with the evidence needed to resolve it. Never draw an invented edge.

Node table:

| Step ID and type | Purpose and instruction source | Inputs and outputs | ASK contract | Side effect or exit |
| --- | --- | --- | --- | --- |
| Exported ID, section, ASK/SET/IF_ELSE/tool/call/etc. | Question or decision, source field | Variables read, written, reset; existing-value skip | Accepted values, mapping instructions, retries, fallback setting | Tool write, child, handoff, return or end |

For each ASK, distinguish an explicit fallback value from a runtime failure,
off-script routing, and a handoff. Record unset fields as unset, not as a
guessed default. Verify retry and fallback semantics from runtime evidence or
current platform documentation when they matter to the diagnosis.

Edge table:

| From | Condition or event | State change | To | Evidence |
| --- | --- | --- | --- | --- |
| Step ID | Accepted answer, invalid answer/retry, exhausted retry/fallback, skip, branch, error, call/return | Exact value or unset/unknown | Step ID or named boundary | Config field, documented behavior or trace turn |

Include implicit continuations as well as explicit IF_ELSE branches. Trace
fallback values through every downstream consumer, including the parent after
a child returns. A default branch is handling only if its resulting behavior
is appropriate for an unresolved answer. Check whether the same customer turn
can be consumed by successive ASKs rather than assuming each waits for a fresh
reply. If this is unknown, mark it OPEN and request a targeted trace.

## 2. Mark weak nodes and paths

Review each ASK together with its predecessors and downstream consumers:

- **Repeated question without progress.** Known state is ignored or cleared,
  the instruction cannot extract a usable indirect answer, the retry repeats
  the same wording, or a return/cycle asks for the same fact again. An
  intentional bounded clarification is healthy when it acknowledges the reply,
  asks for the missing detail and has a safe way out.
- **Fallback treated as an answer.** Retry exhaustion writes a normal business
  value, or an ELSE branch routes unknown/unset to a claim, lookup, purchase or
  handoff without checking intent and required inputs. An unresolved reply
  must not silently become consent or a confirmed intent.
- **Fallback without recovery.** The stored fallback has no suitable consumer,
  the next ASK assumes the previous answer was valid, or several ASKs cascade
  into fallback. A named fallback setting alone does not establish handling.
- **Ambiguous answer contract.** Accepted values overlap, instructions omit
  natural paraphrases or implicit negatives, two facts are requested but only
  one is captured, or the question and stored variable ask different things.
- **Loop or boundary gap.** A retry/call/return cycle has no evidenced progress
  condition or safe exit, a child overwrites parent state, or a tool failure
  returns to an ASK without preserving what the customer already supplied.

Write a risk register with step/edge IDs, triggering reply or state, evidence,
customer consequence, proposed treatment and linked test case. Label findings
as **CONFIRMED** only when a trace demonstrates the path, **SUSPECTED** when
configuration exposes a risk, or **OPEN** when necessary evidence is missing.
Classify each claim separately: suspected routing risk can coexist with OPEN
runtime semantics.
Also record reviewed safe recovery paths and why they are safe. Do not label
every retry or fallback weak, or call a platform bug from configuration alone.
Prioritize unintended writes or consent, wrong routing and repeated dead ends
over wording polish. Do not assign a numeric score without an agreed rubric.

## 3. Turn risks into checks within the approved scope

For affected ASK paths, link saved cases or propose missing cases covering:

- A direct valid answer and a usable indirect answer.
- A vague or partial reply, followed by a useful clarification answer.
- Repeated non-answer through the configured retry limit and its actual
  fallback, including the next customer-visible turn.
- A negative/error reply, an already-known input, and child return or tool
  failure when those edges exist.

Criteria name the observable outcome: no repeated request for supplied data,
clarification before selecting an unconfirmed intent, and a safe destination
after retry exhaustion. Test downstream routing and side effects, not only
whether the ASK stored a value. Reuse cases; do not invent expected behavior
or change protected acceptance criteria to clear a risk.

Graph inspection does not authorize new tests, paid runs, live actions or a
wider redesign. Preserve the workflow's safety, approval and round limits.
Record unrelated risks separately. Once the existing all-pass and refute
requirements are satisfied, test-and-fix still stops; report uncovered graph
risks without starting another fix loop.

After staging, refresh the graph from the persisted draft and compare its
edges with the proposed graph. After authorized testing, annotate exercised
edges with case/run/turn evidence and outcomes. Mark remaining edges UNTESTED
or HELD with the reason. Diagram completeness is not runtime coverage. Report
which risks are resolved, still suspected or blocked; do not claim every
fallback is handled from a happy-path pass.
