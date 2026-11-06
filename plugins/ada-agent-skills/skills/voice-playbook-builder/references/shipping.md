# Setting up, staging and shipping

Everything goes through a changeset: edits are staged, validated, testable and reversible, and nothing reaches
callers until you promote. Read the live playbook schema before the first edit.

## 1. Find what exists before you create anything
- List the variables, handoffs, playbooks, tools, channels and actions.
- The greeting (Conversation Start): which variables it sets (channel, agents-online, caller ID, any dev flag), which it
  clears at the start of a call, and whether it runs playbooks directly. A playbook the greeting runs is never reached by routing.
- The auth child the voice playbooks already use, and the variables it sets.
- The handoff the live voice playbooks use. Confirm it transfers on voice.
- Any live playbook for the same intent. It will win routing over yours (see "Building inside a bot you don't own").

Reuse what fits. Same-named actions often use different variable names across bots, so compare inputs and outputs before
reusing one, and prefer a prefixed copy (`[Voice] <flow>: …`) to editing a live chat action.

## 2. Set up the pieces
- **Count before you design.** Count enabled tools against the bot's cap (sandbox bots
  default to 5), and actions, playbooks and handoffs the same way. Ada can raise a cap on request,
  so if the build needs more, ask the builder to request it rather than building a workaround, and never disable a live entity
  to make room.
- **Variables** go live as soon as you create them; they can't be staged.
  Give them a prefix and keep a list. Status codes need a numeric (long) type, and types can't change later. Show the builder
  the whole list once and get one approval, rather than one per variable.
- **Actions, code tools, the playbook**: create them on one named changeset. Staging runs the same validators as saving an active playbook in the dashboard, so an empty branch or a bad
  operator fails now, not at go-live. A playbook created in a changeset can't be edited in that same changeset: withdraw the
  edit (`remove`) and stage the create again (it gets a new id).
- **Changing a piece mid-build is expensive.** Changing an action or the child playbook means withdrawing and re-staging
  everything above it: action → child → parent. To avoid that, promote the actions and the child behind the dev gate first,
  so only the parent keeps changing. Keep step ids stable so `go_to` targets survive a rebuild.
- **Clearing at the start of a call**: list the call-scoped variables the build sets (auth flags, tokens, lookups,
  checkpoints, counters) and SET each to `NONE` in the greeting, so a new call starts clean but a caller who leaves and
  re-enters the playbook mid-call keeps their place. Stage it in the greeting where it uses the Conversation Start protocol;
  otherwise give the builder the block to add in the dashboard.
- **Code and MCP tools**: select the tool on a run step in the dashboard once, so it's enabled for the playbook.
- **Deviation settings**: set `on_human_request`, `on_off_topic` and `on_off_script` for the playbook, and on each ask that differs
  (best practices §06). They take effect only where the client's deviation switches are on. Check each ask's resolved values
  (the runtime file has the command).

You can stage the whole build in one changeset, or stage it in parts. Either works.

## 3. The dev gate: only test callers and sims reach it
Until the build is ready to ship, only your test callers and sims may get it. Any gate that guarantees that works. Pick one:
- **The caller's number** (simplest when building straight in prod; needs no greeting edit and no extra variable):
  ```json
  {"match":"all","conditions":[
    {"variable":{"id":"<channel var>"},"operator":"equals","value":"voice"},
    {"variable":{"id":"<phone_number meta var>"},"operator":"contains","value":"<tester's number>"}]}
  ```
  For more testers, nest an `any` group with one `contains` per number. Sims don't call from a team number, so run them
  before adding the gate, or set `phone_number` to a team number in the test case's `variables` (a meta variable; check
  the run reached the playbook).
- **A dev flag** the greeting sets when the caller's number is on the team's list. Suits long tester lists; needs the
  greeting edit in the same changeset.
- **Staged only:** test on the changeset and don't promote until it's ready (no live calls, sims only).

If the flow has a self-serve fallback, add a condition that its fallback flag is not set, so the flow can't fire twice in one call.

**Keep the gate on every change.** A change to a gated playbook's steps alone can produce a promote preview without the
gate. On every change: send `availability_rules` with it, check the promote preview shows the gate, and read the live
playbook back after promoting.

## 4. Promote, call in, then open it up
1. Promote the changeset. The first call returns a preview; a person confirms.
2. Call in from a team number and run each path (`testing.md` §2). Remove test values (a TEST FIXTURE section, test-number
   mappings) in a new changeset when done.
3. Open it up with a new changeset that removes the dev condition. To go gradually, set a rollout on that changeset (a percentage and a conversation cap): a random slice of new conversations gets it, up to the cap, and stopping the rollout ends it.
4. Read the first twenty real calls.
5. **Rollback:** revert the promoted changeset. It builds a new changeset that undoes it; promote that.

Before promoting to everyone, check:
- The description lists real caller phrasings **and** the sibling intents that must not trigger it.
- Every path ends in `run exit` after a closing line, or in a handoff.
- No TEST FIXTURE section; no hard-coded test values.
- General instructions are a few named rules, not a second copy of the steps.
- One live playbook per intent.

## 5. Testing changes to a live playbook
A real call only reaches promoted playbooks, and promoting a change to a live playbook puts it in front of every caller it
serves. Adding a test gate to it would cut those callers off. Choose:
- **Sims on the changeset only.** Nothing live changes. Enough for most wording and logic changes.
- **A gated copy.** Stage a copy of the playbook with the change, gated to test callers (§3). In the same changeset, add
  "caller's number does not contain <tester>" to the live playbook's rule, so testers reach only the copy and real callers
  only the original. Promote, call in, then delete the copy and the extra condition in one changeset.
- **A small rollout.** Start a rollout at a low percentage and a conversation cap, read those calls,
  then raise it or stop it.

## Changeset limits worth knowing
- Existing `note` steps must be sent back unchanged, in place, whenever you rewrite `sections`, or they are deleted.
- A playbook with send-step attachments (images) can't have its sections edited here.
- `reason` steps can't be added (they still run where they exist).
- A modify inherits `enabled` from the live version unless you set it.

## Building inside a bot you don't own (a customer's live bot)
Platform facts that each cost a build a day:
- Variables go live when created. Prefix them, list them, and clean up in order: delete the changeset first, then the
  variables (deletion is refused while anything references them).
- A staged create accepts only: name, description, enabled, sections, general_instructions, acknowledgment_instruction,
  chat_acknowledgment_override, availability_rules, on_human_request, on_off_topic, on_off_script.
- If the greeting runs the competing playbook directly, stage a changeset-only IF in the greeting (test variable → yours,
  else theirs).
- A live playbook for the same intent wins routing over a staged one. Stage theirs as disabled inside your changeset only,
  give yours a test-only trigger, or use a separate bot.
- Tools write to their own fixed variables. Use the owner's variables, or copy the tool with a prefix.
- The greeting isn't yours to change. Don't clear your values at the top of your playbook: that breaks resume for a caller who
  leaves and comes back. Give the greeting's owner the clearing block to add, or stage it changeset-only alongside the test IF.

## Moving a build between bots (sandbox → prod)
- Every variable, action, handoff, article and playbook id is bot-specific. Remap by name, with explicit overrides where the
  prod counterpart is named differently. Texts can embed `{{ variable:<id> }}` too, so remap those as well.
- Check there are zero ids from the old bot anywhere in the sections before staging.
- Read every created action back and compare url, method, body, headers and outputs.

## Co-editing with the dashboard
People edit titles and steps in the dashboard while you stage from chat. Before every update, read the live playbook
(the changeset diff shows what yours changes against live) and keep their edits. Never
regenerate and overwrite.
