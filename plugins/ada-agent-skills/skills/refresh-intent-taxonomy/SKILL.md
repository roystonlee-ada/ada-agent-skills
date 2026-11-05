---
name: refresh-intent-taxonomy
description: >
  Refresh an Ada AI agent's Topics and Intents from its AI-recommended intents
  and real conversations, then save a taxonomy snapshot so later analysis uses
  today's vocabulary. Use it whenever someone says "refresh the intents",
  "update topics", "are the intents stale", "review recommended intents",
  "what are customers asking about now", "the topic breakdown looks old", or
  before any analysis, report or business review that groups conversations by
  topic or intent. Also use it on a monthly schedule.
---

# Refresh intent taxonomy

Ada files each conversation under a Topic and an Intent. The list ages:
customers ask new things, and Ada surfaces **recommended intents** for
conversations that fit nothing. Analysis on a stale list files new demand
under "other". Refresh the list, then save a snapshot that later work loads.

A Topic or Intent edit changes **new** classifications only. Old ones stay, so
say so in any before-and-after comparison.

## 0. Pick the runtime

Each step names what to do, not a command. Read one file for how:
- Ada MCP tools present (`get_conversations`, `list_entities`) → `references/runtime-mcp.md`
- `adacli` on the path → `references/runtime-cli.md`

Neither route lists recommended intents or approves them. Those steps use the
dashboard, Analytics > Topics & Intents. The runtime file says which steps.

## 1. Pull the current taxonomy and recommendations

Read the active Topics and Intents with their scope, signals and excludes. Read
the recommended intents with their volume and trend, and the share of
conversations in the "other" and "unclassified" buckets. An "other" share above
about 20% means the list no longer covers what customers ask. A mostly
recommended taxonomy is normal for a new agent.

## 2. Check each recommendation against real conversations

Take the top recommendations by volume, not a small sample. Read three
conversations for each. Count test-user traffic apart from real traffic,
because a recommendation built on test chats is noise. Mark each one:
- **Approve**: a distinct reason that no active intent covers, in real traffic.
- **Merge**: an active intent already covers it. Fix that intent's signals instead.
- **Dismiss**: noise, a one-off, thin, or driven by test users. Say why.

Link samples as `https://<host>.ada.support/insights/conversations/<id>`. Mark a
link opened, read through the tools, or ASSUMED when you saw only a summary.

## 3. Check active intents for drift

Flag an active intent when its volume fell to near zero across two windows, when
two intents overlap, or when its excludes text no longer matches what customers
say. When scope, signals or excludes are empty, propose filling them. Keep
names under 128 characters and descriptions under 1,024.

## 4. Write the proposal

Show the current and proposed taxonomy, the volume behind each change split
real from test, the sample links, and open decisions last. Mark it "Proposed,
not built". When most recommendations are test noise, lead with that: approve a
few, dismiss the rest, no taxonomy change.

## 5. Apply only what the person approves

Approve, dismiss and in-place edits use the dashboard. New Topics and Intents
can use the runtime. Never delete a Topic that has live volume, because deleting
a Topic also deletes its Intents. Tell the person each change is live at once.

## 6. Save the snapshot

Ask where to keep it. Default to `intent-taxonomy.md` in the working folder, and
replace the file each run. Include:
- Date, agent instance, window, and whether any count was capped.
- Active tree: Topic > Intent, one-line scope, volume, resolution rate, CSAT when you have them.
- Recommended intents still open: name, volume, real versus test, verdict.
- The "other" and "unclassified" shares for the window.
- Changes this run, with the date each new intent went live.

## How later analysis uses the snapshot

Load the snapshot before grouping conversations. Use its names as the
vocabulary, and do not invent topic labels. Treat a snapshot older than 45 days
as stale and run this skill first. Report the "other" share so a growing gap
shows. History before a new intent's go-live date is not comparable.

Offer a monthly run once if the person wants one. Do not set it up unasked.
