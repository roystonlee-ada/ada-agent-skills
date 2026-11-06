#!/usr/bin/env python3
"""monitor.py — did callers get the experience you designed? Use it while testing and on the first days live.

  Your test calls or test runs (conversation ids from get_test_runs or the dashboard):
    python3 monitor.py --instance <inst> --conversations <id>,<id> [--playbook <id>]
  Real calls through a playbook (simulations are not in the search index; real calls are):
    python3 monitor.py --instance <inst> --playbook <id> [--start YYYY-MM-DD --end YYYY-MM-DD]

One line per call: how it ended (handoff, or not), how many caller turns, and anything worth a look:
  · a failure phrase spoken (--fail-phrases to add your own)
  · an action status outside 2xx (the 599 / NONE sentinels are ignored unless they're the last value)
  · a backtrack (the caller corrected an earlier answer), an off-topic exit, an "I don't have it" (unable_to_provide)
  · digits of 6+ spoken (an id or reference read aloud)
  · a bot line the caller talked over (voice_metadata.is_interrupted): the caller may not have heard it
--detail prints each call as a script: what the caller said, what they heard, and every variable the call set, in order.
Read that for anything flagged, and for the first few calls of every path you test. The monitor finds failures; only reading
finds wording that lands badly.
"""
import json, os, re, sys, argparse, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ada_api import Ada
OK = {'200', '201', '202', '204'}
SENTINEL = {'599', 'NONE'}

def text(e):
    c = e.get('content') if isinstance(e.get('content'), str) else e.get('body')
    return c.strip() if isinstance(c, str) else ''

def speaker(e):
    et = e.get('entry_type') or ''; who = str(e.get('author') or e.get('role') or e.get('sender') or '').lower()
    if et in ('bot_message', 'agent_message') or 'bot' in who or 'agent' in who: return 'BOT'
    if et in ('user_message', 'chatter_message') or 'user' in who or 'chatter' in who: return 'CALLER'
    return None

def code(v):
    s = str(v).strip()
    return s[:-2] if s.endswith('.0') else s

def read(ada, cid, fails):
    r = {'conv': cid, 'turns': 0, 'handoff': None, 'flags': [], 'script': [], 'status': {}}
    for e in ada.transcript(cid):
        et = e.get('entry_type') or ''
        who = speaker(e); t = text(e)
        cut = bool((e.get('voice_metadata') or {}).get('is_interrupted'))
        if who and cut and not t:
            r['script'].append(f'{who:6s} [talked over, nothing logged]')
            if who == 'BOT': r['flags'].append('caller talked over a bot line (logged blank)')
        if who and t:
            r['script'].append(f'{who:6s} {t}' + ('  [talked over]' if cut else ''))
            if who == 'CALLER': r['turns'] += 1
            else:
                low = t.lower()
                if cut: r['flags'].append(f'caller talked over: "{t[:90]}"')
                if any(p in low for p in fails): r['flags'].append(f'failure phrase: "{t[:90]}"')
                if re.search(r'\d{6,}', t.replace(' ', '')): r['flags'].append(f'digits spoken: "{t[:90]}"')
        elif et == 'variable_set':
            n = (e.get('variable') or {}).get('name'); v = e.get('new_value')
            r['script'].append(f'       set {n} = {str(v)[:80]!r}')
            if n and 'status' in n.lower(): r['status'].setdefault(n, []).append(code(v))
        elif et == 'action_executed':
            r['script'].append(f'       ran {(e.get("action") or {}).get("name")}' + (' (mocked)' if e.get('was_mocked') else ''))
        elif et == 'handoff_triggered':
            r['handoff'] = (e.get('handoff') or {}).get('name') or 'handoff'; r['script'].append(f'       HANDOFF {r["handoff"]}')
        elif et == 'playbook_v2_step':
            blob = json.dumps(e)
            for key, label in (('backtrack', 'backtrack (caller corrected an earlier answer)'),
                               ('intent_change', 'off-topic reply'), ('topic_change', 'off-topic reply'),
                               ('unable_to_provide', '"I don\'t have it" — fallback written, no re-ask')):
                if key in blob and label not in r['flags']: r['flags'].append(label)
    for n, vals in r['status'].items():
        real = [v for v in vals if v not in SENTINEL]
        if any(v not in OK for v in real) or (vals and vals[-1] in SENTINEL): r['flags'].append(f'{n}: {vals}')
    return r

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--instance', required=True)
    ap.add_argument('--conversations', default='', help='comma-separated conversation ids (test calls, test runs)')
    ap.add_argument('--playbook', help='with no --conversations: every real call that ran this playbook in the date range')
    today = datetime.datetime.utcnow().strftime('%Y-%m-%d')
    ap.add_argument('--start', default=today); ap.add_argument('--end', default=today)
    ap.add_argument('--fail-phrases', default="wasn't able to,something seems to have gone wrong,ran into an issue,something went wrong")
    ap.add_argument('--detail', action='store_true', help='print every call as a script')
    a = ap.parse_args(); ada = Ada(a.instance)
    fails = [x.strip().lower() for x in a.fail_phrases.split(',') if x.strip()]
    ids = [x for x in a.conversations.split(',') if x]
    if not ids:
        if not a.playbook: sys.exit('pass --conversations, or --playbook with a date range')
        ids = [c.get('id') or c.get('_id') for c in ada.search([{"type": "PLAYBOOKID", "operator": "IS", "value": [a.playbook]}], a.start, a.end)]
        print(f'{len(ids)} real calls ran the playbook {a.start}..{a.end} (UTC)')
    rows = [read(ada, cid, fails) for cid in ids]
    print(f'{sum(1 for r in rows if r["flags"])} of {len(rows)} calls have something worth a look\n')
    for r in rows:
        print(f'{"!!" if r["flags"] else "  "} {r["conv"]}  turns={r["turns"]}  handoff={r["handoff"] or "no"}')
        for f in r['flags']: print(f'      {f}')
        if a.detail:
            for line in r['script']: print(f'      {line[:200]}')
            print()

if __name__ == '__main__':
    main()
