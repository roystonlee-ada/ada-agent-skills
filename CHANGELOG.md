# Changelog

Each version has a section below. A push to `main` that changes the version
creates a GitHub Release with that section as its notes. To get an email for
each release, open the repo on GitHub, choose Watch, then Custom, then Releases.

## 2026.11.11.6

- New skill `prevent-handoffs`. It gives every handed-off conversation in a window a verdict: preventable, or not because the customer asked for a person, policy needs a person, or the agent lacks system access. Each verdict carries the reason and evidence. It groups the preventable ones by root cause, ranks them by conversations, drafts a knowledge, playbook or action fix for the top causes on a changeset, seeds test cases from the real handed-off conversations, and replays them with `test-and-fix`. A fix stays only when most of its targets now end without a handoff and the controls hold. The report is a ranked list: fix, cause, conversations affected, contained x of y, projected containment gain and links. It never promotes. On a read-only instance it stops at the proposed fix list.
- `ada-agent-guide` routes "which handoffs could the agent have kept" to `prevent-handoffs`.

## 2026.11.11.5

- The README has a new rule for contributors: only generally available features go in a skill. Leave out anything docs.ada.cx marks as Early Access, beta, preview or limited availability. Custom Metrics is an approved exception while it moves to general availability.
- `author-playbook` no longer says Messenger, Instagram, LINE and WhatsApp draw quick-reply buttons. The docs.ada.cx step reference supports quick replies on Web Chat and the Messaging SDK only, and says other channels are not supported yet. The label rules stay as design rules: 20 characters or less, all different, 10 values or fewer.
- `configure-handoff` no longer calls the Salesforce SMTP Connector early access. Its live docs page is in the docs menu and has no Early Access label.

## 2026.11.11.4

- `voice-playbook-builder` lists the SMS opt-out words (`STOP`, `UNSUBSCRIBE`, `END`, `QUIT`, `STOPALL`, `CANCEL`, `REVOKE`, `OPTOUT`), warns against texts that ask for one of them as a reply, and says that with your own SMS channel your provider handles opt-outs. Source: docs.ada.cx, SMS consent and Voice onboarding.

## 2026.11.11.2

- `configure-handoff` checks that every Conditional block in a handoff has an Else. With no Else, a customer who matches no condition gets no handoff and no message. Source: docs.ada.cx, handoff Conditional block.
- `configure-handoff` checks the Human Agent CSAT survey on the return path. It rates the human agent apart from the AI Agent survey, and a suppression rule keeps it from showing when the handoff never reached a person. Source: docs.ada.cx, CSAT survey configuration.

## 2026.11.11.1

- `design-conversation` designs flows where a code tool emails the customer mid-chat (a one-time code, a confirmation, a receipt). The bot turn says the email went out and names the address in part, every such flow gets a "didn't get it" scenario, and a failed send never reads as sent.
- `author-playbook` has a new `references/code-tool-email.md` for `send_email` in a code tool: branch on `sent`, keep a one-time code in a variable the agent cannot read, the per-conversation, per-address and per-agent limits, and how a test run treats a send. Source: docs.ada.cx, code tools, "send_email".

## 2026.11.07.2

- `design-conversation` designs to what each channel can show today. New `references/channel-features.md` lists the published features that change a sample conversation, per channel, each with its docs.ada.cx source: quick replies on ASK steps, hidden keyboard input, progress messages while a tool runs, who writes first, greetings, images, and email variables and trusted senders. It also has the steps to refresh it from the release notes, so a new feature changes one file.
- New design rules: on Email and social channels, and on Web Chat with a conversation start event, every scenario starts with the customer's message, with no greeting. A bot turn can set `hide_keyboard` only on Web Chat and the Messaging SDK. A slow API or code tool shows a progress line when progress messages are on.
- Quick replies on an ASK step show as buttons on Web Chat and the Messaging SDK, the only channels the docs.ada.cx step reference supports. Every other channel gets a plain list of the values to type back, with no numbers. Labels stay at 20 characters or less.
- The board script draws options as buttons on Web Chat and the Messaging SDK, and as a plain list everywhere else. It warns when an email or social scenario starts with the bot, when an `options` list has fewer than 2 or more than 5 labels or a label over 20 characters, and when `hide_keyboard` is on a channel that keeps the message box.
- Boards now show each channel's features: the overview has a "What these channels show" card (quick replies, typing, who starts, progress messages, and one email per reply on Email). A bot turn with `"progress": true` draws as a progress message, Email turns are labelled as emails, and a plain list no longer runs into the question text.

