# Team members, roles and access

Use when the person wants to add or remove a user, change a role, or add one
person to several Ada instances.

## Preconditions

- Owner or Admin role. Admins cannot change an Owner, and nobody can change
  their own role.
- The new user has a business email domain.

## Steps

1. Read the current member list and roles, and record it.
2. Add the user in the team page with a role: Owner (full access), Admin
   (full access except editing Owners), Agent (edits content, coaching,
   persona, branding and variables) or Read Only.
3. The invite link expires after 24 hours. After that, the user picks
   "Forgot Your Password?" to set one.
4. To change a role, pick the new role. It saves at once, emails the user and
   reverts if the update fails.
5. Someone on more than one Ada instance needs a separate add on each one.
6. Only Owner or Admin can edit integrations (channel settings, webhooks),
   redactions, approved domains, API keys and the team.

A change of login email is not in the docs. Write OPEN and tell the person to
ask Ada support. Do not offer a workaround.

## Downtime risk

None expected. A role change applies to the user's next action, and MCP
access follows the role on the next call.

## How to verify

Read the member list again and confirm the role. Ask the user to sign in.

## Rollback

Change the role back to the value recorded. Remove an added user from the
team page.

## Source

- `product-docs/fern/versions/pages/docs/other/team-access/my-team.mdx`
- `.../team-access/profile.mdx` (what a user can change about themselves)

## OPEN or ASSUMED

- OPEN: the CLI accepts the roles admin, manager and agent, and the docs list
  Owner, Admin, Agent and Read Only. The mapping is not documented. Use the
  dashboard for Owner and Read Only.
- OPEN: login email change and billing are not in the docs. Ask Ada support.
