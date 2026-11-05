# Minimal SVG -> PNG renderer for Ada code tools (Monty runtime: no bytes(), bytearray, struct or zlib).
import re
import math
# Supports: rect, line, circle, path, text, image (PNG or SVG data URI), g + transform, linearGradient.
B64A = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
B64R = {}
for _i in range(64):
    B64R[B64A[_i]] = _i
ALLB = b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f\x20\x21\x22\x23\x24\x25\x26\x27\x28\x29\x2a\x2b\x2c\x2d\x2e\x2f\x30\x31\x32\x33\x34\x35\x36\x37\x38\x39\x3a\x3b\x3c\x3d\x3e\x3f\x40\x41\x42\x43\x44\x45\x46\x47\x48\x49\x4a\x4b\x4c\x4d\x4e\x4f\x50\x51\x52\x53\x54\x55\x56\x57\x58\x59\x5a\x5b\x5c\x5d\x5e\x5f\x60\x61\x62\x63\x64\x65\x66\x67\x68\x69\x6a\x6b\x6c\x6d\x6e\x6f\x70\x71\x72\x73\x74\x75\x76\x77\x78\x79\x7a\x7b\x7c\x7d\x7e\x7f\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xab\xac\xad\xae\xaf\xb0\xb1\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xbb\xbc\xbd\xbe\xbf\xc0\xc1\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xcb\xcc\xcd\xce\xcf\xd0\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xdb\xdc\xdd\xde\xdf\xe0\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xeb\xec\xed\xee\xef\xf0\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xfb\xfc\xfd\xfe\xff"


def b64_ints(s):
    out = []
    buf = 0
    bits = 0
    for ch in s:
        v = B64R.get(ch)
        if v is None:
            continue
        buf = ((buf << 6) | v) & 0xFFFFFF
        bits += 6
        if bits >= 8:
            bits -= 8
            out.append((buf >> bits) & 255)
    return out


def ints_b64(byts):
    chunks = []
    out = []
    n = len(byts)
    for i in range(0, n, 3):
        b0 = byts[i]
        b1 = byts[i + 1] if i + 1 < n else 0
        b2 = byts[i + 2] if i + 2 < n else 0
        out.append(B64A[b0 >> 2] + B64A[((b0 & 3) << 4) | (b1 >> 4)]
                   + (B64A[((b1 & 15) << 2) | (b2 >> 6)] if i + 1 < n else "=") + (B64A[b2 & 63] if i + 2 < n else "="))
        if len(out) == 2048:
            chunks.append("".join(out))
            out = []
    chunks.append("".join(out))
    return "".join(chunks)


# ---------------- inflate (zlib) ----------------
LBASE = [3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 15, 17, 19, 23, 27, 31, 35, 43, 51, 59, 67, 83, 99, 115, 131, 163, 195, 227, 258]
LEXT = [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 0]
DBASE = [1, 2, 3, 4, 5, 7, 9, 13, 17, 25, 33, 49, 65, 97, 129, 193, 257, 385, 513, 769, 1025, 1537, 2049, 3073, 4097, 6145, 8193, 12289, 16385, 24577]
DEXT = [0, 0, 0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10, 11, 11, 12, 12, 13, 13]


def huff_table(lengths):
    # canonical Huffman -> dict keyed by (length, code)
    maxb = max(lengths) if lengths else 0
    count = [0] * (maxb + 1)
    for l in lengths:
        if l:
            count[l] += 1
    code = 0
    nxt = [0] * (maxb + 2)
    for b in range(1, maxb + 1):
        code = (code + count[b - 1]) << 1
        nxt[b] = code
    t = {}
    for sym in range(len(lengths)):
        l = lengths[sym]
        if l:
            t[(l << 16) | nxt[l]] = sym
            nxt[l] += 1
    return t


def inflate(data):
    # data: list of ints (zlib stream). returns list of ints.
    pos = [2, 0]  # byte index, bit index (skip zlib header)
    out = []

    def bit():
        b = (data[pos[0]] >> pos[1]) & 1
        pos[1] += 1
        if pos[1] == 8:
            pos[1] = 0
            pos[0] += 1
        return b

    def bits(n):
        v = 0
        for i in range(n):
            v |= bit() << i
        return v

    def decode(t):
        code = 0
        l = 0
        while True:
            code = (code << 1) | bit()
            l += 1
            s = t.get((l << 16) | code)
            if s is not None:
                return s

    fixed_l = huff_table([8] * 144 + [9] * 112 + [7] * 24 + [8] * 8)
    fixed_d = huff_table([5] * 30)
    final = 0
    while not final:
        final = bit()
        typ = bits(2)
        if typ == 0:
            if pos[1]:
                pos[1] = 0
                pos[0] += 1
            ln = data[pos[0]] | (data[pos[0] + 1] << 8)
            pos[0] += 4
            out.extend(data[pos[0]:pos[0] + ln])
            pos[0] += ln
            continue
        if typ == 1:
            lt, dt = fixed_l, fixed_d
        else:
            hlit = bits(5) + 257
            hdist = bits(5) + 1
            hclen = bits(4) + 4
            order = [16, 17, 18, 0, 8, 7, 9, 6, 10, 5, 11, 4, 12, 3, 13, 2, 14, 1, 15]
            cl = [0] * 19
            for i in range(hclen):
                cl[order[i]] = bits(3)
            ct = huff_table(cl)
            lens = []
            while len(lens) < hlit + hdist:
                s = decode(ct)
                if s < 16:
                    lens.append(s)
                elif s == 16:
                    lens.extend([lens[-1]] * (3 + bits(2)))
                elif s == 17:
                    lens.extend([0] * (3 + bits(3)))
                else:
                    lens.extend([0] * (11 + bits(7)))
            lt = huff_table(lens[:hlit])
            dt = huff_table(lens[hlit:])
        while True:
            s = decode(lt)
            if s < 256:
                out.append(s)
            elif s == 256:
                break
            else:
                s -= 257
                ln = LBASE[s] + bits(LEXT[s])
                d = decode(dt)
                dist = DBASE[d] + bits(DEXT[d])
                st = len(out) - dist
                for i in range(ln):
                    out.append(out[st + i])
    return out


