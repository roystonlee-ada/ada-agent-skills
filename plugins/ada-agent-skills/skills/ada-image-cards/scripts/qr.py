# Pure-Python QR encoder for Ada code tools (byte mode, ECC level L, versions 1-10, mask 0).
# qr_matrix(text) -> list of rows of 0/1 modules; qr_path(mods) -> SVG path "d" for the dark modules (1 unit each).
# Draw with: LT + 'path d="' + qr_path(m) + '" fill="#000" transform="translate(x y) scale(module_px)"/>'
# ---------------------------------------------------------------- QR encoder (byte mode, ECC L)
# version: (ec codewords per block, blocks g1, data per block g1, blocks g2, data per block g2)
ECC_L = {1: (7, 1, 19, 0, 0), 2: (10, 1, 34, 0, 0), 3: (15, 1, 55, 0, 0), 4: (20, 1, 80, 0, 0),
         5: (26, 1, 108, 0, 0), 6: (18, 2, 68, 0, 0), 7: (20, 2, 78, 0, 0), 8: (24, 2, 97, 0, 0),
         9: (30, 2, 116, 0, 0), 10: (18, 2, 68, 2, 69)}
ALIGN = {1: [], 2: [6, 18], 3: [6, 22], 4: [6, 26], 5: [6, 30], 6: [6, 34], 7: [6, 22, 38],
         8: [6, 24, 42], 9: [6, 26, 46], 10: [6, 28, 50]}


def gf_mul(x, y):
    z = 0
    for i in range(7, -1, -1):
        z = (z << 1) ^ ((z >> 7) * 0x11D)
        z = z ^ (((y >> i) & 1) * x)
    return z


def rs_divisor(deg):
    res = [0] * (deg - 1) + [1]
    root = 1
    for i in range(deg):
        for j in range(deg):
            res[j] = gf_mul(res[j], root)
            if j + 1 < deg:
                res[j] = res[j] ^ res[j + 1]
        root = gf_mul(root, 2)
    return res


def rs_remainder(data, div):
    res = [0] * len(div)
    for b in data:
        factor = b ^ res[0]
        res = res[1:] + [0]
        for i in range(len(div)):
            res[i] = res[i] ^ gf_mul(div[i], factor)
    return res


def utf8(s):
    out = []
    for ch in s:
        c = ord(ch)
        if c < 0x80:
            out.append(c)
        elif c < 0x800:
            out.append(0xC0 | (c >> 6))
            out.append(0x80 | (c & 63))
        elif c < 0x10000:
            out.append(0xE0 | (c >> 12))
            out.append(0x80 | ((c >> 6) & 63))
            out.append(0x80 | (c & 63))
        else:
            out.append(0xF0 | (c >> 18))
            out.append(0x80 | ((c >> 12) & 63))
            out.append(0x80 | ((c >> 6) & 63))
            out.append(0x80 | (c & 63))
    return out