## 2026.11.07.1

From a customer's review of the skills (07/11/2026). Each change was checked against the adacli 1.4.0 source or the platform code first.

- Removed adacli commands are gone from the skills. `snapshot diff` (removed in 1.0) becomes an export to a second folder and `diff -r`. `knowledge probe` (removed in 0.13.1) becomes `knowledge list` plus asking the question in `chat talk`. `snapshot export --include` and `chat talk --transport` no longer exist, so they are dropped too.
- `troubleshoot` adds the knowledge sync schedule flags (`--sync-at`, `--sync-days`, `--timezone`) next to `--sync`, which still works.
- Logged-in checks read `status --json` for `connected`, because `status` exits 0 when logged out. Scripts can treat exit 3 on a cheap read as logged out (`setup-adacli`, `configure-handoff`, `troubleshoot`, `onboard-agent`, `create-verification-skill`).
- `ada-rollout-changeset` uses the 90% cap across active rollouts (10% always stays on live) and says that a rollout completes silently when it hits its conversation cap.
- `ada-promote-changeset` checks `status: promoted` in the JSON, not the exit code, explains the stale-copy warning and says to keep one open changeset per entity.
- `refresh-intent-taxonomy` lists the intent recommendation commands added in adacli 1.2.0.
- `author-playbook` has a new `references/build-pitfalls.md` with eight checked build mistakes, and the test-case guide says to leave an empty variable out instead of presetting `""`.
- `check_ask_instructions.py` rule A4 now flags an ASK with zero re-asks and no fallback when a later action runs with no `is null` check. The old accept-any wording warning moves to A8 with softer wording. Tests in `evals/test_check_ask_instructions.py`.
- `improve-agent` sizing adds a known-positive and empty-input check for text-matching counts, and says to cover every language. `test-and-fix` says what to do when the test quota reads far below 3,000.
- New `evals/check_cli_commands.py` checks every adacli command and flag the skills name against `agent-context`, and diffs command lists after an upgrade. Baseline in `evals/adacli-commands.json`.

Checked on a sandbox (07/11/2026) and added:

- `author-playbook` build pitfalls add three rows. A yes/no pill prints `True` or `False` in a send. A full-sections stage that leaves out `reasoning_level` turns a High step into Normal with no warning, so start from `export-steps --sections`, which carries it. An action output's `variable_name` takes the variable ID, and a name there makes every call fail.
- The test-case guide says a mocked tool that runs writes its answer over a preset variable.
- `test-and-fix` `safe-to-run.md` and `configure-handoff` say a Send Email app step is mocked in a test run, and a Salesforce email handoff is not: it sends for real.
- `diagnose-conversation` reads what a SET or tool wrote from `conversations reasoning --json`, because the text `conversations log` never prints variable values.

## 2026.11.06.4

- `test-and-fix` accepts a customer's requirements sheet or doc as the anchor. Many customers keep "what good looks like" as one row per scenario. The new `references/anchor-from-sheet.md` covers reading the sheet, mapping its columns to case fields, showing the first rows for approval, and sending vague or contradictory rows back as questions instead of rewording them. Based on feedback from a Claude run on a customer sandbox (06/11/2026).
- `ada-promote-changeset` shows a readable diff. New `references/readable-diff.md`: read the diff as JSON, name each changed entity instead of its ID, show routing and availability rules in full, and check the block count against the changeset. The default view lists IDs and cuts off long fields such as `availability_rules`.

## 2026.11.06.3

- Fix the README routing diagram. 2026.11.06.2 also drew the Install table's "Claude Code" and "Codex" rows as extra columns, with overlapping text. It now reads only the Stage table, and the build stops if the table lists a skill that has no folder.

## 2026.11.06.2

- The routing diagram in the README now reads its skill groups from the Stage table, and the build redraws it every time. It had lagged the table: it was missing `voice-playbook-builder` and `ada-tune-reasoning-level`. The "New in this release" highlight is gone, since nobody kept it current.

## 2026.11.06.1

- New skill `voice-playbook-builder`. It builds, tests and ships V2 playbooks for phone calls: a design checklist, ready patterns (verification, failure branches, confirm-then-write, SMS), how the voice engine treats corrections, exits and API failures, simulation testing, and a staged rollout. It works over adacli or the Ada MCP. Based on Marc M.'s Voice Playbook Builder v1 (Ada, 06/11/2026).
- `design-conversation`, `author-playbook`, `revise-playbook` and `diagnose-conversation` now point to it when the channel is voice.
- The build now also blocks engine source paths and the name of the customer the voice skill came from.