# ---------------- deflate (fixed Huffman + LZ77) ----------------
def rev(v, n):
    r = 0
    for i in range(n):
        r = (r << 1) | ((v >> i) & 1)
    return r


FL = []
for _s in range(288):
    if _s < 144:
        FL.append((rev(0x30 + _s, 8), 8))
    elif _s < 256:
        FL.append((rev(0x190 + _s - 144, 9), 9))
    elif _s < 280:
        FL.append((rev(_s - 256, 7), 7))
    else:
        FL.append((rev(0xC0 + _s - 280, 8), 8))
LCODE = [0] * 259
for _c in range(29):
    for _k in range(LBASE[_c], (LBASE[_c + 1] if _c < 28 else 259)):
        LCODE[_k] = _c
LCODE[258] = 28


def dcode(d):
    c = 0
    while c < 29 and DBASE[c + 1] <= d:
        c += 1
    return c


CRCT = []
for _n in range(256):
    _c = _n
    for _k in range(8):
        _c = (0xEDB88320 ^ (_c >> 1)) if (_c & 1) else (_c >> 1)
    CRCT.append(_c)


def crc32(byts):
    c = 0xFFFFFFFF
    for v in byts:
        c = CRCT[(c ^ v) & 255] ^ (c >> 8)
    return c ^ 0xFFFFFFFF


def u32(v):
    return [(v >> 24) & 255, (v >> 16) & 255, (v >> 8) & 255, v & 255]


def chunk(typ, payload):
    t = [ord(ch) for ch in typ]
    return u32(len(payload)) + t + payload + u32(crc32(t + payload))


def to_bytes(ints):
    return b"".join([ALLB[v:v + 1] for v in ints])


# ---------------- PNG decode (embedded images) ----------------
def decode_png(byts):
    i = 8
    W = H = ct = 0
    idat = []
    plte = []
    trns = []
    while i < len(byts):
        ln = (byts[i] << 24) | (byts[i + 1] << 16) | (byts[i + 2] << 8) | byts[i + 3]
        typ = "".join([chr(c) for c in byts[i + 4:i + 8]])
        d = byts[i + 8:i + 8 + ln]
        if typ == "IHDR":
            W = (d[0] << 24) | (d[1] << 16) | (d[2] << 8) | d[3]
            H = (d[4] << 24) | (d[5] << 16) | (d[6] << 8) | d[7]
            ct = d[9]
        elif typ == "PLTE":
            plte = d
        elif typ == "tRNS":
            trns = d
        elif typ == "IDAT":
            idat.extend(d)
        i += 12 + ln
    raw = inflate(idat)
    bpp = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[ct]
    stride = W * bpp
    prev = [0] * stride
    rgba = []
    p = 0
    for y in range(H):
        f = raw[p]
        cur = raw[p + 1:p + 1 + stride]
        p += 1 + stride
        for k in range(stride):
            a = cur[k - bpp] if k >= bpp else 0
            b = prev[k]
            c = prev[k - bpp] if k >= bpp else 0
            v = cur[k]
            if f == 1:
                v += a
            elif f == 2:
                v += b
            elif f == 3:
                v += (a + b) >> 1
            elif f == 4:
                pa = abs(b - c)
                pb = abs(a - c)
                pc = abs(a + b - 2 * c)
                v += a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
            cur[k] = v & 255
        for x in range(W):
            if ct == 6:
                q = 4 * x
                rgba.append((cur[q + 3] << 24) | (cur[q] << 16) | (cur[q + 1] << 8) | cur[q + 2])
            elif ct == 2:
                q = 3 * x
                rgba.append((255 << 24) | (cur[q] << 16) | (cur[q + 1] << 8) | cur[q + 2])
            elif ct == 3:
                q = cur[x]
                al = trns[q] if q < len(trns) else 255
                rgba.append((al << 24) | (plte[3 * q] << 16) | (plte[3 * q + 1] << 8) | plte[3 * q + 2])
            elif ct == 4:
                rgba.append((cur[2 * x + 1] << 24) | (cur[2 * x] * 65793))
            else:
                rgba.append((255 << 24) | (cur[x] * 65793))
        prev = cur
    raw = None
    return W, H, rgba


# ---------------- canvas + rasterizer ----------------
NAMED = {"white": 0xFFFFFF, "black": 0, "red": 0xFF0000}


def parse_color(s):
    s = (s or "").strip()
    if not s or s == "none" or s.startswith("url"):
        return None
    if s in NAMED:
        return NAMED[s]
    if s.startswith("#"):
        h = s[1:]
        if len(h) == 3:
            h = h[0] * 2 + h[1] * 2 + h[2] * 2
        return int(h[:6], 16)
    return 0


def mat_mul(a, b):
    return [a[0] * b[0] + a[2] * b[1], a[1] * b[0] + a[3] * b[1], a[0] * b[2] + a[2] * b[3],
            a[1] * b[2] + a[3] * b[3], a[0] * b[4] + a[2] * b[5] + a[4], a[1] * b[4] + a[3] * b[5] + a[5]]


