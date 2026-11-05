# Playbook editor will not load

Use when a playbook page stays blank, spins, or opens with an error, while
other playbooks open. A playbook that loads but will not turn Active is a
different case: the editor error menu names each error, so fix those.

## Preconditions

- Write access to the agent.
- The playbook's name and the time the page last worked.
- What changed last: a dashboard edit, a staged edit on a changeset, or an
  edit by someone else. The audit log shows who (see `audit-log.md`).

## Steps

1. Hard refresh the page, then open the same playbook in another browser or a
   private window. If it opens there, the cause is the first browser (cache or
   an extension). Stop here.
2. Open the playbook list at Config > Playbooks. If other playbooks open and
   this one does not, the cause is in this playbook.
3. Read the last change to it for the structures the editor reports as
   errors:
   - A section with no steps.
   - An `IF` or `ELSE IF` branch with no steps. An empty `ELSE` branch is
     allowed.
   - A `GO TO` step with no target.
   - A missing "When to use this Playbook" description, for a playbook that
     can run on its own.
4. If the last change was staged on a changeset that is still Testing, remove
   that edit from the changeset, or delete the changeset, then reload. If it
   was promoted, create a revert and hand it to `ada-promote-changeset`. Both
   paths are in `changesets-staging-revert.md`. A direct edit in the
   dashboard is not on the Change sets page, so put the old text back by
   hand.
5. If it still does not load, raise it with Ada support. Send the instance,
   the playbook name, the time it last worked, the time of the failure, the
   browser, any console error, and the checks above. Say what stays blocked
   until then: the person cannot edit that playbook in the dashboard.

## Downtime risk

None expected from steps 1 to 3, which only read. A playbook with errors can
be saved inactive but cannot be set Active, so an error alone does not put a
broken playbook in front of customers. Step 4 changes content, so check
whether the playbook is live first. A revert is live only after promote.

## How to verify

The playbook opens, the page header shows **Verified**, and the error menu
is empty. If it was Active, run **Test Playbook** once.

## Rollback

Step 4 is its own rollback: a withdrawn edit goes back by staging it again,
and a revert is itself reverted. For a hand edit, restore the text recorded
before the change.

## Source

- `product-docs/fern/versions/pages/docs/automation/playbooks/test-and-publish.mdx`
  (error menu, the editor's error list, save inactive with errors, Active
  toggle locked while errors remain)
- `changesets-staging-revert.md` (stage, remove, revert)

## OPEN or ASSUMED

- ASSUMED: an invalid structure can stop the editor loading, not only show an
  error. The docs say a saved playbook shows its errors when it opens, and
  they list no load failure.
- ASSUMED: a playbook that fails to load in the editor keeps serving its last
  active version to customers.
- OPEN: no doc names another cause of a playbook page that will not load.
  Ada support owns that.