## 2026.11.05.4

- `author-playbook` now tests every complicated SET and ASK step at both Reasoning levels before it stages. A complicated step has several rules, a precedence order, a long list, arithmetic, or several variables at once. It loads `ada-tune-reasoning-level`, runs the step's own inputs at Normal and at High, and keeps the level that gets more right. A tie keeps Normal, because High is slower and has no second model behind it. A simple step stays at Normal with no test.
- `ada-tune-reasoning-level` says in its description that `author-playbook` loads it.
- New script `author-playbook/scripts/check_ask_instructions.py` checks the instruction of every reasoning-mode ASK step in a playbook, changeset or folder of them. It fails an ASK that never says a problem reply means "no", or that tells the model to repeat the question word for word, and warns about a missing re-ask line, re-ask cap or fallback value. It exits 1 on a FAIL. No skill calls it yet.
- `help-center-to-kb-playbooks`: `extract_help_center.py` now connects to the address it checked. It resolved the host name once to check it and again to connect, so a DNS server that changed its answer in between could send a fetch to an internal address. It now resolves once, rejects any non-public address, connects to that address with the original host name for TLS, and checks the connected peer. It also uses the scheme's default port (80 for http) in the check.

## 2026.11.05.3

- `author-playbook` now builds every SET and ASK step at Reasoning level Normal and leaves `reasoning_level` off. In our runs High fixed only date and weekday arithmetic, so a long instruction is not a reason for it. When a step still saves a wrong value in tests or real chats, it loads `ada-tune-reasoning-level` and tests Normal against High on that step's own inputs.
- `revise-playbook` now sends every step's `reasoning_level` back as it read it, because a rewrite that drops the field sets the step to Normal without a warning. It loads `ada-tune-reasoning-level` before rewording a step that saves a wrong value.

## 2026.11.05.2

- `author-playbook` now sets rules for quick-reply labels. On Messenger, Instagram, LINE and WhatsApp, a question shows buttons only when every title is 20 characters or fewer, no two titles match, no title equals another value, and there are 10 options or fewer. If one title is too long, the whole question turns into a text list of the raw values, so a customer can read `did_not_answer` as a line of text. The new `references/quick-replies.md` has the rules and shortened examples. The new `scripts/check_quick_replies.py` checks a playbook file or a changeset file and exits 1 on a bad label.
- The draft step in both runtime files now checks the labels before it stages a changeset.
- Keep a status value such as `did_not_answer` out of the accepted values unless a branch tests it. If a branch does test it, give it a label.

## 2026.11.05.1

- Test cases from real conversations now use Ada's new draft tool. In the MCP it is `draft_test_case_from_conversation`. In adacli 1.1.7 it is `testing cases from-conversation <id> --json`. Both return a screened draft (personal details become fakes of the same shape, credentials and sensitive variables are left out) and save nothing. The draft carries an `instructions` field, and the skills follow it for write, preview, save and run.
- `author-playbook` test-case guide has a new section 8, "Seed a case from a real conversation". It adds what the draft does not decide: agree the outcome with the person first (never copy what the agent did), mark a failed chat as a target and a good chat as a control, draft only (never copy from `get_conversation`), read the preview for personal data, check an empty opening message, describe the external systems from the draft, and set every tool the chat called to mock before the first run. A run that fails with `simulation_not_covered` is a wrong case, so the fix goes in the case's external systems text and not in the agent.
- `test-and-fix`, `diagnose-conversation`, `ada-promote-changeset`, `ada-playbook-monitor-loop` and `create-verification-skill` use the new tool in their runtime files. The `--create`, `--name` and `--criteria` flags are deprecated, and `test-and-fix` says so. `revise-playbook` drafts extra controls from real chats when a rewrite replaces a playbook with few saved cases.
- New skill `mine-human-agent-conversations`. It reads the replies that human agents sent after a handoff, finds the path most of them follow, and places each cluster on a rung (answer, collect, look up, resolve, or stay human). It checks what already exists, then writes a playbook candidate card with a size, the resolvable share as "k of n", the policy to confirm, two or more conversation links and three conversations to seed as test cases. It checks first that the handoff integration returns replies at all, and says what to ask for from the helpdesk when it does not. It only reads.
- `improve-agent` now loads the new skill for its handoff clusters, in place of its own copy of the human-reply guide. The source check and the helpdesk export request moved into the new skill.