def parse_transform(s):
    m = [1, 0, 0, 1, 0, 0]
    for name, args in re.findall(r"(\w+)\s*\(([^)]*)\)", s or ""):
        v = [float(x) for x in re.findall(r"-?[\d.]+(?:e-?\d+)?", args)]
        if name == "translate":
            t = [1, 0, 0, 1, v[0], v[1] if len(v) > 1 else 0]
        elif name == "scale":
            t = [v[0], 0, 0, v[1] if len(v) > 1 else v[0], 0, 0]
        elif name == "rotate":
            a = v[0] * math.pi / 180
            t = [math.cos(a), math.sin(a), -math.sin(a), math.cos(a), 0, 0]
            if len(v) == 3:
                t = mat_mul([1, 0, 0, 1, v[1], v[2]], mat_mul(t, [1, 0, 0, 1, -v[1], -v[2]]))
        elif name == "matrix":
            t = v[:6]
        else:
            continue
        m = mat_mul(m, t)
    return m


def apply(m, x, y):
    return (m[0] * x + m[2] * y + m[4], m[1] * x + m[3] * y + m[5])


def blend(cv, idx, col, a):
    if a <= 0:
        return
    if a >= 1:
        cv["px"][idx] = col
        return
    o = cv["px"][idx]
    ia = 1 - a
    r = int(((o >> 16) & 255) * ia + ((col >> 16) & 255) * a + 0.5)
    g = int(((o >> 8) & 255) * ia + ((col >> 8) & 255) * a + 0.5)
    b = int((o & 255) * ia + (col & 255) * a + 0.5)
    cv["px"][idx] = (r << 16) | (g << 8) | b


def fill_polys(cv, polys, paint, crisp):
    edges = []
    ymin = 1e9
    ymax = -1e9
    for pts in polys:
        n = len(pts)
        for i in range(n):
            x0, y0 = pts[i]
            x1, y1 = pts[(i + 1) % n]
            if crisp:
                x0 = round(x0)
                y0 = round(y0)
                x1 = round(x1)
                y1 = round(y1)
            if y0 == y1:
                continue
            d = 1
            if y0 > y1:
                x0, y0, x1, y1 = x1, y1, x0, y0
                d = -1
            edges.append((y0, y1, x0, (x1 - x0) / (y1 - y0), d))
            if y0 < ymin:
                ymin = y0
            if y1 > ymax:
                ymax = y1
    if edges:
        edges.sort()
        cv["items"].append(("P", ymin, ymax, edges, paint, crisp))


def raster_poly(cv, it, by0, by1):
    ymin, ymax, edges, paint, crisp = it[1], it[2], it[3], it[4], it[5]
    W = cv["W"]
    px = cv["px"]
    solid = isinstance(paint, int)
    SS = 1 if crisp else 4
    ya = max(by0, int(ymin))
    yb = min(by1 - 1, int(math.ceil(ymax)))
    ne = len(edges)
    ei = 0
    active = []
    for py in range(ya, yb + 1):
        base = (py - by0) * W
        allspans = []
        for s in range(SS):
            sy = py + (s + 0.5) / SS
            while ei < ne and edges[ei][0] <= sy:
                active.append(edges[ei])
                ei += 1
            active = [e for e in active if sy < e[1]]
            xs = []
            for e in active:
                xs.append((e[2] + (sy - e[0]) * e[3], e[4]))
            spans = []
            if xs:
                xs.sort()
                wind = 0
                for k in range(len(xs) - 1):
                    wind += xs[k][1]
                    if wind == 0:
                        continue
                    xa = max(0.0, xs[k][0])
                    xb = min(float(W), xs[k + 1][0])
                    if xb > xa:
                        spans.append((xa, xb))
            allspans.append(spans)
        if crisp:
            for (xa, xb) in allspans[0]:
                ia = int(xa + 0.5)
                ib = int(xb + 0.5)
                if ib > ia:
                    if solid:
                        for x in range(base + ia, base + ib):
                            px[x] = paint
                    else:
                        for x in range(ia, ib):
                            px[base + x] = grad_color(paint, x + 0.5, py + 0.5)
            continue
        f0 = 0
        f1 = -1
        if all([len(sp) == 1 for sp in allspans]):
            f0 = int(math.ceil(max([sp[0][0] for sp in allspans])))
            f1 = int(math.floor(min([sp[0][1] for sp in allspans])))
        if f1 > f0:
            if solid:
                for x in range(base + f0, base + f1):
                    px[x] = paint
            else:
                grad_row(px, base, f0, f1, paint, py + 0.5)
        cov = {}
        for spans in allspans:
            for (xa, xb) in spans:
                ia = int(xa)
                ib = int(xb)
                if ia == ib:
                    if not (f0 <= ia and ia < f1):
                        cov[ia] = cov.get(ia, 0) + (xb - xa)
                    continue
                if not (f0 <= ia and ia < f1):
                    cov[ia] = cov.get(ia, 0) + (ia + 1 - xa)
                for x in range(ia + 1, min(ib, f0) if f1 > f0 else ib):
                    cov[x] = cov.get(x, 0) + 1
                if f1 > f0:
                    for x in range(max(ia + 1, f1), ib):
                        cov[x] = cov.get(x, 0) + 1
                if ib < W and not (f0 <= ib and ib < f1):
                    cov[ib] = cov.get(ib, 0) + (xb - ib)
        for x in cov:
            a = cov[x] / SS
            col = paint if solid else grad_color(paint, x + 0.5, py + 0.5)
            blend(cv, base + x, col, min(1.0, a))


