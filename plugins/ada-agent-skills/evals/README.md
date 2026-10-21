# Evals

Checks that each skill loads for real asks, and that with the Ada MCP tools in
front of it the agent keeps the skill's rules. Runs on `claude plugin eval`
with mocked Ada tools, so nothing reaches an Ada instance.

## Run

```
./evals/run.sh                 # 3 repeats: skills on, then skills off
RUNS=1 ./evals/run.sh          # quick pass
TAG=behaviour ./evals/run.sh   # rule cases only
```

Results go to `evals/results/<timestamp>/` (git-ignored): `summary.md`, and
`with.html` / `without.html` with every reply and verdict. A full run costs
about $12 and takes about 10 minutes.

## How it works

| File | Role |
|---|---|
| `build_cases.py` | The spec. Builds every case folder. Edit cases here, not in the folders |
| `run.sh` | Builds, runs skills on, runs skills off (Skill tool removed), compares |
| `compare.py` | One row per case: skill fired, score on, score off, failed checks |

- **Routing** cases (`route-*`) pass when the named skill loads.
  `route-none-*` pass when no Ada skill loads.
- **Behaviour** cases score the agent's tool calls and reply. The score leaves
  out whether the skill loaded. Skills off uses the same tools and mocks, so
  the gap between the two columns is what the skills add.
- Each case loads `plugin-under-test/`: the plugin's skills, copied fresh on
  every build, plus an `ada` MCP server that the mocks stand in for. A case's
  `plugins:` list replaces the plugin under test, which is why the copy exists.

## Live tier

The mocked suite follows the runtime files, so a tool renamed on the server
still passes it. The live tier checks against a real instance, read-only.

```
python3 evals/check_tool_names.py https://<instance>.ada.support/api/mcp/oauth
./evals/run-live.sh            # default: roystonlee-csc
```

- `check_tool_names.py` lists the server's tools without calling any, and
  fails when a tool or `operation` a skill names is missing. The first run
  opens the OAuth sign-in and caches the token.
- `run-live.sh` runs the four `evals-live/` cases with `--mocks off` and
  grants only the read tools in `READ_TOOLS`. Write tools are never granted,
  so the harness refuses them even if the agent tries.
- Graders check tool calls and the skill's rules, never exact numbers, because
  the instance's data changes. A rubric must also pass when the data is empty
  (no handoffs, no drafts), so a quiet instance does not fail a correct reply.
- The harness strips the environment and gives each run a temporary HOME, so
  the build writes the token folder into each live case's server `env`. Those
  built configs are git-ignored; `run-live.sh` rebuilds them.
- `mcp-remote` is pinned to 0.1.38. 0.1.37 rejects the server's protocol
  version, and 0.15.x keeps tokens in another folder, so it needs a new sign-in.
- Use a demo or sandbox instance. Results hold real transcripts, so never
  publish them or point the live tier at a customer instance.

## Add a case

Add an entry to `ROUTING`, `NEGATIVE`, `BEHAVIOUR` or `LIVE` in
`build_cases.py`, then run `python3 evals/build_cases.py`. Test one rule per
case, and take the rule from the skill's own words. Use made-up data only in
mocked cases.

## Not covered

- Write paths on a real instance: staging, test runs and promote run on mocks only.
- The adacli route, multi-turn flows past the first turn, and Codex or ChatGPT.