## 2026.11.04.1

- adacli read-only mode is now part of setup. `setup-adacli` has a new step, "Read-only or read-write": it reads the instance's full domain from `adacli status --json`, shows the `read_only=` line, adds it to `~/.adacli/config` after your yes, and confirms with `status`. It uses the full domain because a short handle matches nothing and adacli gives no warning. The check script now lists the `read_only` entries and warns about any entry with no domain.
- Exit code 7 means the instance is read-only. Every skill that writes now checks `status --json` for `read_only` before it plans a change. On exit 7 it stops, names the change it was about to make, and leaves `~/.adacli/config` alone, so the person decides whether to lift the setting.
- `setup-ada-mcp` explains the MCP equivalent: the Agent and Read Only roles get read tools only, and the Ada server enforces them.
- `ada-agent-guide` sends a read-only instance to the skills that only read: `diagnose-conversation` (untested), `review-handoffs`, `ada-report`, `improve-agent` (ranking only) and `troubleshoot`.
- The monitor and custom-metrics loops split watch ticks, which only read and can run read-only, from fix ticks, which stage changesets and run tests.
- Read-only blocks test runs and simulations, so a read-only instance cannot prove a fix. Build and test on a second instance that is not read-only.

## 2026.11.03.2

- `author-playbook` test-case guide: after you reword criteria, measure the fix by the failed checks on the edited criteria, not by how many runs pass. In the audit they fell from 14 to 4 of 22 while runs passing stayed flat, because a fresh run resamples the bot and the judge and the remaining failures are scattered real defects. Do not forecast a new pass count from old runs.

## 2026.11.03.1

- `author-playbook` test-case guide has a new section on wording the judge reads literally. An audit of a 44-case suite found that two shared criteria ("asks at most one question", "does not ask for what the customer already gave") caused a quarter of all failed checks, and about half of those were the judge misreading a fair reply. The section says how to define the unit, allow the first ask, drop "may", split compound criteria, ask for the claim and not an exact reason, check each target against the real tool, and check a suite before you trust it. `revise-playbook` uses the same guide.

## 2026.10.30.4

- New skill `refresh-intent-taxonomy`. It reads your agent's Topics and Intents, checks the AI-recommended intents against real conversations (test chats counted apart), flags active intents that have drifted, and writes a proposal. It applies only what you approve, then saves a taxonomy snapshot as a markdown file you choose. Later analysis loads the snapshot and treats it as stale after 45 days. Neither adacli nor the MCP can list or approve recommendations, so the skill sends those steps to Analytics > Topics & Intents in the dashboard. The CLI route needs adacli 1.1.0 or later.

## 2026.10.30.3

- Renamed `ada-reasoning-level` to `ada-tune-reasoning-level`, so the name says what the skill does. Nothing else changed. If you installed the old name, update the plugin and use the new one.

## 2026.10.30.2

- New skill `ada-reasoning-level`. It finds the SET and ASK steps worth running at Reasoning level High, tests each one on its own inputs, and stages the change on a changeset. In our sandbox runs High fixed date and weekday arithmetic (17 of 17 right, against 18 of 34 at Normal) and gained nothing on most other tasks, so the skill tests step by step and moves High steps that gain nothing back to Normal. It never promotes.

## 2026.10.30.1

- Fix for Codex and other hosts outside Claude. The `create-verification-skill` description held an XML-style tag, which their skill loaders flag. It now uses plain words. The build now fails if any skill's frontmatter holds a tag.

## 2026.10.28.5