def grad_row(px, base, x0, x1, g, y):
    bx0, by0, bx1, by1 = g["box"]
    w = (bx1 - bx0) or 1
    h = (by1 - by0) or 1
    dx = g["x2"] - g["x1"]
    dy = g["y2"] - g["y1"]
    den = (dx * dx + dy * dy) or 1
    v = (y - by0) / h
    t = (((x0 + 0.5 - bx0) / w - g["x1"]) * dx + (v - g["y1"]) * dy) / den
    dt = dx / w / den
    st = g["stops"]
    ns = len(st)
    k = 1
    for x in range(x0, x1):
        if t <= st[0][0]:
            col = st[0][1]
        elif t >= st[ns - 1][0]:
            col = st[ns - 1][1]
        else:
            while k > 1 and t < st[k - 1][0]:
                k -= 1
            while k < ns - 1 and t > st[k][0]:
                k += 1
            o0, c0 = st[k - 1]
            o1, c1 = st[k]
            f = (t - o0) / ((o1 - o0) or 1)
            col = ((int(((c0 >> 16) & 255) * (1 - f) + ((c1 >> 16) & 255) * f) << 16)
                   | (int(((c0 >> 8) & 255) * (1 - f) + ((c1 >> 8) & 255) * f) << 8)
                   | int((c0 & 255) * (1 - f) + (c1 & 255) * f))
        px[base + x] = col
        t += dt


def grad_color(g, x, y):
    bx0, by0, bx1, by1 = g["box"]
    w = (bx1 - bx0) or 1
    h = (by1 - by0) or 1
    u = (x - bx0) / w
    v = (y - by0) / h
    dx = g["x2"] - g["x1"]
    dy = g["y2"] - g["y1"]
    t = ((u - g["x1"]) * dx + (v - g["y1"]) * dy) / ((dx * dx + dy * dy) or 1)
    st = g["stops"]
    if t <= st[0][0]:
        return st[0][1]
    for k in range(1, len(st)):
        if t <= st[k][0]:
            o0, c0 = st[k - 1]
            o1, c1 = st[k]
            f = (t - o0) / ((o1 - o0) or 1)
            r = int(((c0 >> 16) & 255) * (1 - f) + ((c1 >> 16) & 255) * f)
            gg = int(((c0 >> 8) & 255) * (1 - f) + ((c1 >> 8) & 255) * f)
            b = int((c0 & 255) * (1 - f) + (c1 & 255) * f)
            return (r << 16) | (gg << 8) | b
    return st[-1][1]


# ---------------- path geometry ----------------
def rect_path(x, y, w, h, rx, ry):
    if rx <= 0 and ry <= 0:
        return [[(x, y), (x + w, y), (x + w, y + h), (x, y + h)]]
    rx = min(rx or ry, w / 2)
    ry = min(ry or rx, h / 2)
    pts = []
    for (cx, cy, a0) in ((x + w - rx, y + ry, -90), (x + w - rx, y + h - ry, 0), (x + rx, y + h - ry, 90), (x + rx, y + ry, 180)):
        for k in range(9):
            a = (a0 + k * 90 / 8) * math.pi / 180
            pts.append((cx + rx * math.cos(a), cy + ry * math.sin(a)))
    return [pts]


def arc_pts(x1, y1, rx, ry, phi, fa, fs, x2, y2):
    if rx == 0 or ry == 0:
        return [(x2, y2)]
    rx = abs(rx)
    ry = abs(ry)
    cp = math.cos(phi)
    sp = math.sin(phi)
    dx = (x1 - x2) / 2
    dy = (y1 - y2) / 2
    x1p = cp * dx + sp * dy
    y1p = -sp * dx + cp * dy
    lam = (x1p * x1p) / (rx * rx) + (y1p * y1p) / (ry * ry)
    if lam > 1:
        rx *= math.sqrt(lam)
        ry *= math.sqrt(lam)
    num = rx * rx * ry * ry - rx * rx * y1p * y1p - ry * ry * x1p * x1p
    den = rx * rx * y1p * y1p + ry * ry * x1p * x1p
    co = math.sqrt(max(0, num / den)) if den else 0
    if fa == fs:
        co = -co
    cxp = co * rx * y1p / ry
    cyp = -co * ry * x1p / rx
    cx = cp * cxp - sp * cyp + (x1 + x2) / 2
    cy = sp * cxp + cp * cyp + (y1 + y2) / 2

    def ang(ux, uy, vx, vy):
        a = math.atan2(ux * vy - uy * vx, ux * vx + uy * vy)
        return a

    t1 = ang(1, 0, (x1p - cxp) / rx, (y1p - cyp) / ry)
    dt = ang((x1p - cxp) / rx, (y1p - cyp) / ry, (-x1p - cxp) / rx, (-y1p - cyp) / ry)
    if not fs and dt > 0:
        dt -= 2 * math.pi
    elif fs and dt < 0:
        dt += 2 * math.pi
    n = max(4, int(abs(dt) / (math.pi / 16)))
    pts = []
    for k in range(1, n + 1):
        t = t1 + dt * k / n
        pts.append((cx + rx * math.cos(t) * cp - ry * math.sin(t) * sp, cy + rx * math.cos(t) * sp + ry * math.sin(t) * cp))
    return pts