def qr_matrix(text):
    data = utf8(text)
    ver = 0
    for v in range(1, 11):
        ec, b1, d1, b2, d2 = ECC_L[v]
        cap_bits = (b1 * d1 + b2 * d2) * 8
        need = 4 + (8 if v < 10 else 16) + 8 * len(data)
        if need <= cap_bits:
            ver = v
            break
    if ver == 0:
        return None
    ec, b1, d1, b2, d2 = ECC_L[ver]
    cap_bytes = b1 * d1 + b2 * d2
    bits = []

    def put(val, n):
        for i in range(n - 1, -1, -1):
            bits.append((val >> i) & 1)

    put(4, 4)
    put(len(data), 8 if ver < 10 else 16)
    for b in data:
        put(b, 8)
    put(0, min(4, cap_bytes * 8 - len(bits)))
    while len(bits) % 8:
        bits.append(0)
    cw = []
    for i in range(0, len(bits), 8):
        v = 0
        for j in range(8):
            v = (v << 1) | bits[i + j]
        cw.append(v)
    pad = [0xEC, 0x11]
    k = 0
    while len(cw) < cap_bytes:
        cw.append(pad[k % 2])
        k += 1

    blocks = []
    pos = 0
    for n, ln in [(b1, d1), (b2, d2)]:
        for i in range(n):
            blocks.append(cw[pos:pos + ln])
            pos += ln
    div = rs_divisor(ec)
    ecs = [rs_remainder(b, div) for b in blocks]
    final = []
    longest = max([len(b) for b in blocks])
    for i in range(longest):
        for b in blocks:
            if i < len(b):
                final.append(b[i])
    for i in range(ec):
        for e in ecs:
            final.append(e[i])

    size = 17 + 4 * ver
    mods = [[0] * size for _ in range(size)]
    func = [[0] * size for _ in range(size)]

    def setf(x, y, dark):
        mods[y][x] = 1 if dark else 0
        func[y][x] = 1

    for i in range(size):
        setf(6, i, i % 2 == 0)
        setf(i, 6, i % 2 == 0)
    for cx, cy in [(3, 3), (size - 4, 3), (3, size - 4)]:
        for dy in range(-4, 5):
            for dx in range(-4, 5):
                xx = cx + dx
                yy = cy + dy
                if 0 <= xx < size and 0 <= yy < size:
                    d = max(abs(dx), abs(dy))
                    setf(xx, yy, d != 2 and d != 4)
    al = ALIGN[ver]
    last = len(al) - 1
    for i in range(len(al)):
        for j in range(len(al)):
            if (i == 0 and j == 0) or (i == 0 and j == last) or (i == last and j == 0):
                continue
            for dy in range(-2, 3):
                for dx in range(-2, 3):
                    setf(al[i] + dx, al[j] + dy, max(abs(dx), abs(dy)) != 1)

    def draw_format(mask):
        d = (1 << 3) | mask  # ECC L = 01
        rem = d
        for _ in range(10):
            rem = (rem << 1) ^ ((rem >> 9) * 0x537)
        fb = ((d << 10) | rem) ^ 0x5412
        for i in range(6):
            setf(8, i, (fb >> i) & 1)
        setf(8, 7, (fb >> 6) & 1)
        setf(8, 8, (fb >> 7) & 1)
        setf(7, 8, (fb >> 8) & 1)
        for i in range(9, 15):
            setf(14 - i, 8, (fb >> i) & 1)
        for i in range(8):
            setf(size - 1 - i, 8, (fb >> i) & 1)
        for i in range(8, 15):
            setf(8, size - 15 + i, (fb >> i) & 1)
        setf(8, size - 8, True)

    draw_format(0)
    if ver >= 7:
        rem = ver
        for _ in range(12):
            rem = (rem << 1) ^ ((rem >> 11) * 0x1F25)
        vb = (ver << 12) | rem
        for i in range(18):
            bit = (vb >> i) & 1
            a = size - 11 + i % 3
            b = i // 3
            setf(a, b, bit)
            setf(b, a, bit)

    i = 0
    total = len(final) * 8
    right = size - 1
    while right >= 1:
        if right == 6:
            right = 5
        for vert in range(size):
            for j in range(2):
                x = right - j
                upward = ((right + 1) & 2) == 0
                y = size - 1 - vert if upward else vert
                if not func[y][x] and i < total:
                    mods[y][x] = (final[i >> 3] >> (7 - (i & 7))) & 1
                    i += 1
        right -= 2

    for y in range(size):  # mask 0: (x + y) % 2 == 0
        for x in range(size):
            if not func[y][x] and (x + y) % 2 == 0:
                mods[y][x] = mods[y][x] ^ 1
    draw_format(0)
    return mods


def qr_path(mods):
    d = []
    for y in range(len(mods)):
        x = 0
        n = len(mods)
        while x < n:
            if mods[y][x]:
                s = x
                while x < n and mods[y][x]:
                    x += 1
                d.append("M" + str(s) + " " + str(y) + "h" + str(x - s) + "v1h-" + str(x - s) + "z")
            else:
                x += 1
    return "".join(d)
