# What the sandbox runs showed (30/10/2026)

A test agent with no live traffic. Web chat only. Each chat ran one SET instruction three times in a row: Normal, High, Normal again. The two Normal runs count as two Normal answers. Chats where the input never reached the step are left out. The runs are small, so read the table as direction, not as a rate.

| Task | Normal right | High right | Median seconds, Normal | Median seconds, High |
|---|---|---|---|---|
| Date plus 3 weeks ("last Tuesday of February 2027") | 3 of 8 | 4 of 4 | 2.1 | 1.9 |
| 5 business days after a date | 6 of 10 | 5 of 5 | 2.5 | 1.9 |
| Same date task, instruction rewritten as numbered steps | 5 of 8 | 4 of 4 | 2.4 | 1.9 |
| Same business-day task, instruction rewritten as numbered steps | 4 of 8 | 4 of 4 | 2.4 | 2.0 |
| Price with discount, then VAT | 6 of 6 | 2 of 3 | 1.2 | 2.0 |
| Layered baggage-fee rule in the instruction | 8 of 8 | 4 of 4 | 1.5 | 2.0 |
| Loyalty tier from a two-part rule | 8 of 8 | 4 of 4 | 1.2 | 2.0 |
| 30-entry lookup list | 8 of 8 | 4 of 4 | 1.0 | 1.9 |
| Classify by primary ask | 10 of 10 | 5 of 5 | 1.1 | 1.8 |
| Pull an order number (control) | 6 of 6 | 3 of 3 | 0.9 | 1.7 |

## What to take from it

- **Date and weekday arithmetic is the clear win.** Normal got 18 answers right out of 34 on the four date tasks above: 9 of 18 on the original wording and 9 of 16 on the rewrite. High got all 17. Normal's misses were off by 1 to 5 days, and the wrong answer looked fine, so nobody would notice without a check.
- **A longer instruction did not rescue Normal.** Numbered steps, month lengths and the weekday spelled out left Normal at about half right. Raise the level for date math. Do not expect a rewrite to fix it.
- **High is not a general upgrade.** On rules, lookups, classification, plain extraction and this arithmetic task, Normal was already right every time. High cost 0.5 to 0.9 seconds more per step and got one price wrong (3753.00 for 3780.00).
- **The cost depends on the task.** On a plain extraction High took about 1.9 times as long (1.7 against 0.9 seconds). On date math High was no slower than Normal. The longest High step in about 45 runs was 3.0 seconds.
- **These cases were easy for Normal.** The rule, lookup and classification cases may still need High when they are harder or messier than these. That is why the skill proves each step on its own inputs instead of trusting the task type.

## How High works (read from the platform source on 30/10/2026)

- High sends every extraction for the step to one stronger model at low effort, with the same prompt and schema.
- High has a time limit of 8 seconds and no second model. If it fails on a SET, the step writes its `fallback_value`. A failed ASK extraction is retried by asking again. Neither case tries the fast model.
- Normal tries a fast model first and falls back to a second model on any error.
- The level applies to a generative SET and a reasoning ASK, including follow-up turns and voice read-backs. It does nothing on an exact SET, an exact ASK or a send step.
- A stored value that is not `high` runs as Normal.

## Not measured

- Voice. High adds time to each extraction, and a voice ASK with a read-back adds it to every turn.
- Real customer inputs, which are messier than these.
- Whether High changes answers on multi-variable SET steps.
- How often High hits its 8 second limit under load.
