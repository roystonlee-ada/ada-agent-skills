#!/usr/bin/env python3
"""prereq_check.py — run before you build. Read-only; it only reports.

  python3 prereq_check.py --instance <inst> [--sample 40]

  1. Tools   Is adacli installed and the latest release? (adacli <inst> upgrade --check)  Is jmespath installed?
  2. Access  Is there a live adacli session for the instance? Is the Ada MCP server for it signed in (claude mcp get)?
  3. Flags   Client-level behaviours you can't see in the dashboard, read from recent real calls (a bot with no real V2
             calls yet gets one line instead):
               · action status-code output — whether failure branches after an API call run, or the call hands off first
               · ask step in use · backtrack detector seen firing · unquoted exact SET values writing
             Anything not proven prints CHECK; confirm it with Ada support.

Lines: OK · FIX (do this before you build) · CHECK (worth knowing; confirm with Ada if it matters for your flow).
The live schema comes from the Ada MCP, which a script can't call: Claude reads the live playbook schema and the improvement guide.
"""
import argparse, json, os, re, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))

rows = []
def out(level, area, msg): rows.append((level, area, msg))

# ---------- 1. tools ----------
def check_tools(inst):
    sys.path.insert(0, HERE)
    from ada_api import adacli_cmd
    try: cmd = adacli_cmd()
    except SystemExit as e: out('FIX', 'tools', f'{e} — install: brew install adasupport/tap/adacli (or the adacli-setup-guide skill)'); return
    for _ in range(2):   # the release lookup fails now and then; one retry
        r = subprocess.run(cmd + [inst, 'upgrade', '--check'], capture_output=True, text=True, timeout=60)
        txt = r.stdout + r.stderr
        if 'Latest version' in txt: break
    cur = re.search(r'Current version:\s*(\S+)', txt); latest = re.search(r'Latest version:\s*(\S+)', txt)
    src = next((c for c in cmd if c.endswith(os.path.join('adacli', 'dist', 'index.js'))), None)
    if src and latest:   # a source build always reports its package.json version; check the checkout has the release instead
        repo = os.path.dirname(os.path.dirname(os.path.dirname(src))); tag = f'adacli-v{latest.group(1)}'
        subprocess.run(['git', '-C', repo, 'fetch', '--quiet', '--no-tags', 'origin', 'tag', tag], capture_output=True, timeout=120)
        has = subprocess.run(['git', '-C', repo, 'merge-base', '--is-ancestor', tag, 'HEAD'], capture_output=True).returncode == 0
        if has: out('OK', 'tools', f'adacli from source ({repo}) includes the latest release {latest.group(1)}; rebuild with `npm run build` in adacli/ after pulling')
        else: out('FIX', 'tools', f'adacli from source ({repo}) is behind {latest.group(1)}: git pull, then `npm install && npm run build` in adacli/ (or install a release with brew install adasupport/tap/adacli)')
    elif cur and latest and cur.group(1) != latest.group(1):
        hint = next((l.strip() for l in txt.splitlines() if 'newer version' in l.lower()), f'update adacli to {latest.group(1)}')
        out('FIX', 'tools', f'adacli {cur.group(1)} is behind {latest.group(1)}: {hint}')
    elif cur and latest: out('OK', 'tools', f'adacli {cur.group(1)} is the latest release')
    else: out('CHECK', 'tools', f'adacli {cur.group(1) if cur else "?"} — could not read the latest release; run: adacli {inst} upgrade --check')
    try:
        import jmespath  # noqa: F401
        out('OK', 'tools', 'jmespath installed')
    except ImportError: out('FIX', 'tools', 'jmespath missing (action_test.py uses it): pip3 install jmespath')

