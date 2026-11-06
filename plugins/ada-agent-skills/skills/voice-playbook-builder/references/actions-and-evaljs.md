# Actions, status handling, and EvalJS as the logic module

## Wiring an action

- Outputs map JMESPath keys to variables (`variable_name` holds the variable **id**). Each output key is capped at **1024 characters** — the API returns a generic 400 past it. Minify, drop redundant clauses.
- Create and edit actions as `api_tool` entities on your changeset (the runtime file names the calls; read the live schema for the fields).
- Add an output with `source: status_code`, key `http_status_code`, mapped to a **numeric (long)** variable. Variable types are immutable after creation; create typed variables first (`edit_agent_config`, entity_type `variable`).
- Mapping the status variable disables the platform's automatic 4xx/5xx exit-and-handoff **only when the client has status-code output turned on** and a later IF reads that variable. With it off, any non-2xx is a hard step failure that hands off before your IF runs. The runtime file says how to read real calls for whether it is on. Where it's off, have the API return 200 with an error field and branch on that.
- **Sims skip the forced handoff**, so a sim can't prove a failure path. Prove it with the action test (the real response) plus one live failure, or the evidence from real calls above.
- Billing-API-style responses are often a dict keyed by id with scalar fields mixed in: filter with `values(@)[?type=='Subscription']` before touching fields; `contains()` on a null field crashes the whole output.
- Tokens expire (one API token lasted 900 s). Grab once at setup, once more right before the work loop.
- Same-named actions and variables differ across instances; compare outputs/inputs before reusing one. Prefer prefixed clones (`[Voice] <flow>: <action>`) over touching a live chat action.

## The status sentinel

```
SET status = "599"          ← sentinel
RUN action                   ← writes http_status_code into status (or doesn't, on transport failure)
IF status gte "400" → SEND honest failure → GO TO handoff
```
Every call gets one, and the failure takes a route you chose (checklist §7; shape in `patterns.md`). Two live patterns to copy:
- **Auth child** (a modular voice authentication playbook): after each lookup/verify call, `IF http_status gte 400 → SET
  error_fallback = True → GO TO exit`. The child never speaks the failure; the parent reads the flag and gives the unverified
  answer. It has no sentinel before each call, so a transport failure can inherit an earlier
  200; add one.
- **Cancel v2**: sentinel 599 before prep and before place → `gte 400` → one honest line → handoff with context.

Use `gte` only on numeric variables; a string status variable needs `is not "200" AND is not "201" AND is not "202" AND is not "204"` with a `"NONE"` sentinel. Async endpoints ("submitted") may return 200 or 202 — never gate success on one exact code. Repeat the sentinel for every call, including second runs of the same action.

## Code tools and MCP tools: a status field instead of a status code
They return what their code returns, with no HTTP code to check. Write the tool so it returns a `status` on every path,
caught exceptions included (`ok`, `not_found`, `invalid_input`, `error`), and bind it to a variable on the tool definition.
Then `GUARDED_TOOL`: SET status `NONE` → RUN (`target_type: mcp_tool`) → `IF status is not ok AND is not not_found → failure
route`, then branch on the specific statuses. A tool that never writes leaves `NONE`, which fails the check instead of passing.

## The WAF in front of Ada rejects some request bodies
Any dashboard write or inline test whose body contains a literal `...` (three dots) or HTML that looks like XSS comes back
as a **403 HTML error page** — from `PUT`/`POST web_actions`, from `web_actions/test`, and from the CLI's action update
(not a permissions problem). Build such strings at runtime (`E = "." + "." + "."`) and never feed raw upstream records into
EvalJS. Bisect a blocked body by swapping fragments for neutral text and probing each variant through the inline test
endpoint (side-effect free). `PUT web_actions/<id>` also wants `client_id` echoed back in the body (400 "Field required"
otherwise); the CLI's action update does the same fetch-merge-PUT for you.

## Read before you write
Two live playbooks for one intent on one client: the one that runs a read-only eligibility/status action before the write action had far fewer action failures and resolved more often. Look up, categorize, confirm, then write.

## Code Tools or EvalJS for the decision layer
Ada's authoring guidance now prefers **Code Tools** (sandboxed Python subset, `run` step with `target_type: mcp_tool` and the tool's id, enabled for the playbook) for new logic; EvalJS is the older mechanism and still works. Either way: one deterministic module makes every decision, its outputs bind to variables, and you test it with real inputs before wiring (the code-tool test for code tools — staging checks syntax only; the action test for EvalJS). Code-tool results are **not** visible to a contextual `send`; bind them to variables and reference `{{ variable:<id> }}`.

## EvalJS as the deterministic decision layer

Wire Ada's EvalJS endpoint as a web action (see the EvalJS docs for the URL on your instance):

```json
{"ada/code": "<one JS expression>", "wl": "{<var id>|}", "sel": "{<var id>|}", "pause": "{<var id>|}"}
```
Inputs are `{<variable id>|<default>}` placeholders, quote-free, read as `args.<key>`. Return an **array**; map outputs with keys `result[0]`, `result[1]`, … to variables.

What works (verified): arrow functions, `filter/map/reduce`, comma-expression assignment
(`(rows = …, sel = …, [out1, out2])`), regexes, ternaries. What returns null: `function(){}`, `return`,
plain-object results. A 2,200-character expression is fine.

Pattern — the categorizer: rows in a fixed `~`/`;` schema → every list the playbook later reads
(cancel ids/names, pause ids/names, skip names, cascade names, flags for offers, a count). Call it once after
selection and again after any decision that changes the lists (a pause acceptance). Check its status after
**both** calls.

Update an action's code through the runtime file's action update route. A raw PUT on the action endpoint returns 500 for
every body. Create returns `{"web_action_id"}`.

## Test any action inline, with literal values, without creating anything

`POST /api/generative_actions/web_actions/test` accepts `{"web_action": <full definition>, "test_inputs": {}}`.
Substitute `{<var id>|…}` placeholders with literals first (the CLI route's `action_test.py` does this). The outcome
carries `status_code` and `full_response` but not evaluated output mappings — evaluate the same JMESPath
locally to see exactly what each variable would receive. This is how a real cancel, pause and lookup were
proven on a test account before any caller reached them. Read-only calls are safe to run against prod;
anything that mutates (place cancel, pause) is single-use per account — spend it deliberately.

## Run the logic module against real data before trusting it

Harvest real payloads from conversation transcripts (read-only), run the lookup's JMESPath over them, then run
the categorizer over the resulting rows with every selection pattern (ALL, each id, pairs, base-only) and
every decision mode. Zero errors and no rule violations across a few hundred runs is the bar. The
cancellation build found free-trial rows dropped, blank app-store names, a pausable add-on on an unpausable
base, and "active" subscriptions with renewal dates years in the past this way.
