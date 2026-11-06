# A readable promote diff

The person approves a promote from this diff. They should see which thing
changed and what it says now, with no second lookup.

## Why the default view is not enough

- Each change is listed by entity ID, such as `6aebca17...`, not by name.
- A long field, such as a playbook's `availability_rules`, can be cut off part
  way, so the routing rule the person is approving is not on screen.

## Build the view

1. Read the full diff (the runtime file gives the call). Each change has an
   entity type, an entity ID, a change type (`created`, `modified`, `deleted`)
   and, per field, a `before` and an `after`.
2. Name each entity. Look up the ID with the runtime file's call and write
   "Refund playbook (playbook)", not the ID. Put the ID in brackets after the
   name for lookup. If a name cannot be found, write "name not found" and keep
   the ID. Never guess a name.
3. Group the changes by entity, one block each, in this order: playbooks,
   knowledge, coaching and custom instructions, then everything else.
4. For each changed field, show `before` and `after`. Show routing and
   availability rules (`availability_rules`, triggers, conditions) in full, word
   for word. Never shorten a rule. For other long text, show the changed
   sentences and say how many characters the field has in all.
5. A field that did not change is left out. If the diff is empty for an entity,
   say so instead of skipping it.
6. Check you have not dropped anything: the number of blocks equals the number
   of changes in the changeset. Say the count.

## Say what it means

Under each playbook block, add one plain line on the effect, for example "The
refund playbook now runs only when the customer names an order." Mark it as
your reading, and keep it apart from the platform's text, so the person can
check it against the real diff.

## If live moved

Compare against the live version before you show the diff. If live config
changed after staging, say which entities moved and offer to restage.
