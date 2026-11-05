# Session timeout and session limits

Use when the person asks why users get signed out, or wants a shorter or
longer dashboard session.

## Preconditions

- Owner or Admin role.

## Steps

1. Open the avatar menu in the dashboard, then Session limits.
2. Read both values and record them: Active session limit and Inactivity
   timeout. The inactivity timeout cannot exceed the active session limit.
3. Change a value and save.
4. A stricter limit than the dashboard allows goes through an Ada
   representative.
5. adacli sessions follow the instance's inactivity timeout (24 hours by
   default in the CLI guide). Exit code 3 means log in again.

## Downtime risk

None for the AI Agent. Users with a shorter limit are signed out sooner.
Warn the team before shortening.

## How to verify

Open the page again and confirm the saved values. Check the audit log for a
Session limits entry.

## Rollback

Set the values back to those recorded in step 2.

## Source

- `product-docs/fern/versions/pages/docs/other/team-access/session-timeout.mdx`
- `adacli/docs/guide.md` (session lifetime)
- `api/core/analytics/audit_log/stores/clickhouse.py` (Session Limits label)

## OPEN or ASSUMED

- OPEN: the default values are not in the docs. The 24 hours is the CLI
  guide's figure for the inactivity timeout.
