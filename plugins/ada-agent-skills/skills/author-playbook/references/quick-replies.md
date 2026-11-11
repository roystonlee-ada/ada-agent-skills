# Quick-reply labels

Read this when you write or review an ASK with `accepted_values`. Source: the
docs.ada.cx step reference,
[quick replies for accepted values](https://docs.ada.cx/docs/automation/playbooks/step-reference#quick-replies-for-accepted-values).

## What the channel does

An ask draws buttons when it has one input, quick replies are on, and it has 2
or more accepted values. Each button title is the label from
`quick_reply_labels`, or the raw value when the value has no label. The docs
allow up to 10 options, and a value or label of up to 256 characters.

Quick replies work on Web Chat and the Messaging SDK only. The docs say other
channels are not supported yet, and how they show the question may change. Do
not promise buttons on Messenger, Instagram, LINE, WhatsApp, SMS or Email.
Write the question so a customer can type the answer, and see
`design-conversation/references/channel-features.md` for each channel.

## Rules for a label set

1. Every value gets a label of at most 20 characters, counted as Python `len`.
   This is a design rule for short buttons. The platform allows 256.
2. Labels are different from each other and from every other value.
3. A label reads as a button: "Yes, resolved", not "Yes, I would like to proceed with
   the refund request". Put the full wording in the question.
4. No snake_case token and no status value (`did_not_answer`) as a title. If a branch
   tests `did_not_answer`, keep the value and add a label such as "I'll describe it".
   If nothing tests it, leave it out: the extractor already returns that status.
5. Keep 10 values or fewer, the documented limit. Group the choices or split
   the question.
6. Do not word the question around a label. A customer on another channel may
   never see the buttons.

A tapped button's label or value is matched by the ask, so you can reword a label on a
live playbook without changing any branch.

## Shorten, do not cut meaning

| Too long | Fits |
|---|---|
| Yes, I would like to proceed with the refund request (52) | Yes, proceed (12) |
| No, I still need help (21) | No, still need help (19) |
| Driver or delivery partner earnings and payouts (47) | Earnings or payouts (19) |
| Receipt/statement - Transport booking (37) | Transport receipt (17) |

Keep the emoji if a design uses them. Each counts as at least one character, and some
(a heart with a variation selector) count as two.

## Check before you stage

Run the checker on the playbook JSON or the changeset file. It exits 1 on any title
over 20 characters, a clash, a snake_case title or a status title, and prints a WARN
for more than 10 values:

    python3 scripts/check_quick_replies.py <file.json>

Fix an existing agent the same way: export each playbook, add the missing labels, run
the checker, stage the change as a changeset, and read the diff. Only
`quick_reply_labels` should differ.
