# Situation classes for handoff clusters

Place each handoff cluster in one class. The class decides what to recommend and
which skill takes it next. Read the conversations to place a cluster: the
reason code the agent recorded is a lead, not the answer.

Contents:
- How to place a cluster
- The six classes
- Clusters outside handoffs
- Mixed clusters

## How to place a cluster

Ask these in order. Stop at the first yes.

1. Did a person need to decide, approve or hold authority that the agent may
   not have? Policy or authority.
2. Was the customer distressed, complaining, grieving or a high-value case where
   a person is the right answer? Judgment or care.
3. Was the answer a fact the agent lacked, or got wrong? Information gap.
4. Did the task need a system the agent could not read or write? System action.
5. Did the handoff come from routing, a trigger or a loop, not from the task?
   Design or routing.
6. Could the agent have resolved it with what it already had? Agent-resolvable.

The order puts the floor first on purpose. A cluster that looks automatable but
needs an authority decision is a floor cluster, and ranking it as a target sends
the next skill after a fix that policy will block.

## The six classes

### Information gap

Knowledge is missing or wrong.

- Signals: reason `knowledge_unavailable`; a knowledge search with no useful
  article; the agent answered with a wrong or stale fact; human agents answer
  the same question with the same facts after the handoff.
- Recommend: name the questions, with counts. Draft the article or fix the
  existing one. Check for a duplicate or a conflicting article first.
- Metric moved: containment and automated resolution. CSAT when the wrong fact
  caused the low score.
- Next skill: knowledge edit (a changeset edit of the article), then
  `test-and-fix`.
- Take the facts from the human replies (`human-agent-learning.md`) when you
  have them. Never invent the article body.

### Policy or authority

A person must decide.

- Signals: reason `out_of_scope`; the agent said it cannot approve or change
  something; the human agent approved, waived or declined.
- Recommend: nothing to automate. Report it as the floor with its size.
- Metric moved: none by automation. Say so.
- Next skill: none. If the business wants to change the policy, that is a
  decision for the business, not a fix to the agent.
- One exception worth flagging: when the humans approve nearly every case, the
  policy may be a rubber stamp. Report that as a question for the owner. Never
  recommend removing the check.

### System action

The task needs a system the agent cannot reach, or that failed.

- Signals: reason `tool_unavailable` or `tool_failed`; the human agent did the
  task in a back-office system (changed a booking, reissued a code, looked up an
  order); the agent promised an action it could not run.
- If an API exists for the task: size the task, then propose end-to-end
  resolution. Name the call, what the agent checks before it, what it tells the
  customer after it, what it does when the call fails, and which cases still go
  to a person. Never stop at "add an API".
  - Metric moved: containment, automated resolution, often CSAT.
  - Next skill: `design-conversation` for a new use case, `revise-playbook` when
    a playbook already owns the flow.
- If no API exists: do not recommend a build that cannot happen. Recommend that
  the agent collect the required fields, verify what it can, and write a
  summary before it hands off, so the human resolves the case faster.
  - Metric moved: human handle time and CSAT. Containment does not move, so do
    not claim it.
  - Next skill: `revise-playbook` or `design-conversation` to add the
    collection step, and `configure-handoff` when the fields or the summary do
    not reach the helpdesk.
- For `tool_failed`: name the tool and what it returned. A failing tool is a
  fix to the tool, then `diagnose-conversation` for the cases it already
  dropped.

### Judgment or care

A complaint, a distressed customer, or a high-value case.

- Signals: strong negative sentiment; a bereavement, a safety issue, a threat to
  leave, a legal or media mention; a customer flagged as high value.
- Recommend: keep the handoff. Make it better: hand off early, say why, do not
  make the customer repeat themselves, and pass a summary.
- Metric moved: CSAT, and human handle time. Not containment.
- Next skill: `revise-playbook` for the handoff step and its wording.
  `ada-custom-metrics-improve` if a metric already scores these.
- Do not rank by containment. These are not targets. Report the size so the
  person sees the share of the human workload they represent.

### Design or routing

The customer asked early, a trigger misfired, or the flow looped.

- Signals: reason `end_user_requested` in the first turns; reason
  `handoff_configured` with a request the agent could handle; the wrong
  playbook started; the same step repeated; the greeting swallowed the first
  message.
- Recommend: name the misfire. A request for a person in the first turn is often
  a trust or wording problem, so read what the agent said just before. A loop is
  a step with no exit.
- Metric moved: containment, CSAT.
- Next skill: `diagnose-conversation` first, because it names the surface that
  owns the problem and rules out the others. Then `revise-playbook` or
  `configure-handoff`.

### Agent-resolvable

The agent could have resolved it, and an instruction or playbook gap stopped it.

- Signals: reasons `issue_unresolved` or `other`, or a `handoff_configured` that
  a rule no longer justifies; the knowledge and the tools were enough; the
  agent gave up, over-escalated, or asked too many questions.
- Recommend: name the rule, step or instruction gap. If a playbook sends cases
  to a person by design, show the count and ask whether it still should.
- Metric moved: containment, automated resolution.
- Next skill: `diagnose-conversation` to name the surface, then
  `revise-playbook` or a knowledge edit, then `test-and-fix`.

## Clusters outside handoffs

Not every cluster is a handoff. Place these the same way.

- Contained but not resolved: the agent answered and the customer got nothing
  they could use. Usually an information gap or an agent-resolvable gap.
- Low CSAT without a handoff: read the comments. A wrong fact is an information
  gap. A cold or looping reply is design or routing.
- Failing custom metric: if the metric is a fair judge, the cluster is a defect
  of one of the classes above. If the judge is wrong, the next skill is
  `ada-custom-metrics-improve`, which decides that.

## Mixed clusters

One cluster can hold two classes, for example a refund task where small refunds
are automatable and large ones need approval. Split it by the condition that
separates them (an amount, a customer tier, a region) and size each part. The
part that needs a person is floor. The other part is a target.
