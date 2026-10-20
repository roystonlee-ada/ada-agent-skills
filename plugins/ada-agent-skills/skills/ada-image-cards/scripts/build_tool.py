"""Assemble a deployable code-tool source: renderer + font atlas + your card file, minified, under 64 KB.

usage: python3 build_tool.py <card.py> <atlas.b64> <out.py> [extra modules, e.g. scripts/qr.py]
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from minify import minify
from dce import strip_unused

card_path, atlas_path, out_path = sys.argv[1:4]
extras = "".join("\n" + open(p).read() + "\n" for p in sys.argv[4:])
renderer = open(os.path.join(HERE, "svgpng.py")).read()
card = open(card_path).read()
atlas = open(atlas_path).read().strip()
src = renderer + extras + "\nATLAS = " + json.dumps(atlas) + "\n" + card
out = minify(strip_unused(src))
size = len(out.encode())
open(out_path, "w").write(out)
print(out_path, size, "bytes", "OK" if size <= 65536 else "OVER the 64 KB cap - use a smaller atlas (fewer weights / smaller size)")
