# Changesets: what can be staged, and how to revert

Use when the person asks whether a change can be tested before it is live,
why a dashboard edit is not on the Change sets page, or how to undo a
promoted change. Promote and rollout stay with `ada-promote-changeset` and
`ada-rollout-changeset`. Do not copy their steps here.

## Preconditions

- Write access to the agent.
- The changeset's status: Testing, Promoting, Promoted or Reverted.

## Steps

1. Staged on a changeset: knowledge articles, custom instructions, playbooks,
   API tools, code tools, MCP tools, MCP server connections, coaching and
   processes.
2. Live at once, no changeset: topics, intents, custom metrics, scorecards,
   glossary terms, knowledge sources, variables and test cases. Channels,
   team, SSO, session limits, API keys, webhooks, allowed websites and email
   are dashboard or API settings with no changeset.
3. A direct edit on the Knowledge or Playbooks page does not appear on the
   Change sets page. Revert it by hand.
4. Rename, rollout, promote and delete need write access and Testing
   status. Rollout percentages across active rollouts cannot exceed 100.
5. To undo a promoted changeset, create a revert. It makes a new Testing
   changeset that inverts the promoted one. Nothing goes live until the new
   changeset is promoted. Only one Testing revert per source is allowed.
6. A promoted changeset can be reverted for 90 days, then it is deleted. A
   Testing changeset is deleted 90 days after creation.
7. For the promote or rollout of the revert, hand over to
   `ada-promote-changeset`.

## Downtime risk

None for staging, testing or building a revert. Promote is the step that
changes live traffic.

## How to verify

Read the changeset's diff and confirm it lists the edits expected.

## Rollback

The revert is the rollback. For a live-only setting, restore the recorded
old value by hand.

## Source

- `product-docs/fern/versions/pages/docs/optimization/change-sets.mdx`
- `edit_agent_behavior` tool definition (entity types, operations)
- `adacli/docs/guide.md` (changesets)

## OPEN or ASSUMED

- OPEN: the entitlement for `set-rollout` in adacli (`changesets-rollout`)
  may be off for an instance. Say so if the command is refused.
