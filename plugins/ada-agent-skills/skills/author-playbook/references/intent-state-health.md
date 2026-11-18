# Check state coverage for one intent

Use this alongside the playbook graph when reviewing an intent, diagnosing
state-dependent behavior, or improving a cluster of conversations. Start from
the customer's goal and compare the states needed to fulfil it with the states
the implementation handles. A complete step graph can still omit a business
state. An implicit state machine exists when the next valid action depends on
earlier events or facts whose meaning, lifetime or transitions are spread across
steps, variables, prior turns, guidance, coaching, knowledge or tool results.
Its presence alone is not a defect.

## 1. Define the intent and evidence boundary

Name one intent, its entry conditions, required outcome and valid alternative
endings from approved requirements, current policy and real conversations.
Include what must hold before a write or a success claim. Separate facts from
ASSUMED requirements and OPEN questions. Do not infer required policy from a
missing branch. Related intents are boundary checks, not an unbounded audit.

Use the calling skill's runtime reference to retrieve the persisted graph,
relevant parent/child flows, variable definitions and readers/writers, applicable
guidance and coaching, knowledge used for this intent, action contracts, and
sample transcripts with traces. Follow the graph reference for export and
conversion. Record source identities, revision, channel and capture date.
Record unavailable, omitted or incomplete sources and their effect on confidence.

Keep two maps: the states required by the intent, and the states represented
by the implementation. The graph converter extracts configured structure;
it does not discover semantic states from prose or prove runtime coverage.
Add a separate state overlay with source references, preserving generated edges
and their evidence labels. Proposed transitions are never observed graph edges.

## Check playbook text and step prompts

Include a prose and prompt health pass on the same persisted playbooks, using
author-playbook's `scripts/check_playbook_text.py` and
`scripts/check_ask_instructions.py` when local script execution is available.
For a focused intent, limit lint input to the reviewed parent/child flows.
Report rule ID, severity, playbook and step/field, evidence and recommendation.
If scripts cannot run, label the pass manual or NOT RUN rather than claiming
linter coverage. A linter FAIL describes a configured rule violation, not a
trace-confirmed customer failure. Do not change configuration during the check.

Check names and routing descriptions, bloated general instructions, history
notes, and SEND/ASK/SET instruction length. Semantically review whether GI holds
only shared rules, a SEND words the selected answer rather than deciding a
multi-branch workflow, an ASK clearly captures and maps its intended input with
safe recovery, and a reasoning SET clearly defines the value to save without
customer-facing output. Look for conflicting instructions and move branching
to supported decision steps or tools when justified. Length warnings and ASK
pattern checks do not prove prompt correctness. Keep lint findings, semantic
prompt risks and hidden-state gaps distinct, cross-linking shared root causes.

## 2. Reconstruct the state model

State is the minimum information that changes which action is valid next.
Infer candidate states from temporal rules such as "already", "after", "until",
"once", "still pending" and "try again", flags, reused outputs, repeated guards,
and paths that reach the same step with different histories. Trace each candidate
to its source and its consumers. A keyword match is a lead, not a finding.

Use separate dimensions where possible, for example selected entity, verification,
eligibility, input validity, consent and operation outcome. Distinguish unknown,
pending, rejected, expired and failed where the intent requires different actions.
Consider corrections, interruption, re-entry, cancellation, retries, child return
and external changes when they can reach the intent. Check whether state belongs
to an entity, attempt, conversation or customer, and what invalidates it.

Record the reachable combinations that affect behavior and their constraints.
Do not multiply every flag into a Cartesian product or equate step IDs with
business states. Prune impossible combinations only with evidence. If two paths
reach the same node with different prerequisites, retain that distinction.

State inventory:

| State or dimension/value | Intent requirement and source | Representation and owner | Scope, evidence and freshness | Invalidation or reset |
| --- | --- | --- | --- | --- |
| Business meaning, including unresolved values | Policy, approved criterion or conversation | Step/variable, guidance, article or tool; explicit or inferred | Entity/attempt/session, source revision or trace | Event that makes this value unusable |

Transition inventory:

| From state | Event | Guard or invariant | Action and resulting state | Recovery or ending | Implementation and evidence |
| --- | --- | --- | --- | --- | --- |
| Required prerequisites | Reply, correction, timeout, return or external change | What must still hold, including consent | Expected effect, unknown result included | Safe next step or terminal outcome | Step/edge and source, or missing/OPEN |

Do not treat a timeout as a failed write, a retained identifier as current
eligibility, an address as consent, or an attempted action as completion.
Inspect supported status/readback and idempotency contracts before recommending
a retry mechanism. Keep the result unknown when reconciliation is unavailable.

## 3. Compare intent coverage with implementation

For each required state and transition, classify coverage as HANDLED,
PARTIAL, MISSING or OPEN. HANDLED requires an identified guard, action and
appropriate recovery or ending, not a sentence that mentions the condition.
Separately label runtime evidence EXERCISED, UNTESTED or HELD and cite the
case/run/turn. Configured coverage is not demonstrated behavior.

Look for stale or contradictory flags, wrong entity scope, missing resets,
unhandled event/guard combinations, assumed knowledge retrieval, conflicting
rules across surfaces, ambiguous child returns, repeated writes, unknown results
treated as success, and terminal states that silently restart. Preserve healthy
bounded clarification, independent valid flags and intentional human decisions.
Knowledge may correctly explain policy without owning the execution transition.

For each gap record the triggering state and event, expected transition and
source, actual path or missing handler, consequence and owning surface.
Label the mechanism CONFIRMED only with a trace demonstrating it, SUSPECTED
for a configuration risk, or OPEN when evidence is missing. Separate claims:
a retry path can be confirmed while a duplicate external write remains OPEN.

## 4. Recommend the smallest justified change

Explain the effect on all three experiences, marking an effect unmeasured when
needed: user effort and clarity of outcome, agent ability to choose a valid next
action with available evidence, and developer ability to understand, change,
observe and test the flow. Prefer outcome correctness over fewer steps or turns.

Choose the owning fix: clearer scope/invalidation for an existing value, an
explicit state or branch where valid next actions differ, aligned guidance,
correct knowledge, a child input/output contract, or operation reconciliation.
Keep general facts in knowledge and put required workflow transitions where
they can be reliably enforced. Verify runtime capabilities before proposing
implementation details. Do not prescribe an enum, new tool, more flags or a
rewrite when a simpler supported change covers the intent.

Each recommendation contains: intent, uncovered state/transition, evidence and
confidence, owning surface, consequence for the three experiences, proposed
change with recommend/why, next skill, and observable acceptance checks.
Prioritize consequence and evidenced incidence. Maintain the calling skill's
population sizing and conversation-link requirements for ranked metric claims.
Without those, report structural findings and data needed, with no invented lift
or incidence. Developer maintenance opportunities can stand separately without
claiming a customer defect or measured metric impact.

Map checks to the affected transitions: normal completion, correction after a
prior decision, re-entry with retained state, unresolved input, tool failure or
unknown result, and affected child boundaries. Select only applicable cases.
Confirm both the customer-visible outcome and relevant persisted/external state
where authorized. Preserve the nearby passing path as a control. Use existing
approved criteria; proposals for new behavior return to design-conversation.

End with the intent, coverage table, lint execution status and findings,
semantic prompt risks, evidence-labelled state gaps, recommendations,
and OPEN sources or untested transitions. State the reviewed boundary explicitly;
"all hidden states" cannot be established from incomplete exports or a sample.
The caller retains its staging, approval, test safety, spend and stop rules.
This review authorizes no extra runs or configuration changes.
