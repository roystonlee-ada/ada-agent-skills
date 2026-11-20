# Read a sensitive variable in a code tool

Source: https://docs.ada.cx/docs/automation/tools/code-tools/inputs-outputs-and-environment

Use this when a code tool must check a value the agent holds in a
sensitive-scoped variable: the last 4 characters of an ID, a date of birth, a
code the customer typed. The docs cover the basics: code can't read or write a
sensitive variable with `get_variable` or `set_variable`, so you declare it as
an environment variable with the **Sensitive Variable** source and read it with
`os.getenv`. This file covers what you hit when you build and test one.

## Wire the value in

- An input can't be linked to a sensitive variable. Use an environment entry
  for every sensitive value the tool reads, including the one the customer just
  typed into a sensitive variable.
- Over the MCP or the API, an environment entry backed by a variable looks like
  this. `value` is the sensitive variable's id, not its value:

  ```json
  {"key": "VALUE_ON_FILE", "source": "secret", "value": "<sensitive variable id>"}
  ```

- Read it with `os.getenv("VALUE_ON_FILE")`. Treat a missing or blank value as
  its own result (for example `missing`), never as a mismatch the customer can
  retry.
- A change set that modifies a code tool can't change its environment, inputs
  or outputs, so adding an entry later means a new tool. List every value the
  tool needs before you create it.

## Compare inside the tool

- Clean both sides the same way before comparing: trim spaces, drop
  separators, upper-case. Logs show the sensitive values only as redacted, so a
  format mismatch (`a1234` vs `A-1234`) looks exactly like a wrong answer and
  you can't see why.
- Return a category word into a normal text variable: `match`, `no_match` or
  `missing`. Never return the sensitive value, part of it, or a hint about it.
  The agent can see a code tool's outputs, and a customer can ask the agent for
  anything it can see.
- Branch with IF_ELSE on the category. The playbook never needs the value.

## Test it in two steps

1. **The logic.** At the time of writing, `run_code_tool` skips variable-backed
   environment entries, so `os.getenv` returns nothing there and every run
   looks like `missing`. If a dry run shows `missing` for values you know are
   set, this is why. Test the comparison with a copy of the code
   that takes the two values as plain inputs, and cover each category plus the
   format cases (case, spaces, separators, blank).
2. **The bindings.** Then run a real test case with both sensitive variables
   preset to known values (test cases accept presets for sensitive variables),
   once for a match and once for a mismatch. This is the only check that proves
   the environment entries point at the right variables. Read the result from
   the category variable and the branch taken, since the values themselves stay
   redacted in the run.