# ---------- 2. access ----------
def check_access(inst):
    sys.path.insert(0, HERE)
    try:
        from ada_api import Ada
        ada = Ada(inst)
    except SystemExit as e:
        out('FIX', 'access', f'{e} — then re-run'); return None
    if ada.expired: out('FIX', 'access', f'adacli session for {inst} expired — run: adacli {inst} login'); return None
    try:
        st, _ = ada.api('GET', '/api/playbooks')
        if st != 200: out('FIX', 'access', f'session present but GET /api/playbooks returned {st} — run: adacli {inst} login'); return None
    except Exception as e:
        out('FIX', 'access', f'API unreachable with the saved session ({e}) — run: adacli {inst} login'); return None
    out('OK', 'access', f'adacli session for {inst} is live')
    return ada

def check_mcp(inst):
    setup = 'set it up per https://docs.ada.cx/mcp/introduction/overview (or the setup-ada-mcp skill)'
    cfg = os.path.expanduser('~/.claude.json'); names = {f'ada-{inst}'}
    if os.path.exists(cfg):
        found = set(re.findall(r'"(ada-[a-z0-9-]+)"\s*:\s*\{', open(cfg, encoding='utf-8').read()))
        names |= {n for n in found if inst.split('.')[0].replace('sandbox2-', '') in n}
    if not shutil.which('claude'):
        out('CHECK', 'access', f'claude CLI not on PATH, so MCP sign-in can\'t be checked; run /mcp and look for ada-{inst}'); return
    for name in sorted(names):
        try: r = subprocess.run(['claude', 'mcp', 'get', name], capture_output=True, text=True, timeout=60)
        except subprocess.TimeoutExpired: out('CHECK', 'access', f'claude mcp get {name} timed out; run /mcp to check it'); return
        status = re.search(r'Status:\s*(.+)', r.stdout)
        if r.returncode or not status: continue
        st = status.group(1).strip()
        if 'Connected' in st: out('OK', 'access', f'Ada MCP server {name} is signed in')
        elif 'auth' in st.lower(): out('FIX', 'access', f'Ada MCP server {name} needs sign-in: run /mcp in the session doing the build and sign in there')
        else: out('FIX', 'access', f'Ada MCP server {name}: {st} — run /mcp to reconnect')
        return
    out('FIX', 'access', f'no Ada MCP server for {inst}: {setup}. Changesets and describe_entity need it')

# ---------- 3. flags, from evidence ----------
def adacli_conversations(inst, pid, days=14):
    from ada_api import adacli_cmd
    r = subprocess.run(adacli_cmd() + [inst, 'conversations', 'search', '--playbook', pid, '--since', f'{days}d', '--json'], capture_output=True, text=True)
    try: return [c['id'] for c in json.loads(r.stdout).get('conversations', [])]
    except (ValueError, KeyError): return []

def walk(steps):
    for s in steps:
        yield s
        for b in s.get('branches') or []: yield from walk(b.get('steps') or [])