def parse_path(d):
    toks = re.findall(r"[MmLlHhVvCcSsQqAaZz]|-?(?:\d+\.?\d*|\.\d+)(?:e-?\d+)?", d)
    subs = []
    cur = []
    i = 0
    x = y = 0.0
    sx = sy = 0.0
    cmd = ""
    lcx = lcy = None
    n = len(toks)

    def num():
        return float(toks[i])

    while i < n:
        t = toks[i]
        if t.isalpha():
            cmd = t
            i += 1
            if cmd in "Zz":
                if cur:
                    subs.append(cur)
                cur = []
                x, y = sx, sy
                continue
        c = cmd
        rel = c.islower()
        C = c.upper()
        if C == "M":
            nx = float(toks[i])
            ny = float(toks[i + 1])
            i += 2
            if rel:
                nx += x
                ny += y
            if cur:
                subs.append(cur)
            cur = [(nx, ny)]
            x, y = nx, ny
            sx, sy = nx, ny
            cmd = "l" if rel else "L"
        elif C == "L":
            nx = float(toks[i])
            ny = float(toks[i + 1])
            i += 2
            if rel:
                nx += x
                ny += y
            cur.append((nx, ny))
            x, y = nx, ny
        elif C == "H":
            nx = float(toks[i])
            i += 1
            x = nx + x if rel else nx
            cur.append((x, y))
        elif C == "V":
            ny = float(toks[i])
            i += 1
            y = ny + y if rel else ny
            cur.append((x, y))
        elif C in "CSQ":
            k = 6 if C == "C" else 4
            v = [float(toks[i + j]) for j in range(k)]
            i += k
            if rel:
                for j in range(0, k, 2):
                    v[j] += x
                    v[j + 1] += y
            if C == "S":
                c1x = 2 * x - lcx if lcx is not None else x
                c1y = 2 * y - lcy if lcy is not None else y
                v = [c1x, c1y] + v
            if C == "Q":
                q = v
                v = [x + 2 / 3 * (q[0] - x), y + 2 / 3 * (q[1] - y), q[2] + 2 / 3 * (q[0] - q[2]), q[3] + 2 / 3 * (q[1] - q[3]), q[2], q[3]]
            for s in range(1, 13):
                tt = s / 12
                mt = 1 - tt
                cur.append((mt * mt * mt * x + 3 * mt * mt * tt * v[0] + 3 * mt * tt * tt * v[2] + tt * tt * tt * v[4],
                            mt * mt * mt * y + 3 * mt * mt * tt * v[1] + 3 * mt * tt * tt * v[3] + tt * tt * tt * v[5]))
            lcx, lcy = v[2], v[3]
            x, y = v[4], v[5]
            continue
        elif C == "A":
            v = [float(toks[i + j]) for j in range(7)]
            i += 7
            nx, ny = v[5], v[6]
            if rel:
                nx += x
                ny += y
            cur.extend(arc_pts(x, y, v[0], v[1], v[2] * math.pi / 180, int(v[3]), int(v[4]), nx, ny))
            x, y = nx, ny
        lcx = lcy = None
    if cur:
        subs.append(cur)
    return [s for s in subs if len(s) > 1]


def circle_path(cx, cy, r):
    return [[(cx + r * math.cos(k * math.pi / 24), cy + r * math.sin(k * math.pi / 24)) for k in range(48)]]


def line_poly(x1, y1, x2, y2, w):
    dx = x2 - x1
    dy = y2 - y1
    L = math.sqrt(dx * dx + dy * dy) or 1
    nx = -dy / L * w / 2
    ny = dx / L * w / 2
    return [[(x1 + nx, y1 + ny), (x2 + nx, y2 + ny), (x2 - nx, y2 - ny), (x1 - nx, y1 - ny)]]


def stroke_poly(pts, w, closed):
    out = []
    n = len(pts)
    m = n if closed else n - 1
    for i in range(m):
        a = pts[i]
        b = pts[(i + 1) % n]
        out.extend(line_poly(a[0], a[1], b[0], b[1], w))
    return out


# ---------------- font ----------------
FONT = {}


def load_font(b64zip):
    d = inflate(b64_ints(b64zip))
    nw = d[0]
    ws = [d[1 + i] * 100 for i in range(nw)]
    p = 1 + nw
    for w in ws:
        M = d[p]
        asc = d[p + 1]
        hgt = d[p + 2]
        p += 3
        glyphs = {}
        for c in range(32, 127):
            adv = (d[p] << 8) | d[p + 1]
            left = d[p + 2] - 128
            gw = d[p + 3]
            p += 4
            glyphs[c] = [adv / 4.0, left, gw, None]
        order = list(range(32, 127))
        nx = d[p]
        p += 1
        for _k in range(nx):
            cp = (d[p] << 8) | d[p + 1]
            adv = (d[p + 2] << 8) | d[p + 3]
            glyphs[cp] = [adv / 4.0, d[p + 4] - 128, d[p + 5], None]
            order.append(cp)
            p += 6
        for c in order:
            g = glyphs[c]
            npx = g[2] * hgt
            nbytes = (npx + 3) // 4
            g[3] = d[p:p + nbytes]
            p += nbytes
        FONT[w] = {"M": M, "asc": asc, "h": hgt, "g": glyphs}


def glyph_alpha(g, hgt, gx, gy):
    if gx < 0 or gy < 0 or gx >= g[2] or gy >= hgt:
        return 0
    k = gy * g[2] + gx
    return ((g[3][k >> 2] >> ((k & 3) * 2)) & 3) / 3.0


ACC = {"à": "a", "á": "a", "â": "a", "ä": "a", "ã": "a", "å": "a", "ç": "c", "è": "e", "é": "e", "ê": "e", "ë": "e",
       "ì": "i", "í": "i", "î": "i", "ï": "i", "ñ": "n", "ò": "o", "ó": "o", "ô": "o", "ö": "o", "õ": "o", "ù": "u",
       "ú": "u", "û": "u", "ü": "u", "ý": "y", "ÿ": "y", "’": "'", "‘": "'", "“": '"', "”": '"', "–": "-", "—": "-",
       "•": "*", "→": ">", "·": "."}


