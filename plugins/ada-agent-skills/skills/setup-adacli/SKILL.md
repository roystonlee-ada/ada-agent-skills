---
name: setup-adacli
description: >
  Check that adacli is installed and current, install or upgrade it with
  Homebrew, and log in to an Ada instance. Use it first, before any other
  Ada Architect skill that runs adacli, and whenever the person says "set up
  adacli", "install adacli", "upgrade adacli", "update adacli", "adacli not
  found", "which adacli version", "log in to Ada", "make adacli read-only",
  "stop adacli changing my agent", or an adacli command fails with "command
  not found", a login error, or exit code 7. Also covers the Ada MCP route
  for people with no shell.
---

# Set up adacli

adacli is Ada's command line for reading and changing an AI Agent. The other
skills in this plugin use it, or the Ada MCP server. This skill gets one of
the two working.

Homebrew installs the adacli binary and nothing else. It carries no skills.
The skills are this plugin.

## 1. Check

Run the check. It reads the machine and changes nothing.

```bash
bash "${CLAUDE_SKILL_DIR}/scripts/check_adacli.sh"
```

If `CLAUDE_SKILL_DIR` is empty, run the script from this skill's `scripts/`
folder. Read the `STATE:` line.

| STATE | Meaning | Do |
|---|---|---|
| `up-to-date` | Homebrew build, latest release | Go to step 3 |
| `upgrade-available` | Homebrew build, a newer release exists | Step 2, upgrade |
| `not-installed` | Homebrew is there, adacli is not | Step 2, install |
| `no-homebrew-no-adacli` | Neither is installed | Step 2, Homebrew first |
| `installed-outside-homebrew-current` | Another tool installed it, and it is the latest release | Nothing to fix. Go to step 3 |
| `installed-outside-homebrew` | Another tool installed it, and it is older or unchecked | Ask, see below |
| `version-unknown` | Could not reach GitHub | Step 2, upgrade check by hand |
| `unsupported-platform` | Not macOS or Linux | Use the MCP route |

## 2. Install or upgrade

Installing software changes the person's machine. Say what you are about to
run and wait for a yes.

- Install: `brew install adasupport/tap/adacli`
- Upgrade: `brew update && brew upgrade adasupport/tap/adacli`
- No Homebrew: the person installs it from https://brew.sh first. Do not pipe
  the installer script yourself.

After either one, run the check again and confirm `STATE: up-to-date`.

If adacli came from somewhere other than Homebrew (a copy someone built or
linked), do not remove it, and do not say the skills need the Homebrew build:
they work with any current adacli. Ask whether to keep it. If they switch to the
Homebrew build, run `which -a adacli` and confirm the Homebrew one comes first.

On macOS, a release tarball downloaded by hand can be blocked by Gatekeeper.
Installing through Homebrew avoids that. If it happens anyway:
`xattr -d com.apple.quarantine "$(which adacli)"`.

`adacli <instance> upgrade --check` also reports a newer release, but it never
installs one. Homebrew does the upgrade.

## 3. Log in

The instance is the first part of the dashboard address. For
`acme-corp.ada.support` it is `acme-corp`. Ask for it if you do not know it.

```bash
adacli <instance> login
adacli <instance> status
```

`login` prints a code and a link. The person opens the link, signs in and
approves the code. Then `status` should report a healthy session.

- Never ask for a password in chat. Headless login with `--email` and
  `--password` exists for accounts that do not use single sign-on. Let the
  person type it in their own terminal.
- A person who uses single sign-on must use the device code route.

## 4. Read-only or read-write

Read-only mode makes adacli refuse every write to an instance before it sends
a request. Reads, `login`, `logout` and `status` still work. Offer it for a
live customer agent or an audit. Ask once: "Should adacli be able to change
this agent, or only read it?" Skip the question if the person has said.

If they choose read-only:

1. Read the full domain from `adacli <instance> status --json`, the
   `instance` field, for example `acme-corp.ada.support`. Use that value. A
   short handle such as `acme-corp` matches nothing, and adacli does not warn.
   A regional instance keeps its region, for example `acme-corp.us2.ada.support`.
2. Show the exact line you will add and wait for a yes:
   `read_only=acme-corp.ada.support`.
3. Edit `~/.adacli/config`. Create it if it is missing. If a `read_only=`
   line exists, add the domain to it with a comma. Keep every other line. Do
   not rewrite the file from scratch.
4. Run `adacli <instance> status`. The Read-only row must say `yes`. With
   `--json` it has `"read_only": true`. The change applies to the next
   command, with no new login.

Run the check script again. It lists the `read_only` entries and warns about
any entry with no domain.

Tell the person:

- It is a safety setting, not a permission. It sits in a file on this
  computer, the Ada server does not know about it, and anyone with the file can
  remove it. To stop a person from changing an agent, give them a dashboard
  role with less access.
- It belongs to the instance, not the session. Log out and in, and it stays.
- It applies to one computer. Each person, and each machine that runs an
  agent, needs its own line. There is no command-line flag.
- It also blocks test runs and simulations, because they create records. A
  read-only instance cannot prove a fix. To build and test, use a second
  instance that is not read-only.

To turn it off, the person removes the instance from the `read_only` line, or
deletes the line.

### If a command exits with code 7

Exit code 7 means the instance is read-only. With `--json` the error category
is `read_only`. Stop. Say which change you were about to make, and that it is
blocked on purpose. Offer two ways forward: a writable instance, or the
person removes the instance from `read_only` themselves. Never edit
`~/.adacli/config` to get past a block, and never retry the command, even if
the person asked for the change. The person decides whether to lift it.

## 5. MCP route

Use this when the person has no shell, is on Windows, or prefers it. The Ada
MCP server signs in with OAuth, with no API key.

- The server address is `https://<dashboard domain>/api/mcp/oauth`, for
  example `https://acme-corp.ada.support/api/mcp/oauth`.
- If the person's Claude has Ada's `install-ada-mcp` skill, use that.
  Otherwise point them to Ada's MCP setup guide in their Ada admin docs.
- Each skill in this plugin has a `references/runtime-mcp.md` that maps its
  steps to MCP tools, and says where the MCP has no tool and what to do
  instead.
- The MCP route has no `read_only` file. The same safety comes from the
  person's role: Agent and Read Only roles get only the read tools, and an
  Owner can limit tools under Config > PLATFORM > MCP server. Unlike adacli's
  setting, the Ada server enforces it. If the person wants a look-only
  connection, connect with a Read Only user. If a write tool is refused, stop
  and tell the person, as for exit code 7.

## 6. Report

Tell the person in two or three lines which route is working (adacli or MCP),
the adacli version, the instance they are logged in to, and whether it is
read-only. Then hand over to
the skill they came for.
