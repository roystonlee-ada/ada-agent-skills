---
name: ada-rollout-changeset
description: >
  Ramp a tested changeset onto live traffic in steps (sampled rollout at 10%,
  20%, 50%), judge each step against the baseline, and recommend promote, hold
  or revert. Use when someone says "roll it out", "start on 10%", "ramp it",
  "step it up", "stop the rollout", "is the change hurting", or "should we
  revert", or after ada-promote-changeset picks the rollout path.
---

# Roll out a changeset in steps

A sampled rollout sends a random share of new chats to the changeset and keeps
the rest on live. Because the split is random, a gap between the two groups is
caused by the change. That is why a ramp beats "promote and watch".

## 0. Pick the runtime

Each step below names what to do, not a command. Read one file for how:
- Ada MCP tools present (`get_ada_configuration`, `list_agent_changesets`) →
  `references/runtime-mcp.md`
- `adacli` on the path, or you are inside Ada Architect →
  `references/runtime-cli.md`

Read `references/rollout-metrics.md` before building the comparison, the stop
check or the attribution table, and before recommending a revert.

## Preconditions

- The changeset is `testing` and passed the checks in `ada-promote-changeset` step 1.
- Sampled rollouts on the instance add up to 100% or less. Read each active
  rollout's percentage from the changeset list.
- The person asked for this step in chat. Starting or raising a rollout puts the
  change in front of real customers. Stopping one never needs a second ask.

## Ask which ramp first

Before starting, ask the person which they want, and recommend one with a reason:

- **Stepped ramp, 10% then 20% then 50%** (recommended by default). Each step
  waits for enough chats and a clean stop check. Fits a change that touches
  what customers are asked or a high-volume use case.
- **One number they choose** (for example 5%, 25% or 50%). The rollout stays at
  that percent until they ask to change it. Fits a low-risk change, or a small
  instance where the stepped hold times would take days.

If they give a number, use it as the only stage. Keep the same stop check and
the 100% cap across active rollouts, and tell them how many chats at that
percent the stop check needs and roughly how long that takes at current volume.

## The stepped ramp

| Stage | Percent | Hold at least | Chats on the changeset before moving on |
|---|---|---|---|
| 1 | 10 | 2 h | 5 that reached a changed playbook |
| 2 | 20 | 2 h | 15 |
| 3 | 50 | 6 h | enough for the stop check (100 per arm) |

Early stages count the changeset arm only, because ramping is how a thin arm
gets chats. The last stage needs the minimum in both arms, so the stop check has
power before anyone is asked to decide. Change the hours and counts to fit
volume, and say so.

Start, raise or stop a stage as the runtime file says. Set the conversation cap
high enough to reach the stage minimum, because the rollout completes the
moment the cap is hit.

## At each stage

1. List the sampled chats that have settled (`ada-playbook-monitor-loop`,
   `references/finding-verification.md`). An unfinished chat reads as a dead end.
2. Compute the changeset arm against the baseline arm, with 95% intervals
   (reference file).
3. Run the stop check. If it fires, stop the rollout, then report. Stopping is
   safe and reversible, and waiting for an ask costs customers chats.
4. If it holds, report the stage in one block: chats per arm, bad rate for each
   with the interval, loops traced to a playbook, and the next stage's earliest
   time. Then wait for the person to ask for the next step.

## Judging the result

When the last stage ends, compare with the platform's changeset comparison, over
the rollout's dates. Start on the first full day after the rollout began. The platform groups by
day, so a mid-day start puts chats from before the changeset existed into the
same day and shows a false drop.

Report each finished ramp as "this change, these metrics": changeset arm vs
baseline with intervals, then give a plain recommendation:

- **Promote** when the stop check never fired and the key metric held or moved
  the right way.
- **Hold** when the arms are too thin to tell. Say how many more chats you need.
- **Revert** only when the defect comes from a step the change touched and no
  quick forward fix exists. See the reference file.

The person promotes or reverts. Promote through `ada-promote-changeset`.