def norm_text(s):
    out = []
    known = FONT[400]["g"]
    for ch in s:
        lo = ch.lower()
        if ord(ch) in known:
            out.append(ch)
        elif lo in ACC:
            r = ACC[lo]
            out.append(r.upper() if ch != lo else r)
        elif 32 <= ord(ch) < 127:
            out.append(ch)
        else:
            out.append("?")
    return "".join(out)


def font_for(weight):
    w = int(weight or 400)
    want = 700 if w >= 650 else (600 if w >= 500 else 400)
    if want in FONT:
        return FONT[want]
    return FONT[700] if want == 600 and 700 in FONT else FONT[400]


def text_width(s, size, weight):
    f = font_for(weight)
    sc = size / f["M"]
    return sum([f["g"][ord(ch)][0] for ch in s]) * sc


def draw_text(cv, m, x, y, s, size, weight, col, anchor):
    s = norm_text(s)
    f = font_for(weight)
    tw = text_width(s, size, weight)
    vw = cv.get("fit_w")
    if vw:
        if anchor == "middle":
            room = 2 * (min(x, vw - x) - 4)
        elif anchor == "end":
            room = x - min(vw - x, 28)
        else:
            room = vw - x - min(x, 28)
        if room > 20 and tw > room:
            size = size * room / tw
            tw = room
    if anchor == "middle":
        x -= tw / 2
    elif anchor == "end":
        x -= tw
    k = math.sqrt(abs(m[0] * m[3] - m[1] * m[2]))
    ox, oy = apply(m, x, y)
    sc = size * k / f["M"]
    top = oy - f["asc"] * sc
    cv["items"].append(("T", top, top + f["h"] * sc, ox, s, sc, f, col))


def raster_text(cv, it, by0, by1):
    top, ox, s, sc, f, col = it[1], it[3], it[4], it[5], it[6], it[7]
    pen = ox
    W = cv["W"]
    hgt = f["h"]
    inv = 1.0 / sc
    for ch in s:
        g = f["g"][ord(ch)]
        gw = g[2]
        gd = g[3]
        gx0 = pen + (g[1] - 1) * sc
        if gw > 1 and ch != " ":
            dx0 = max(0, int(gx0))
            dx1 = min(W, int(gx0 + gw * sc) + 1)
            for py in range(max(by0, int(top)), min(by1, int(top + hgt * sc) + 1)):
                fy = (py + 0.5 - top) * inv - 0.5
                iy = int(math.floor(fy))
                ty = fy - iy
                r0 = iy * gw if 0 <= iy and iy < hgt else -1
                r1 = (iy + 1) * gw if 0 <= iy + 1 and iy + 1 < hgt else -1
                if r0 < 0 and r1 < 0:
                    continue
                base = (py - by0) * W
                for px in range(dx0, dx1):
                    fx = (px + 0.5 - gx0) * inv - 0.5
                    ix = int(math.floor(fx))
                    tx = fx - ix
                    a00 = a10 = a01 = a11 = 0
                    if 0 <= ix and ix < gw:
                        if r0 >= 0:
                            k = r0 + ix
                            a00 = (gd[k >> 2] >> ((k & 3) * 2)) & 3
                        if r1 >= 0:
                            k = r1 + ix
                            a01 = (gd[k >> 2] >> ((k & 3) * 2)) & 3
                    if 0 <= ix + 1 and ix + 1 < gw:
                        if r0 >= 0:
                            k = r0 + ix + 1
                            a10 = (gd[k >> 2] >> ((k & 3) * 2)) & 3
                        if r1 >= 0:
                            k = r1 + ix + 1
                            a11 = (gd[k >> 2] >> ((k & 3) * 2)) & 3
                    if a00 + a10 + a01 + a11 == 0:
                        continue
                    a = ((a00 * (1 - tx) + a10 * tx) * (1 - ty) + (a01 * (1 - tx) + a11 * tx) * ty) / 3.0
                    if a > 0.01:
                        blend(cv, base + px, col, a)
        pen += g[0] * sc


# ---------------- SVG walker ----------------
def attrs_of(tag):
    a = {}
    for k, v in re.findall(r'([\w:-]+)\s*=\s*"([^"]*)"', tag):
        a[k] = v
    return a


def unesc(s):
    out = []
    i = 0
    n = len(s)
    while i != n:
        j = s.find("&#", i)
        if j == -1:
            out.append(s[i:])
            break
        k = s.find(";", j)
        if k == -1:
            out.append(s[i:])
            break
        out.append(s[i:j])
        t = s[j + 2:k]
        v = -1
        if t[:1] in ("x", "X") and len(t) > 1:
            v = int(t[1:], 16)
        elif t.isdigit():
            v = int(t)
        out.append(chr(v) if v != -1 else s[j:k + 1])
        i = k + 1
    s = "".join(out)
    return s.replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"').replace("&#39;", "'").replace("&apos;", "'").replace("&amp;", "&")