def check_flags(ada, sample, inst):
    st, body = ada.api('GET', '/api/playbooks')
    pbs = body.get('playbooks') if isinstance(body, dict) else body
    v2 = []
    for p in pbs or []:
        pid = p.get('_id') or p.get('id')
        st, full = ada.get_pb(pid)
        if st == 200 and full.get('sections'): v2.append(full)
    steps = [s for pb in v2 for sec in pb['sections'] for s in walk(sec.get('steps') or [])]
    asks = [s for s in steps if s.get('type') == 'ask']
    active = [pb for pb in v2 if pb.get('is_active')]
    bare = {}
    for pb in active:
        for sec in pb['sections']:
            for s in walk(sec.get('steps') or []):
                v = s.get('value')
                if s.get('type') == 'set' and isinstance(v, str) and re.fullmatch(r'[A-Za-z_]+', v): bare.setdefault(s['variable_id'], set()).add(v)
    # recent conversations through any active V2 playbook
    convs = []
    for pb in active[:8]:
        convs += adacli_conversations(inst, pb.get('_id') or pb.get('id'))
    convs = [c for c in dict.fromkeys(convs) if c][:sample]
    status_on = status_off = backtracks = 0; bare_wrote = set()
    for cid in convs:
        st, t = ada.api('GET', f'/api/conversations/{cid}/transcript')
        ents = t if isinstance(t, list) else (t.get('messages') or t.get('transcript') or []) if isinstance(t, dict) else []
        blob = json.dumps(ents).lower()
        if any(x.get('entry_type') == 'playbook_v2_step' and 'backtrack' in json.dumps(x).lower() for x in ents): backtracks += 1
        for i, e in enumerate(ents):
            if e.get('entry_type') != 'variable_set': continue
            var = e.get('variable') or {}; val = e.get('new_value')
            if var.get('id') in bare and val in bare[var['id']]: bare_wrote.add(val)
            if 'status' in (var.get('name') or '').lower():
                try: code = float(val)
                except (TypeError, ValueError): continue
                if code >= 400 and code != 599:
                    nxt = [x.get('entry_type') for x in ents[i + 1:i + 8]]
                    first = next((x for x in nxt if x in ('playbook_v2_step', 'handoff_triggered')), None)
                    if first == 'playbook_v2_step': status_on += 1
                    elif first == 'handoff_triggered': status_off += 1
    n = len(convs)
    st, acts = ada.api('GET', '/api/generative_actions/web_actions'); al = acts.get('web_actions') if isinstance(acts, dict) else acts
    enabled = sum(1 for x in al or [] if not x.get('is_disabled'))
    caps = f'enabled web actions: {enabled} — if any create (action, playbook, handoff…) is refused for a cap, ask Ada to raise that limit; not a design constraint'
    if not n:
        out('CHECK', 'flags', 'no real calls through a live V2 playbook yet, so client flags can\'t be read. The one that matters is status-code output '
            'turned on for the client: your first test call with a failing API shows whether the failure branch runs or the call transfers')
        out('OK', 'flags', caps); return
    out('OK' if asks else 'CHECK', 'flags', f'ask step: {len(asks)} in {len(v2)} V2 playbooks' + ('' if asks else ' — none found; ask Ada support whether the ask step is on for this client'))
    if status_on and not status_off: out('OK', 'flags', f'action status-code output ON: {status_on} real non-2xx status(es) in {n} conversations were followed by more playbook steps')
    elif status_off and not status_on: out('CHECK', 'flags', f'action status-code output looks OFF: non-2xx statuses were followed straight by a handoff ({status_off}×), so failure branches after an API call will not run — ask Ada support to turn it on, or have the API return 200 with an error field')
    elif status_on and status_off: out('CHECK', 'flags', f'action status-code output mixed ({status_on} continued, {status_off} handed off) — read those transcripts before relying on failure branches')
    else: out('CHECK', 'flags', f'action status-code output: no real non-2xx status in {n} conversations — ask Ada support whether it is on. Sims skip the forced handoff, so a sim cannot prove it')
    out('OK' if backtracks else 'CHECK', 'flags', f'backtrack detector: fired in {backtracks}/{n} conversations' + ('' if backtracks else ' — none seen; it is on by default, so design for it; widen --sample to see one'))
    if bare:
        if bare_wrote: out('OK', 'flags', f'unquoted exact SET values write on this instance (seen: {", ".join(sorted(bare_wrote)[:5])})')
        else: out('CHECK', 'flags', 'unquoted exact SET: none observed writing — inner-quote string literals ("\\"NONE\\"") until proven')
    out('OK', 'flags', caps)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--instance', required=True); ap.add_argument('--sample', type=int, default=40)
    a = ap.parse_args()
    check_tools(a.instance); ada = check_access(a.instance); check_mcp(a.instance)
    if ada: check_flags(ada, a.sample, a.instance)
    else: out('CHECK', 'flags', 'skipped — needs a live adacli session')
    for lvl, area, msg in rows: print(f'{lvl:6s} {area:7s} {msg}')
    print('\nClaude, before building: read the live playbook schema and the improvement guide from the instance\'s Ada MCP server.'
          ' Where they disagree with this skill, they win.')
    print(f'\n{sum(r[0] == "FIX" for r in rows)} to fix, {sum(r[0] == "CHECK" for r in rows)} to check')

if __name__ == '__main__':
    main()
