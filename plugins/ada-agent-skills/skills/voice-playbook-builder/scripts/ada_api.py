"""ada_api.py — Ada dashboard API with the adacli session cookie, write paths allow-listed per instance.

  from ada_api import Ada
  ada = Ada('<instance>')                                     # reads ~/.adacli/sessions.json['<instance>.ada.support']
  ada.allow(playbooks=['<id>'], actions=['<id>'])       # only these may be PATCHed/PUT; POST create paths + testing are on by default
  st, pb = ada.get_pb('<id>');  st, r = ada.patch_pb('<id>', sections=...)   # patch_pb always leaves is_active False
  st, r, active, rules = ada.activate_gated('<id>', expected_rule)            # the only way to activate

Why: production is co-edited and live; a helper that can only touch what this build owns turns a typo into a
refused call instead of an incident. Sessions expire (~24 h): check `expired` and re-run `adacli <inst> login`.
"""
import json, os, re, shutil, subprocess, time, urllib.request

def adacli_cmd():
    """How to run adacli from a script. Shell aliases aren't visible to subprocesses, so: $ADACLI if set (e.g. "node /path/dist/index.js"),
    else `adacli` on PATH."""
    if os.environ.get('ADACLI'): return os.environ['ADACLI'].split()
    if shutil.which('adacli'): return ['adacli']
    raise SystemExit('adacli not found: install it (see the setup-adacli skill), or set ADACLI="node /path/to/adacli/dist/index.js"')

def adacli_version():
    try: return subprocess.run(adacli_cmd() + ['--version'], capture_output=True, text=True, timeout=60).stdout.strip().split()[-1]
    except Exception: return ''

STRIP = {'_id', 'client_id', 'version', 'contains_media', 'created_at', 'created_by', 'updated_at', 'updated_by', 'id', 'referencing_playbooks'}
ACTION_STRIP = ('_id', 'client_id', 'created_at', 'updated_at', 'referencing_playbooks', 'referencing_processes', 'referenced_variables', 'is_deleted')

