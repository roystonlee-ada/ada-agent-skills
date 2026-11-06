# Anchor from a requirements sheet or doc

Use this when the customer's "what good looks like" lives in a Google Sheet,
a CSV, or a doc with one row or section per scenario. The sheet is the anchor:
cases come from its rows, and no criterion comes from you.

## 1. Read it

- Google Sheet or Doc: use a Drive or Sheets tool if the host has one. Read the
  whole tab, not a preview.
- No such tool: ask the person to download the tab as CSV, or paste the rows.
- If the file has several tabs, ask which one holds the scenarios.

Count the rows and say the number before you map anything.

## 2. Map the columns

Find these by header, and show the person your guess before you use it:

| Case field | Usual column |
|---|---|
| `name` | Scenario name or ID, written "<Use case>: <scenario>" |
| `user_message` | What the customer says (first message) |
| `scenario_goal` / `scenario` | Context, facts the customer gives later, the customer's aim |
| `success_criteria` | Expected outcome, one criterion per distinct thing the sheet requires |

- Copy the sheet's words. Split one expected-outcome cell into several
  criteria only where it lists several outcomes.
- A "must not" in the sheet becomes its own criterion.
- Keep the row number or scenario ID in the case name, so a failure traces back
  to its row.
- Follow `author-playbook/references/test-cases.md` for the field rules.
- Put no real customer data in a case. Use fakes of the same shape.

## 3. Check before saving

- Show the first two or three mapped cases. The person confirms the mapping,
  then you map the rest.
- A row with no expected outcome, or an outcome too vague to judge ("handles it
  well"), is not a case. List it as a question for the person.
- Rows that contradict each other, or contradict the customer's own policy
  text, go back to the person as questions. This is the "case wrong" kind in
  step 4.5. Do not reword a row so it passes.
- Report the counts: rows read, cases ready, questions raised.

## 4. Save and carry on

Save the approved cases with the runtime file's create call. From here the
saved cases are the anchor, and the sheet row IDs in their names link each
result back to the sheet. Pick controls, then continue at step 2 of the skill.