def draw_image(cv, m, a):
    href = a.get("href") or a.get("xlink:href") or ""
    x = float(a.get("x", 0))
    y = float(a.get("y", 0))
    w = float(a.get("width", 0))
    h = float(a.get("height", 0))
    if href.startswith("data:image/svg+xml;base64,"):
        inner = "".join([chr(c) for c in b64_ints(href[26:])])
        vb = re.search(r'viewBox="([^"]+)"', inner)
        v = [float(t) for t in vb.group(1).split()] if vb else [0, 0, w, h]
        t = mat_mul(m, [w / v[2], 0, 0, h / v[3], x - v[0] * w / v[2], y - v[1] * h / v[3]])
        fw = cv["fit_w"]
        cv["fit_w"] = None
        walk(cv, inner, t)
        cv["fit_w"] = fw
        return
    if not href.startswith("data:image/png;base64,"):
        return
    x0, y0 = apply(m, x, y)
    x1, y1 = apply(m, x + w, y + h)
    dw = max(1, int(round(x1 - x0)))
    dh = max(1, int(round(y1 - y0)))
    key = href[-40:] + "|" + str(dw) + "x" + str(dh)
    cache = cv["imgcache"]
    if key not in cache:
        iw, ih, src = decode_png(b64_ints(href[22:]))
        small = []
        for yy in range(dh):
            sy = min(ih - 1, int((yy + 0.5) * ih / dh))
            for xx in range(dw):
                small.append(src[sy * iw + min(iw - 1, int((xx + 0.5) * iw / dw))])
        src = None
        cache[key] = (dw, dh, small)
    cv["items"].append(("I", y0, y0 + dh, x0, x0 + dw, key))


def raster_image(cv, it, by0, by1):
    y0, x0 = it[1], it[3]
    dw, dh, px = cv["imgcache"][it[5]]
    W = cv["W"]
    ix0 = int(round(x0))
    iy0 = int(round(y0))
    for yy in range(max(by0, iy0), min(by1, iy0 + dh)):
        row = (yy - iy0) * dw
        for xx in range(max(0, ix0), min(W, ix0 + dw)):
            v = px[row + xx - ix0]
            al = (v >> 24) & 255
            if al:
                blend(cv, (yy - by0) * W + xx, v & 0xFFFFFF, al / 255.0)


def bbox(polys):
    xs = [p[0] for s in polys for p in s]
    ys = [p[1] for s in polys for p in s]
    return (min(xs), min(ys), max(xs), max(ys))


def walk(cv, svg, base):
    stack = [(base, {})]
    grads = cv["grads"]
    for gid, gx, body in re.findall(r'<linearGradient\s+id="([^"]+)"([^>]*)>(.*?)</linearGradient>', svg.replace("\n", " ")):
        ga = attrs_of(gx)
        stops = []
        for st in re.findall(r"<stop[^>]*>", body):
            sa = attrs_of(st)
            off = sa.get("offset", "0")
            o = float(off[:-1]) / 100 if off.endswith("%") else float(off)
            stops.append((o, parse_color(sa.get("stop-color", "#000"))))
        grads[gid] = {"x1": float(ga.get("x1", 0)), "y1": float(ga.get("y1", 0)), "x2": float(ga.get("x2", 1)),
                      "y2": float(ga.get("y2", 0)), "stops": stops}
    body = svg
    a0 = body.find("<defs>")
    if a0 != -1:
        a1 = body.find("</defs>", a0)
        if a1 != -1:
            body = body[:a0] + body[a1 + 7:]
    for m_ in re.finditer(r"<(/?)(\w+)([^>]*?)(/?)>([^<]*)", body):
        close, name, rest, selfc, after = m_.group(1), m_.group(2), m_.group(3), m_.group(4), m_.group(5)
        if name == "svg":
            if not close:
                a = attrs_of(rest)
                vb = a.get("viewBox")
                if vb and len(stack) == 1 and cv.get("scale"):
                    pass
            continue
        if close:
            if name == "g" and len(stack) > 1:
                stack.pop()
            continue
        a = attrs_of(rest)
        pm, inh = stack[-1]
        m = mat_mul(pm, parse_transform(a.get("transform"))) if a.get("transform") else pm
        st = dict(inh)
        for k in ("fill", "stroke", "stroke-width", "font-size", "font-weight", "text-anchor", "shape-rendering"):
            if k in a:
                st[k] = a[k]
        if name == "g":
            if not selfc:
                stack.append((m, st))
            continue
        fill_s = st.get("fill", "#000")
        stroke = parse_color(st.get("stroke"))
        sw = float(st.get("stroke-width", 1))
        crisp = st.get("shape-rendering") == "crispEdges"
        polys = None
        closed = True
        if name == "rect":
            polys = rect_path(float(a.get("x", 0)), float(a.get("y", 0)), float(a.get("width", 0)), float(a.get("height", 0)),
                              float(a.get("rx", a.get("ry", 0))), float(a.get("ry", a.get("rx", 0))))
        elif name == "circle":
            polys = circle_path(float(a.get("cx", 0)), float(a.get("cy", 0)), float(a.get("r", 0)))
        elif name == "path":
            polys = parse_path(a.get("d", ""))
        elif name == "line":
            x1 = float(a.get("x1", 0))
            y1 = float(a.get("y1", 0))
            x2 = float(a.get("x2", 0))
            y2 = float(a.get("y2", 0))
            if stroke is not None:
                fill_polys(cv, [[apply(m, p[0], p[1]) for p in s] for s in line_poly(x1, y1, x2, y2, sw)], stroke, crisp)
            continue
        elif name == "text":
            col = parse_color(fill_s)
            if col is None:
                col = 0
            draw_text(cv, m, float(a.get("x", 0)), float(a.get("y", 0)), unesc(after), float(st.get("font-size", 16)),
                      st.get("font-weight", 400), col, st.get("text-anchor", "start"))
            continue
        elif name == "image":
            draw_image(cv, m, a)
            continue
        if not polys:
            continue
        dev = [[apply(m, p[0], p[1]) for p in s] for s in polys]
        if fill_s.startswith("url(#"):
            g = grads.get(fill_s[5:-1])
            if g:
                g2 = dict(g)
                g2["box"] = bbox(dev)
                fill_polys(cv, dev, g2, crisp)
        else:
            col = parse_color(fill_s)
            if col is not None:
                fill_polys(cv, dev, col, crisp)
        if stroke is not None:
            k = math.sqrt(abs(m[0] * m[3] - m[1] * m[2]))
            sp = []
            for s in dev:
                sp.extend(stroke_poly(s, sw * k, closed))
            fill_polys(cv, sp, stroke, crisp)


