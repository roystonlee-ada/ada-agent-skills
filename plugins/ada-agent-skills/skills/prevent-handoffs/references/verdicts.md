# Verdicts for handed-off conversations

Give every handed-off conversation one verdict, one category, a cause label
and evidence. Judge what the customer needed and what stopped the agent, not
the reason code. The agent picks the code itself, so treat it as a lead.

## Before you start

Write down three facts about the agent, because every verdict depends on them:
- which systems the agent can read or write (its tools and actions, and
  whether each is enabled)
- which playbooks hand off by design, and what triggers each
- which channels and languages it serves

A task is "system access" only when the agent has no tool for it. If a tool
exists and the agent did not use it, the handoff is preventable.

## Categories

Test in this order and stop at the first that fits. The floor comes first on
purpose: a handoff that looks easy but needs a person's authority must not be
counted as a target.

### Not preventable

| Category | Fits when | Typical signals |
|---|---|---|
| `N_POLICY` | A person must decide or act by policy | Safety, accident, harassment, threats, fraud, account takeover, a legal or media threat, a conduct complaint that needs an investigation, a refund or compensation that needs approval, a suspension appeal, a request the business routes to a team by rule |
| `N_SYSTEM` | The task needs a lookup or a change in a system the agent cannot reach | The status of one case, application or order; a balance, payout or charge on one account; a profile or bank change done in a back office. The human agent looked up or changed a record |
| `N_ASKED` | The customer wanted a person and gave the agent nothing it could act on | Only "agent" or "human", a refusal to state the issue, or the agent gave a correct, complete answer and the customer still wanted a person |

A request for a person is not `N_ASKED` when the customer also stated a task.
Judge the task. A customer who types "agent", then describes a question the
agent could answer, is preventable if the agent then failed to answer.

### Preventable

| Category | Fits when |
|---|---|
| `P_KNOWLEDGE` | The need was a general fact, rule or procedure, and the agent had no article, said it did not know, or gave a vague or wrong answer. Also when the human agent only gave general information, with no lookup |
| `P_GAVE_UP` | The agent had or retrieved the right information, or the task was answerable, and it handed off anyway, or a triage step routed to a person without trying |
| `P_ROUTING` | A wrong playbook fired, a greeting or role question looped, or a keyword sent an answerable question to a handoff playbook |
| `P_LOOP` | The agent repeated the same question or "did that help?" until the customer asked for a person |

### Unclear

`U`: the record does not show enough to decide. Send it to the read pass. A
cause with more than 15% unclear needs more transcripts read before it is
ranked.

## Hard calls

| Case | Verdict |
|---|---|
| Generic troubleshooting failed, and the human then checked the account | `N_SYSTEM`. The first steps were right; the rest needed a lookup |
| Generic troubleshooting failed, and the human repeated the same tips | `P_KNOWLEDGE` or `P_GAVE_UP`. The agent could have said it |
| A handoff-by-design playbook fired on a general question | `P_ROUTING`. The design may still be right for the cases it was built for, so name both |
| The human told the customer to wait for an existing case | `N_SYSTEM` for the status lookup. If the agent could have said the standard wait time, note it as a smaller knowledge fix |
| The customer was upset, and the task itself was a fact | Judge the task. Note the sentiment in the evidence |
| Mixed: part of the cluster needs approval, part does not | Split it by the condition that separates them, as `improve-agent` `references/situation-classes.md` says under mixed clusters |

## The cause label

3 to 6 words naming the task, in the language of the report:
"office address and hours", "case status follow-up", "driver registration
requirements". Reuse a label across conversations for the same task. Merge
near-duplicates before you count.

## Output line

One line per conversation, pipe-separated:

```
id|verdict|category|cause|evidence
```

- `verdict`: `preventable`, `not_preventable` or `unclear`
- `evidence`: 20 words at most, from the summary or the transcript, in your
  own words. No names, contact details, order numbers or account numbers.

## Checking the record pass

When you judge from summaries, check them against transcripts (SKILL step 3).
Read at least 8 per large cause, and count agreement on verdict and on
category apart. The verdict matters for the ranking. The category matters for
the fix.
