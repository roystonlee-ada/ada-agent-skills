#!/usr/bin/env python3
"""action_test.py — execute an action definition inline with literal values and show what each output would store.

  python3 action_test.py --instance <instance> --action <id> --set <var id>=<value> ... [--token-action <id> --token-var <var id>]

Nothing is created or saved on the Ada side. The API call itself is real: reads are safe; a cancel or a
pause is single-use per account — spend it deliberately.
Output mappings are evaluated locally with jmespath
(pip install jmespath) because the test endpoint returns full_response and status_code only.
"""
import json, sys, os, argparse, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ada_api import Ada, substitute

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--instance', required=True); ap.add_argument('--action', required=True)
    ap.add_argument('--set', action='append', default=[]); ap.add_argument('--token-action'); ap.add_argument('--token-var'); ap.add_argument('--vars', help='vars list JSON to name outputs')
    a = ap.parse_args(); ada = Ada(a.instance)
    names = {}
    if a.vars:
        d = json.load(open(a.vars)); vs = d.get('variables', d) if isinstance(d, dict) else d
        names = {(v.get('_id') or v.get('id')): v['name'] for v in vs}
    values = dict(kv.split('=', 1) for kv in a.set)
    token = None
    if a.token_action:
        st, tdef = ada.get_action(a.token_action); st, oc = ada.test_action(tdef)
        token = (oc.get('full_response') or {}).get('access_token'); assert token, f'no access_token in token action outcome: {str(oc)[:300]}'
        values[a.token_var] = token; print('token acquired (not shown)')
    st, adef = ada.get_action(a.action); adef2 = substitute(adef, values)
    left = re.findall(r'\{([0-9a-f]{24})(?:\|[^}]*)?\}', json.dumps({k: adef2.get(k) for k in ('url', 'request_body', 'headers')}))
    if left: print('WARNING unsubstituted placeholders:', [names.get(x, x) for x in left])
    print(adef['method'], re.sub(r'\{[0-9a-f]{24}\|[^}]*\}', '{var}', adef['url']))
    st, oc = ada.test_action(adef2)
    red = lambda s: s.replace(token, '<TOKEN>') if token else s
    print(f"HTTP {st} | outcome status={oc.get('status')} status_code={oc.get('status_code')} error={oc.get('error_message')}")
    print('full_response:', red(json.dumps(oc.get('full_response')))[:1500])
    try:
        import jmespath
        for o in adef.get('outputs') or []:
            if o.get('source') == 'status_code': val = oc.get('status_code')
            else:
                try: val = jmespath.search(o['key'], oc.get('full_response'))
                except Exception as e: val = f'JMESPATH ERROR {e}'
            tgt = names.get(o.get('variable_name'), o.get('variable_name')) if o.get('save_as_variable') else '(llm only)'
            print(f"   → {str(tgt):28} = {red(json.dumps(val))[:200]}")
    except ImportError:
        print('(pip install jmespath to see per-variable output values)')

if __name__ == '__main__':
    main()
