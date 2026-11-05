from PIL import Image, ImageDraw, ImageFont
import zlib, base64
import sys
# usage: python3 build_atlas.py <font_dir> <family_prefix> [pixel_size=24] [weights=400,700]
# expects <font_dir>/<family_prefix>-Regular.ttf, -SemiBold.ttf, -Bold.ttf (only the weights you list)
FONT_DIR, FAMILY = sys.argv[1], sys.argv[2]
M = int(sys.argv[3]) if len(sys.argv) > 3 else 24
WEIGHTS = (sys.argv[4] if len(sys.argv) > 4 else "400,700").split(",")
WMAP = {"400": "Regular", "600": "SemiBold", "700": "Bold"}
out = [len(WEIGHTS)] + [int(w) // 100 for w in WEIGHTS]
for wname in [WMAP[w] for w in WEIGHTS]:
    f = ImageFont.truetype(f"{FONT_DIR}/{FAMILY}-{wname}.ttf", M)
    asc, desc = f.getmetrics()
    H = asc + desc
    out += [M, asc, H]
    meta = []
    pix = []
    for c in range(32, 127):
        ch = chr(c)
        adv = f.getlength(ch)
        bb = f.getbbox(ch)
        gw = max(1, bb[2] - bb[0] + 2)
        im = Image.new("L", (gw, H), 0)
        ImageDraw.Draw(im).text((-bb[0] + 1, 0), ch, font=f, fill=255)
        vals = [int(round(p * 3 / 255)) for p in im.get_flattened_data()]
        packed = []
        for i in range(0, len(vals), 4):
            b = 0
            for j in range(4):
                if i + j < len(vals):
                    b |= vals[i + j] << (2 * j)
            packed.append(b)
        a4 = int(round(adv * 4))
        meta += [a4 >> 8, a4 & 255, bb[0] + 128, gw]
        pix += packed
    EX = "\u00b7\u2022\u2013\u2014\u2019\u2018\u201c\u201d\u2192\u00e9\u00c9"
    meta2 = [len(EX)]
    for ch in EX:
        adv = f.getlength(ch); bb = f.getbbox(ch); gw = max(1, bb[2] - bb[0] + 2)
        im = Image.new("L", (gw, H), 0); ImageDraw.Draw(im).text((-bb[0] + 1, 0), ch, font=f, fill=255)
        vals = [int(round(q * 3 / 255)) for q in im.get_flattened_data()]
        for i in range(0, len(vals), 4):
            b = 0
            for j in range(4):
                if i + j < len(vals):
                    b |= vals[i + j] << (2 * j)
            pix.append(b)
        a4 = int(round(adv * 4)); cp = ord(ch)
        meta2 += [cp >> 8, cp & 255, a4 >> 8, a4 & 255, bb[0] + 128, gw]
    out += meta + meta2 + pix
raw = bytes(out)
z = zlib.compress(raw, 9)
open(f"font_atlas_{M}_{'-'.join(WEIGHTS)}.b64", "w").write(base64.b64encode(z).decode())
print("atlas raw", len(raw), "zlib", len(z), "b64", len(base64.b64encode(z)))
