#!/usr/bin/env python3
"""runsummary.py — one screen per test run: pass/fail, the criteria that failed and why, what was said, and the variables set.

  python3 runsummary.py --instance <inst> [--prefix <var prefix>] <test run id> ...

Read-only. Use it after a batch of test runs (get_test_runs gives the ids) to spot the runs worth reading in full with
monitor.py --detail. --prefix limits the variable lines to your build's variables (e.g. ol_).
"""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ada_api import Ada

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--instance', required=True); ap.add_argument('--prefix', default='')
    ap.add_argument('runs', nargs='+')
    a = ap.parse_args(); ada = Ada(a.instance)
    for rid in a.runs:
        st, d = ada.api('GET', f'/api/testing/test_runs/{rid}'); d = d.get('test_run', d)
        name = (d.get('test_case_snapshot') or {}).get('name', rid)
        print(f"\n=== {name}  status={d.get('status')} pass={d.get('did_pass')} conv={d.get('conversation_id')}")
        for c in d.get('criteria_results') or []:
            if not c.get('did_pass'): print('  [FAIL]', c.get('success_criteria', '')[:90], '\n       →', str(c.get('rationale'))[:260])
        if not d.get('conversation_id'): continue
        for e in ada.transcript(d['conversation_id']):
            et = e.get('entry_type')
            if et in ('bot_message', 'user_message'): print('   ', 'BOT:' if et == 'bot_message' else 'CALLER:', (e.get('content') or '')[:200])
            elif et == 'variable_set':
                var = (e.get('variable') or {}).get('name', '')
                if var.startswith(a.prefix) and e.get('new_value') not in ('NONE', None): print('        ·', var, '=', str(e.get('new_value'))[:90])
            elif 'handoff' in str(et): print('        ⇒', et)

if __name__ == '__main__':
    main()
