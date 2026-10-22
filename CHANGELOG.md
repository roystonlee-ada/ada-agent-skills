# Changelog

Each version has a section below. A push to `main` that changes the version
creates a GitHub Release with that section as its notes. To get an email for
each release, open the repo on GitHub, choose Watch, then Custom, then Releases.

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
