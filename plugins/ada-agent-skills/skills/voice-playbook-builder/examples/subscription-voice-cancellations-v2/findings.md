# Findings from the first live calls

What went wrong and what changed, as lessons. Every billing API call did what it should. The losses came before the flow
(verification) and from the fallback wording.

## What went wrong
- Most callers never verified. The phone-number member search found no account, and callers repeated the same number.
- A few callers timed out while fetching a code. The auth child needs patience during code entry.
- A discount offer turned many verified callers into transfers, and it was offered to a chargeback dispute.
- A subscription that the billing API calls active, with a long-past renewal date, failed cancel prep with 422. The caller got an
  honest message and a transfer, and an agent then cancelled the real membership.
- Some callers with no active membership were read the cancel walkthrough anyway.
- Duplicate membership names broke fee disclosure.
- A caller phrase about not being able to get online re-fired the fallback.

## What changed or is proposed
1. Say up front that the cancel can be done on this call.
2. Short, choice-based fallback (text the link, or connect to an agent), keyed on portfolio state.
3. Email path in the auth child, plus a loop guard on the "can't get online" phrase.
4. Skip the save offers for billing disputes.
5. Continue past a failed membership instead of stopping.
6. Never state refund outcomes.
