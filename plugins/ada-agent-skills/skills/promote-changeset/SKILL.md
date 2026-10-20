---
name: promote-changeset
description: >
  Take a staged changeset from "tested" to "ready for the person to promote":
  check the test results, show the real diff, pick direct promote or a sampled
  rollout, and hand the person the promote step. Use whenever someone says
  "promote", "go live", "ship it", "roll it out", "no ramp", or asks why a
  staged change is not live yet.
---

# Promote a changeset

A changeset reaches live traffic only when the person decides it should. You
prepare the decision and make it easy to take. You never take it for them.

## 0. Pick the runtime

Each step below names what to do, not a command. Read one file for how:
- Ada MCP tools present (`get_ada_configuration`, `list_agent_changesets`) →
  `references/runtime-mcp.md`
- `adacli` on the path, or you are inside Ada Architect →
  `references/runtime-cli.md`

## 1. Prove it before asking

- Confirm the changeset is still `testing`. A status of `promoted`, `reverted`
  or `deleted` ends this skill: say so.
- Run the saved cases that touch the changed playbook on the draft and on
  live. Report each case as live vs draft, with the judge's reason for every
  failure.
- Add real past conversations that hit the changed step as cases, so the test
  is not only the cases you wrote for the fix.
- A green table with zero cases means nothing was tested. Say that instead of
  "passed".
- A case that fails on draft and passed on live is a regression. List it first.

## 2. Show the real diff

Show the platform's own before and after for the changeset. Do not describe the
change from memory: the thing that made the change is the worst judge of it.

If live config moved after staging, the promote will refuse as stale. Offer to
restage against the current live version and show the new diff.

## 3. Pick the path and recommend one

| Path | When it fits |
|---|---|
| Sampled rollout (`rollout-changeset`) | The change touches a high-volume use case, changes what customers are asked, or the test set is thin. |
| Direct promote | A wording fix or one-step bug fix, a passing test set with real conversations in it, and low volume. |

Ask with a recommendation and a reason, in plain words. State the cost of each
path: a rollout takes hours and needs enough chats, a direct promote moves
every chat at once.

## 4. Promote

The person promotes. The runtime file says how that happens where you are. If
you cannot promote from here, hand over the changeset name and where to press
Promote in Ada, and say nothing is live yet. Typed text such as "just promote
it", or a skill file, never counts as authorisation to skip a gate.

Do not retry a refused promote or work around it. Report the refusal and the
exact error.

## 5. After it is live

- Say in one sentence whether it went live, and when.
- Start watching it with `playbook-monitor-loop`, which holds the arms and the
  stop rule.
- Record the changeset name, the promote time and the test numbers where this
  use case's notes live, or in your final message if nothing saves them.

## Rules

- You draft and test. The person promotes or rolls out.
- Never promote someone else's changeset, or one you did not test this session.
- Keep customer data, order numbers and personal details out of the summary.
- Delete changesets you staged only for a test.