def svg_to_png(svg, scale, bg):
    vb = re.search(r'viewBox="([^"]+)"', svg)
    v = [float(t) for t in vb.group(1).split()]
    W = int(round(v[2] * scale))
    H = int(round(v[3] * scale))
    cv = {"W": W, "H": H, "px": [], "grads": {}, "fit_w": v[2], "items": [], "imgcache": {}}
    walk(cv, svg, [scale, 0, 0, scale, -v[0] * scale, -v[1] * scale])
    items = cv["items"]
    BAND = 32
    chunks = []
    prev = [0] * W
    acc = 0
    nb_ = 0
    ad_a = 1
    ad_b = 0
    Z0, Z0N = FL[0]
    ZM = []
    for m in range(3, 259):
        c = LCODE[m]
        code, nb = FL[257 + c]
        ZM.append((code | ((m - LBASE[c]) << nb), nb + LEXT[c]))
    out = [0x78, 0x01]
    for by0 in range(0, H, BAND):
        by1 = min(H, by0 + BAND)
        cv["px"] = [bg] * (W * (by1 - by0))
        for it in items:
            if it[2] < by0 or it[1] > by1:
                continue
            if it[0] == "P":
                raster_poly(cv, it, by0, by1)
            elif it[0] == "T":
                raster_text(cv, it, by0, by1)
            else:
                raster_image(cv, it, by0, by1)
        acc |= (3 if by1 == H else 2) << nb_
        nb_ += 3
        px = cv["px"]
        for y in range(by1 - by0):
            base = y * W
            cur = px[base:base + W]
            code, nb = FL[2]
            acc |= code << nb_
            nb_ += nb
            ad_a += 2
            ad_b += ad_a
            z = 0
            if cur == prev:
                z = 3 * W
            else:
                for x in range(W + 1):
                    if x != W:
                        c = cur[x]
                        q = prev[x]
                        if c == q:
                            z += 3
                            continue
                    if z:
                        ad_b += ad_a * z
                        acc |= Z0 << nb_
                        nb_ += Z0N
                        z -= 1
                        while z >= 3:
                            m = 258 if z > 258 else z
                            code, nb = ZM[m - 3]
                            acc |= code << nb_
                            nb_ += nb + 5
                            z -= m
                        while z:
                            acc |= Z0 << nb_
                            nb_ += Z0N
                            z -= 1
                        while nb_ >= 8:
                            out.append(acc & 255)
                            acc >>= 8
                            nb_ -= 8
                    if x == W:
                        break
                    for v in ((((c >> 16) & 255) - ((q >> 16) & 255)) & 255, (((c >> 8) & 255) - ((q >> 8) & 255)) & 255, ((c & 255) - (q & 255)) & 255):
                        code, nb = FL[v]
                        acc |= code << nb_
                        nb_ += nb
                        ad_a += v
                        ad_b += ad_a
                    while nb_ >= 8:
                        out.append(acc & 255)
                        acc >>= 8
                        nb_ -= 8
                prev = cur
            if z:
                ad_b += ad_a * z
                acc |= Z0 << nb_
                nb_ += Z0N
                z -= 1
                while z >= 3:
                    m = 258 if z > 258 else z
                    code, nb = ZM[m - 3]
                    acc |= code << nb_
                    nb_ += nb + 5
                    z -= m
                while z:
                    acc |= Z0 << nb_
                    nb_ += Z0N
                    z -= 1
            while nb_ >= 8:
                out.append(acc & 255)
                acc >>= 8
                nb_ -= 8
            ad_a %= 65521
            ad_b %= 65521
        code, nb = FL[256]
        acc |= code << nb_
        nb_ += nb
        while nb_ >= 8:
            out.append(acc & 255)
            acc >>= 8
            nb_ -= 8
        if by1 == H:
            if nb_:
                out.append(acc & 255)
            out.extend([ad_b >> 8, ad_b & 255, ad_a >> 8, ad_a & 255])
        else:
            nb_ += 3
            while nb_ >= 8:
                out.append(acc & 255)
                acc >>= 8
                nb_ -= 8
            if nb_:
                out.append(acc & 255)
            acc = 0
            nb_ = 0
            out.extend([0, 0, 255, 255])
        chunks.append(to_bytes(out))
        out = []
        cv["px"] = []
    data = b"".join(chunks)
    t = [73, 68, 65, 84]
    c = 0xFFFFFFFF
    for v in t:
        c = CRCT[(c ^ v) & 255] ^ (c >> 8)
    for v in data:
        c = CRCT[(c ^ v) & 255] ^ (c >> 8)
    c ^= 0xFFFFFFFF
    ihdr = u32(W) + u32(H) + [8, 2, 0, 0, 0]
    pre = [137, 80, 78, 71, 13, 10, 26, 10] + chunk("IHDR", ihdr) + u32(len(data)) + t
    post = u32(c) + chunk("IEND", [])
    return to_bytes(pre) + data + to_bytes(post)
