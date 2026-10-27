# Changelog

Each version has a section below. A push to `main` that changes the version
creates a GitHub Release with that section as its notes. To get an email for
each release, open the repo on GitHub, choose Watch, then Custom, then Releases.

## 2026.10.27

- New skill `ada-custom-metrics-loop`. It runs the custom metrics improvement loop for one metric or for every active metric: measure, check the judge, cluster the fails, stage and test a fix, ramp it, re-measure against a target, and go round again until the metric holds or the loop stops.
- `ada-custom-metrics-improve`'s health script takes `--metric` to report on one metric by id or part of its name.

## 2026.10.26.1

- `ada-image-cards` no longer falls back to a key derived from the card data when the runtime has no random `uuid4()`. It refuses to upload instead, because anyone holding the file key can mint a fresh link.

## 2026.10.26

- New skill `ada-image-cards`. It builds a per-customer image card that a playbook shows in chat: a code tool draws the card, turns it into a PNG, hosts it through Ada's file upload, and a send step shows it. It ships a local build and test kit, a font atlas builder and an optional QR code encoder.

## 2026.10.24

- `design-conversation` now lets the person choose between one question per turn and one message that lists every fact needed, with a short reason for each. `author-playbook` builds the listed version without asking again for facts already given.
- New design rules from a customer review: answer a side question and then return to the first issue, ask a follow-up only after its condition is confirmed, answer from the article that matches the question, vary the sorry line, keep the closing line true for every outcome, and offer a person only when the customer asks or the playbook cannot fix the problem.
- A reviewer's wording and tone corrections now apply to every board for that agent, and the skill reads the agent's voice notes first.

## 2026.10.22.2

- Fixed the design board so a title or name containing `</script>` or other markup cannot run as code.

## 2026.10.22.1

- The design board script now ships in the plugin, in `design-conversation/scripts/board.py`. Claude Code runs it from the plugin, so you no longer need Ada Architect's helpers to get the board.
- The board has the same look as the project tracker pages, with one tab per scenario.

## 2026.10.22

- `design-conversation` boards drawn in Claude Code now have a comment field on
  every turn, every scenario and the whole board. A Copy button in the top bar
  stays in view while you scroll and copies all comments for pasting into chat.
- The board opens in your browser once, then reloads the same tab on each round.

## 2026.10.21.1

- Claude Code now tells you at session start when a newer version exists, at
  most once a day, with the two commands to update.
- Each version now has a GitHub Release with these notes.

## 2026.10.21

- Added `ada-custom-metrics-setup` and `ada-custom-metrics-improve`.
- Added `create-verification-skill`.
- Fixed the MCP route for rollouts and promotes, so the skills no longer claim
  steps your permissions can refuse. They give you the dashboard step instead.

## 2026.10.20

- First release as `ada-agent-skills`, one plugin for the adacli and Ada MCP
  routes. It replaces `ada-architect-skills` and `ada-architect-skills-mcp`.
- Skills: `setup-adacli`, `setup-ada-mcp`, `design-conversation`,
  `author-playbook`, `revise-playbook`, `diagnose-conversation`,
  `review-handoffs`, `ada-promote-changeset`, `ada-rollout-changeset`,
  `ada-playbook-monitor-loop`.
- Added `ada-image-cards`.
