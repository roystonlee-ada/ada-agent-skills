# Case map example

The shape of `verify-<subject>/cases/`. This example is for a made-up refund
status use case. Every name, id and sentence is a placeholder to show the
shape, so replace each one with real values from the agent's instance.

## cases/README.md

# Refund status verification map

Read this index before testing, then use the matching case file as the recipe.

## Baseline preconditions

- A draft changeset is staged. Doctor confirms its id.
- The test data holds one refunded order and one order with no refund.
- No case starts a real handoff or sends a real message.

## Driving conventions

- Run every case on live first, then on the draft. A target case that already
  passes on live is a wrong case.
- Repeat the cases that matter for a pass rate.

## Proof and skip reporting

- Each proof lists the case name, the conversation links, the verdict and the
  reason.
- Report an unreachable case with what was attempted and what was missing.
- Never report a skipped case as verified some other way.

## Cases

- [Refund found](./refund-found.md) covers a customer with a refunded order.
- [No refund yet](./no-refund-yet.md) covers a customer whose order has none.

## cases/refund-found.md

# Refund found

A customer asks where their refund is. They get the amount, the date and the
payment method in one reply, and the agent does not ask for the order number
twice.

## Sub-cases

- `refund-found-chat` resolves in two customer turns.
- `refund-found-no-number` asks once for the order number when it is missing.

## How the customer reaches it

- Types "where is my refund" in the chat.
- Gives an order number in the first message.

## Driving it

Preconditions: the draft is staged and the test data holds the refunded order.

- **First message only.** Send "where is my refund". Expect one ask for the
  order number and no handoff.
- **With the number.** Give the order number. Expect the amount, the date and
  the method from the lookup, matching the test data.
- **Proof.** Save the conversation links for the live run and the draft run,
  and the reasoning log line that shows the lookup.

## Gotchas

- A case that names an amount passes only if the test data holds that order.
- Chat and voice wording differ. Add a separate voice case.
