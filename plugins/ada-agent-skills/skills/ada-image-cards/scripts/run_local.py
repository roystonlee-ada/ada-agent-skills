"""Run a built tool locally in pydantic-monty (the same Python subset as Ada) with a stub fetch.

usage: python3 run_local.py <built_tool.py> '<inputs json>' [out.png]
Writes the PNG the tool would upload, so you can look at it before going live.
Pass EVERY input the tool declares; use null for an unset variable (Ada passes None for those).
"""
import base64
import json
import sys
import time

import pydantic_monty

STUB = '''
import json
CAPTURED = []
def log(*a):
    return None
COUNTER = []
def uuid4():
    COUNTER.append(1)
    return '00000000-0000-4000-8000-' + str(len(COUNTER)).zfill(12)
def fetch(method, url, headers=None, body=None, timeout=None):
    if url.endswith("generate-presigned-post/invoke"):
        return {"status_code": 200, "headers": {}, "body": json.dumps({"url": "https://s3.example/", "fields": json.dumps({"key": "k"})})}
    if url.startswith("https://s3.example"):
        CAPTURED.append(body)
        return {"status_code": 204, "headers": {}, "body": ""}
    if url.endswith("generate-presigned-get/invoke"):
        return {"status_code": 200, "headers": {}, "body": json.dumps({"fetch_file_url": "https://example/ok.png"})}
    return {"status_code": 500, "headers": {}, "body": ""}
'''

src_path, inputs = sys.argv[1], json.loads(sys.argv[2])
out_png = sys.argv[3] if len(sys.argv) > 3 else "out.png"
pre = STUB + "".join(k + " = " + repr(v) + "\n" for k, v in inputs.items())   # repr: null -> None
code = pre + open(src_path).read() + "\n[result, ints_b64(CAPTURED[0]) if CAPTURED else '']\n"
t = time.time()
with pydantic_monty.Monty() as p:
    with p.checkout() as s:
        res, body64 = s.feed_run(code)
print("result:", res, "| %.2fs" % (time.time() - t))
if body64:
    body = base64.b64decode(body64)
    i = body.find(b"\x89PNG")
    j = body.rfind(b"IEND") + 8
    open(out_png, "wb").write(body[i:j])
    print("wrote", out_png, j - i, "bytes")
