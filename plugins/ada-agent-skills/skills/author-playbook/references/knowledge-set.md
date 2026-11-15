# Knowledge in a reasoning SET

A reasoning SET can search Knowledge or reference a specific article to set
one variable. Use it to extract a policy fact that later steps need. If the
task must populate several variables, split the SET steps or use an existing
tool that supplies those values. An exact SET copies or clears a value
without a reasoning search.

The search budget is three searches per customer turn, shared across SEND
and reasoning SET steps. Design the whole turn around that budget rather
than giving every SET three searches of its own. Reference the relevant
article where appropriate and avoid repeated searches for the same fact.

If no answer is found, the SET writes its configured fallback, or clears
the value when there is no fallback. A previous value is not a safe fallback.
A variable default can reappear when the value is cleared, so an "Is not
set" branch may miss the failure. Choose a distinct unavailable fallback
where supported and branch on it before using the result. Do not run a
dependent action with an unavailable or defaulted policy value.

Test a supported answer, no matching answer, a prior value followed by no
answer, and an exhausted shared search budget. Confirm the stored variable
and branch, not only the visible reply. Runtime files own the tool schema:
inspect it before setting fields and use the dashboard if the host does not
expose the Knowledge controls.

Source: https://docs.ada.cx/docs/automation/playbooks/step-reference#search-knowledge-in-set-steps
