# Vertical priors for custom metrics

Priors, not facts. Every metric here is ASSUMED until this agent's transcripts or stated rules support it. Read the universal set plus the matching vertical only.

## Contents

- Universal set
- Airlines
- Ecommerce and retail
- Fintech and banking
- Telecom and utilities
- Travel and hospitality
- Marketplace, ride-hailing and delivery
- B2B SaaS and software support
- Verticals not listed

## Universal set

Fits any agent. Start here, then add the vertical layer.

| Metric | Passes when |
|---|---|
| No repeated replies | The agent does not resend the same reply after a usable new customer turn |
| No re-asking | The agent does not ask for information the customer already gave |
| Clear way forward | The customer ends with a next step, an answer or a person, never a dead end |
| Handoff kept | The agent does not promise a person and then drop the customer |
| Verify before sharing | Account or booking details go out only after the customer is verified |
| Question answered | The reply addresses what the customer asked |
| Request resolved | The request was done or correctly routed to a person who must do it |
| Language match | The agent replies in the customer's language |

## Airlines

Customers care about: disruption (delay, cancel, rebook), refunds and credits, baggage, check-in and seats, name changes, loyalty miles, speed to a human in a crisis.

| Candidate | Passes when | Judge limit |
|---|---|---|
| Disruption help first | A disrupted customer gets options before a form or a handoff | Sees offered options, not the real rebooking |
| Fare rule stated correctly | Change or refund conditions match what the customer was told earlier in the chat | Cannot check against the fare database |
| Empathy on disruption | The agent acknowledges the impact before the process | Text only |
| Baggage case next step | A baggage report ends with a reference or clear next step | Cannot see the system record |
| Loyalty claim handled | Missing-miles requests get the right route and required details | Cannot see the account |
| Urgent need escalated | Travel within hours, medical or bereavement requests reach a person fast | Needs a clear transcript signal |

Watch: containment and handoff wording, since needed handoffs are common. Keep a handoff that the request needs null or pass.

## Ecommerce and retail

Customers care about: where is my order (WISMO), returns and refunds, wrong or damaged items, cancellations, promo codes, product questions, delivery changes.

| Candidate | Passes when | Judge limit |
|---|---|---|
| Order status given | A status request gets status or the reason it cannot be given, before an offer to refund | Cannot confirm the status was right |
| Return path explained | The customer gets the steps, window and cost of a return | Policy accuracy needs a KB check |
| Damaged item handled | Evidence is requested once and the customer gets a clear remedy | Cannot see photos |
| Refund promise safe | The agent never promises a refund outside stated policy | Needs the policy in the metric wording |
| No upsell on a complaint | An unhappy customer is not pitched a product | Text only |
| Product answer grounded | The agent says when it does not know a product fact | Cannot see the catalogue |

Watch: refund or reprint cases that escalate by design, so keep them null or pass.

## Fintech and banking

Customers care about: card and account access, disputes and fraud, payment failures, limits and fees, KYC and onboarding, stress when money is missing.

| Candidate | Passes when | Judge limit |
|---|---|---|
| Identity verified first | Account detail follows verification | Cannot see the verification system |
| No sensitive data requested in chat | The agent never asks for a full card number, PIN or password | Text only |
| Fraud routed fast | A fraud or lost-card report gets a safe immediate step and a person | Needs clear signal |
| Fee and limit stated plainly | Costs are given without hedging or invention | Accuracy needs a KB check |
| Compliance wording kept | Required disclaimers appear where the customer's rules say | Needs the customer's rule list |
| Tone under stress | A distressed customer gets calm, direct help | Subjective, spot-check |

Ask in the interview: which wording is regulated, and which topics must never be automated.

## Telecom and utilities

Customers care about: outages, bills and charges, plan changes, device and SIM issues, contract exit, moving home.

| Candidate | Passes when | Judge limit |
|---|---|---|
| Outage acknowledged | A known outage is named before troubleshooting | Cannot see outage data |
| Troubleshooting not looped | Each step is new, and the agent stops after the useful steps | Text only |
| Bill explained | A charge question gets a plain breakdown or a route to one | Cannot see the bill |
| Retention handled honestly | A cancel request gets the path, with at most one relevant offer | Subjective |
| Plan change confirmed | The customer gets the effective date and cost | Accuracy needs a KB check |

## Travel and hospitality

Customers care about: booking changes and cancellation, check-in and arrival, refunds and deposits, special requests, third-party bookings (who owns the booking).

| Candidate | Passes when | Judge limit |
|---|---|---|
| Booking owner identified | The agent finds who holds the booking before offering a change | Text only |
| Cancellation terms stated | Cost and deadline are given before the customer commits | Accuracy needs a KB check |
| Time-critical request escalated | Same-day arrival or check-in problems reach a person | Needs clear signal |
| Special request logged | The customer is told what happens to the request | Cannot see the system |

## Marketplace, ride-hailing and delivery

Customers care about: missing or wrong orders, refunds, driver or courier issues, safety, payment and promo problems, account bans. Two or three audiences (customer, driver or courier, merchant) with different needs.

| Candidate | Passes when | Judge limit |
|---|---|---|
| Audience identified | The agent works out whether it speaks to a rider, driver or merchant before advising | Text only |
| Safety escalated | A safety report gets an immediate step and a person | Needs clear signal |
| Compensation within rules | Refund or credit offers stay inside the stated limits | Needs the limits in the wording |
| Local language and tone | The reply matches the customer's language and register | Spot-check per language |
| Policy not invented | The agent says when it does not know a rule | Text only |


## B2B SaaS and software support

Customers care about: access and login, billing and seats, how-to questions, bugs and outages, integrations, escalation to an engineer.

| Candidate | Passes when | Judge limit |
|---|---|---|
| Step-by-step answer usable | A how-to answer has ordered steps the customer can follow | Cannot check product accuracy |
| Bug report complete | Escalations carry the details an engineer needs, asked once | Cannot see the ticket |
| Known limit stated | The agent says when the product cannot do something | Needs the limit list |
| Security request routed | Access, SSO and data requests go to the right person | Needs clear signal |

## Verticals not listed

Build the prior from the agent itself: the top topics, the customer's own rules, and what the customer's team complained about in tickets or calls. Then tell the user the vertical layer is thin and lean on the interview (step 5).