class Ada:
    def __init__(self, instance):
        sessions = json.load(open(os.path.expanduser('~/.adacli/sessions.json')))
        key = instance if instance in sessions else f'{instance}.ada.support'
        if key not in sessions: raise SystemExit(f'no adacli session for {instance}; run: adacli {instance} login')
        s = sessions[key]; self.base = s['baseUrl']; self.expired = s.get('expiresAt', 0) < time.time() * 1000
        self.h = {"cookie": s['cookie'], "x-csrf-token": s['csrf'], "x-ada-request-origin": "app", "x-ada-source": "cli",
                  "content-type": "application/json", "accept": "application/json"}
        self._playbooks, self._actions = set(), set()

    def allow(self, playbooks=(), actions=()):
        self._playbooks |= set(playbooks); self._actions |= set(actions)

    def _allowed(self, method, path):
        if method == 'GET': return True
        if method == 'POST' and path in ('/api/variables', '/api/generative_actions/web_actions', '/api/playbooks',
                                         '/api/generative_actions/web_actions/test', '/api/conversations/search'): return True
        if method in ('POST', 'PATCH') and path.startswith('/api/testing/'): return True
        if method == 'PATCH': return any(path == f'/api/playbooks/{p}' for p in self._playbooks)
        if method == 'PUT': return any(path == f'/api/generative_actions/web_actions/{a}' for a in self._actions)
        return False

    def api(self, method, path, body=None):
        if not self._allowed(method, path): raise PermissionError(f'refused: {method} {path} (not allow-listed for this build)')
        req = urllib.request.Request(self.base + path, data=json.dumps(body).encode() if body is not None else None, headers=self.h, method=method)
        try:
            r = urllib.request.urlopen(req, timeout=90); return r.status, json.loads(r.read().decode() or '{}')
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode()[:2000]

    # ---- playbooks
    def get_pb(self, pid):
        st, pb = self.api('GET', f'/api/playbooks/{pid}'); return st, (pb.get('playbook', pb) if isinstance(pb, dict) else pb)
    @staticmethod
    def clean_sections(secs):
        out = []
        for s in secs:
            s = dict(s)
            if not re.fullmatch(r'[0-9a-f]{24}', str(s.get('id') or '')): s.pop('id', None)
            out.append(s)
        return out
    def patch_pb(self, pid, **changes):
        """Fetch fresh, merge, PATCH. Always leaves is_active False — activation goes through activate_gated."""
        st, pb = self.get_pb(pid)
        body = {k: v for k, v in pb.items() if k not in STRIP and not k.startswith('compiled_') and not k.startswith('referenced_')}
        if 'sections' in body: body['sections'] = self.clean_sections(body['sections'])
        body.update(changes); body['is_active'] = False
        return self.api('PATCH', f'/api/playbooks/{pid}', body)
    def create_pb_inactive(self, playbook, expected_rule):
        """POST a new playbook that must come back INACTIVE and carrying expected_rule. `playbooks create` has landed
        ACTIVE before, so: body forces is_active False + the gate, then the live row is re-read;
        if it is active anyway it is PATCHed inactive at once and the call raises so nobody builds on a live placeholder."""
        body = {k: v for k, v in playbook.items() if (k not in STRIP or k == 'version') and not k.startswith('compiled_') and not k.startswith('referenced_')}
        body['is_active'] = False; body['rules'] = expected_rule
        if 'sections' in body: body['sections'] = self.clean_sections(body['sections'])
        st, r = self.api('POST', '/api/playbooks', body)
        pid = ((r.get('playbook') or {}).get('_id') or r.get('_id')) if isinstance(r, dict) else None   # POST returns the row unwrapped
        if st not in (200, 201): raise RuntimeError(f'create failed: {st} {str(r)[:500]}')
        if not pid:   # created but the id is not where we looked: find it by name so nothing is left behind untracked
            st_l, pbs = self.api('GET', '/api/playbooks'); rows = [x for x in (pbs.get('playbooks') if isinstance(pbs, dict) else pbs) if x.get('name') == body.get('name')]
            if len(rows) != 1: raise RuntimeError(f'created ({st}) but cannot identify the new row by name: {len(rows)} matches for {body.get("name")!r}')
            pid = rows[0]['_id']
        self._playbooks.add(pid)
        st2, live = self.get_pb(pid)
        if live.get('is_active'):
            self.patch_pb(pid); st3, live = self.get_pb(pid)
            raise RuntimeError(f'created playbook {pid} came back ACTIVE — forced inactive (now {live.get("is_active")}); check for live impact before continuing')
        if (live.get('rules') or '').replace(' ', '') != expected_rule.replace(' ', ''):
            raise RuntimeError(f'created playbook {pid} is inactive but the gate did not stick: {live.get("rules")!r}')
        return pid, live
    def activate_gated(self, pid, expected_rule):
        st, pb = self.get_pb(pid)
        if (pb.get('rules') or '').replace(' ', '') != expected_rule.replace(' ', ''):
            raise PermissionError(f'refusing to activate {pid}: live rule {pb.get("rules")!r} != expected gate')
        body = {k: v for k, v in pb.items() if k not in STRIP and not k.startswith('compiled_') and not k.startswith('referenced_')}
        body['sections'] = self.clean_sections(body['sections']); body['is_active'] = True
        st, r = self.api('PATCH', f'/api/playbooks/{pid}', body)
        st2, live = self.get_pb(pid); return st, r, live.get('is_active'), live.get('rules')

    # ---- actions
    def get_action(self, aid):
        st, r = self.api('GET', f'/api/generative_actions/web_actions/{aid}'); return st, (r.get('web_action', r) if isinstance(r, dict) else r)
    @staticmethod
    def create_body(action, name=None):
        b = {k: v for k, v in action.items() if k not in ACTION_STRIP}
        b['outputs'] = [{k: v for k, v in o.items() if k != 'id'} for o in b.get('outputs') or []]
        if name: b['name'] = name
        return b
    def test_action(self, action_def):
        """Execute an inline action definition (nothing saved). Returns the step outcome: status_code, full_response, error_message."""
        body = {k: v for k, v in action_def.items() if k not in ACTION_STRIP}
        st, r = self.api('POST', '/api/generative_actions/web_actions/test', {"web_action": body, "test_inputs": {}})
        return st, (r.get('step_outcome', r) if isinstance(r, dict) else r)

    # ---- conversations
    def transcript(self, cid):
        st, t = self.api('GET', f'/api/conversations/{cid}/transcript'); return (t.get('transcript', []) if isinstance(t, dict) else [])
    def search(self, filters, start, end, size=100):
        out, last = [], None
        while True:
            body = {"text": "", "conversation_id": "", "size": size, "filters": filters, "date": {"start": start, "end": end, "timeZone": "UTC"}}
            if last: body["last_sort"] = last
            st, r = self.api('POST', '/api/conversations/search', body); d = r.get('data', r) if isinstance(r, dict) else {}
            out += d.get('conversations', [])
            if not d.get('more_available') or not d.get('last_sort'): return out
            last = d['last_sort']

def substitute(obj, values):
    """Replace {<var id>|default} placeholders in an action definition with literal values."""
    s = json.dumps(obj)
    for vid, val in values.items():
        s = re.sub(r'\{%s(\|[^}]*)?\}' % vid, lambda m: json.dumps(str(val))[1:-1], s)
    return json.loads(s)
