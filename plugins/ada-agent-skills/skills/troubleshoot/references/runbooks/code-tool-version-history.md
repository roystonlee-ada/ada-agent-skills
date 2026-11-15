# Compare or restore code tool versions

Use for code tool history and restoring an earlier saved configuration. A
changeset revert and a code tool version restore are different operations.

## Preconditions and steps

1. Open the tool in the dashboard and record its current code, input/output
   definitions, availability rules, block-in-simulations setting, environment
   values and Active state. Avoid copying secrets into the conversation.
2. Resolve unsaved edits before opening history. Compare the selected
   historical version with the current saved version. The latest 25 versions
   are available. Sensitive environment values are masked in the comparison.
3. Show the proposed restoration and get approval before restoring. Read
   Only users can compare versions but cannot restore.
4. Restore in the dashboard. This creates a new version. It restores code,
   inputs, outputs, availability rules and the block-in-simulations setting.
   It retains the current environment values and Active state. Check the old
   code still fits those current values rather than assuming an old credential
   or activation state came back.
5. Compare the saved result and test representative inputs, missing inputs,
   and the affected playbook path. A tool test alone creates no version.
   Check network side effects before testing a tool that writes externally.

Saving in the dashboard, updating through the API, and promoting changes
create versions. Existing tools start history with their next save, recording
the prior saved configuration as version 1. Do not promise older history.

## Downtime risk

A restore changes the saved tool configuration. An active tool may affect
subsequent calls. Confirm the intended environment and activation state, and
the scope of the change, before restoring.

## Rollback

Select the version recorded before the restore and restore it as another new
version. Current environment values and Active state are retained again;
restore those separately only with approval and a recorded prior value.

## Runtime boundary

Use the dashboard history viewer. The runtime references describe the current verification boundary. A normal code-tool edit
is not a substitute for an actual version restore.

Source: https://docs.ada.cx/2026-11-10-code-tools-version-history