- Start with `/ada-agent-guide`. The README now opens with it and a diagram of where it sends each request. You do not need to remember the skill names.
- New skill `onboard-agent`. It reads your agent and marks each setup stage done, partial or not started, with evidence. It asks only what the setup cannot show, then hands you to the skill for the next stage. It lists what each channel needs.
- New skill `test-and-fix`. It runs a use case's saved tests, sends each failure to `diagnose-conversation`, fixes it on a changeset and runs every case again. It stops when all pass, after three rounds, or when a fix changes the design. It never promotes, and it holds any case that could reach a live queue.
- New skill `improve-agent`. It ranks improvements across the whole agent by how much each moves handoffs, containment, CSAT and custom metrics. Each recommendation names its situation, its size, the mechanism, two or more conversations and the next skill.
- New skill `configure-handoff`. It sets up and fixes handoff to Zendesk, Salesforce, Gladly, email and the other platforms in Ada's docs. It checks the chain in order, from trigger to return path, with one reference file per platform.
- New skill `troubleshoot`. It answers Ada platform and account questions from a library of runbooks. Every answer gives the steps, the downtime risk, how to verify, the rollback and its source.
- `ada-agent-guide` routes to the five new skills. A "why did it" question goes to `diagnose-conversation`, and a "fix it and prove it" request goes to `test-and-fix`.
- `diagnose-conversation`, `author-playbook`, `revise-playbook` and `test-and-fix` link each conversation as `/insights/conversations/<id>`, the address the dashboard uses.
- `author-playbook` lists the real adacli test case fields: `name`, `user_message`, `scenario`, `success_criteria` and `language`.
- `configure-handoff` treats every handoff and integration change as live, because neither sits on a changeset. It backs up first and asks before each write. When every link checks out and the handoff still fails, it tells you to raise it with Ada support and what stays broken until then.
- `troubleshoot` ends every answer with the same escalation step, and has a runbook for a playbook editor that will not load.
- After runs on real agents: `onboard-agent` reads your setup in one call and states what it finds instead of asking. `configure-handoff` checks your off-hours text against the schedule, expired holidays, handoffs that do not count in metrics, and more than five live handoffs. `improve-agent` checks containment against real handoffs per channel before it ranks anything. `review-handoffs` gives plain adacli commands.
- `test-and-fix` still diagnoses a failure from an earlier run while a case waits on a tool or handoff check. It stages no fix until that case runs.
- The eval suite gives `onboard-agent` and `configure-handoff` a reply per setup area and puts each judge's pass condition in the line the judge reads.

## 2026.10.28.4

- `help-center-to-kb-playbooks` fetches only http and https URLs, including redirects and image links. A page can no longer make the script read a local file with a `file://` link. It refuses hosts on private, loopback or link-local addresses unless you pass `--allow-private`. It names each saved image from a fixed list of image types, not from the server's header.

## 2026.10.28.3

- New skill `help-center-to-kb-playbooks`. It turns a help center into KB articles and playbooks. It sorts each article into fact, procedure, decision or action, merges articles that answer the same question, and flags articles that have not changed in 2 years. It decides what each image is for, and attaches the ones that show where to act to playbook send steps. It holds screenshots of partner products and flags images too tall for chat or that show personal data.
- `scripts/extract_help_center.py` finds every article from an index page, downloads the articles and images, and writes a manifest with edit dates and image sizes. It warns when a page holds no readable text.
- Images attach last, in the dashboard. A changeset cannot edit an attachment, and a playbook with an image cannot have its sections edited through a changeset.

## 2026.10.28.2

- `ada-report` rebuilds each transcript link from checked parts. It refuses a URL with a backslash, whitespace, a control character, a user name, a password or a port, because a browser and the script's parser read those differently.

## 2026.10.28.1

- `ada-report` drops a transcript link unless it is https on an Ada host, and adds `rel="noopener noreferrer"` to the links it keeps. It now masks emails, phone numbers and long numbers in transcript titles, option labels, photo descriptions, note labels and the on-page warnings, not only in message text.

## 2026.10.28

- New skill `ada-report`. It builds an Ada-branded report on how an AI Agent is performing, from real metrics and conversations. If the person has not said who reads it, for which period or what to focus on, it asks up to three questions with a recommended answer for each.
- The report draws real chat transcripts as bubbles. Where a conversation shows Ada using a feature (a playbook, an action, a knowledge answer, a handoff), a small note under the reply opens into a plain-language explanation. The report ends with the notes it used and a next step for each opportunity.
- `scripts/report.py` renders one self-contained HTML file in Ada's brand, masks emails, phone numbers and long numbers in transcripts, and warns about internal terms, blame wording and too many notes.

## 2026.10.27.2

- `diagnose-conversation`, `author-playbook`, `revise-playbook`, `ada-custom-metrics-improve` and `ada-custom-metrics-loop` each gain an "Unattended mode" section. It says how to behave when `/mnt/memory` is mounted and no person is in the chat: never wait for a board or a person, record each step's outcome, and never promote, revert, delete or ramp. In `ada-custom-metrics-loop` the ramp and promote steps are marked not allowed in that mode.

## 2026.10.27.1

- New skill `ada-agent-guide`. When a request about an Ada agent names no stage, such as "fix this chat" or "get this use case live", it picks the stage and loads that skill. It skips requests that already say what to build or change.
- A session-start hint points those requests at `ada-agent-guide`. It prints one line, and only when `adacli` or an Ada MCP server is set up.

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
