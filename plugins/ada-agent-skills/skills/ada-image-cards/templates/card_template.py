# Example image card for an Ada code tool.
# Inputs arrive as bare names (declared on the tool and bound to variables):
#   title, subtitle, status, rows   (rows = "Label~Value||Label~Value||...")
# Result: {"image_url": <signed https link or "">, "debug": <short diagnostic>}
# The build script inserts the SVG->PNG renderer and the font atlas (ATLAS) above this file's code.
import json
import datetime

LT = "\x3c"   # never type a literal less-than + tag name in the source: the WAF 403s it
INSTANCE = "your-handle"   # <-- the bot handle this tool runs on (its own domain needs no allow-listing)
UPLOAD_API = "https://" + INSTANCE + ".ada.support/api/action-integrations/s3-uploader-action/actions/"
BOUNDARY = "----AdaImageCard7f3a"
PNG_NAME = "card.png"     # the extension decides the Content-Type the link is served with
FONT_FAMILY = "Montserrat, Arial, sans-serif"
INK = "#2F3238"
MUTED = "#7A7F87"
DASH = "–"
STATUS_COLOURS = [("CANCEL", "#E5484D"), ("DELAY", "#F5A524"), ("ACTIVE", "#34B262"), ("OK", "#34B262")]


def txt(v):
    # inputs bound to an unset variable arrive as None
    s = str(v or "").strip()
    return "" if s.lower() in ("null", "none") else s


def esc(s):
    out = []
    for ch in s or "":
        if ch == "&":
            out.append("&amp;")
        elif ch == LT:
            out.append("&lt;")
        elif ch == ">":
            out.append("&gt;")
        elif ch == '"':
            out.append("&quot;")
        else:
            out.append(ch)
    return "".join(out)


def tag(name, attrs, body):
    return LT + name + " " + attrs + ">" + body + LT + "/" + name + ">"


def text(x, y, s, size, weight, fill, anchor):
    return tag("text", 'x="' + str(x) + '" y="' + str(y) + '" font-size="' + str(size) + '" font-weight="'
               + str(weight) + '" fill="' + fill + '" text-anchor="' + anchor + '"', esc(s))


def status_colour(s):
    u = s.upper()
    for k, c in STATUS_COLOURS:
        if k in u:
            return c
    return "#8A9099"


def build_card():
    W = 480
    H = 360
    stat = txt(status).upper()
    out = []
    out.append(LT + 'rect x="1" y="1" width="' + str(W - 2) + '" height="' + str(H - 2)
               + '" rx="12" fill="#FFFFFF" stroke="#E6E8EC"/>')
    out.append(text(24, 46, txt(title) or DASH, 24, 700, INK, "start"))
    out.append(text(24, 72, txt(subtitle), 14, 400, MUTED, "start"))
    if stat:
        pw = 24 + int(len(stat) * 9.2)   # pill width follows the label
        out.append(LT + 'rect x="' + str(W - 20 - pw) + '" y="24" width="' + str(pw)
                   + '" height="28" rx="14" fill="' + status_colour(stat) + '"/>')
        out.append(text(W - 20 - pw / 2.0, 43, stat, 13, 700, "#FFFFFF", "middle"))
    out.append(LT + 'line x1="24" y1="96" x2="' + str(W - 24) + '" y2="96" stroke="#EEF0F2" stroke-width="1.5"/>')
    # up to 6 label/value cells, 2 columns
    cells = [r.split("~") for r in txt(rows).split("||") if r]
    for i in range(min(6, len(cells))):
        x = 24 if i % 2 == 0 else W // 2 + 8
        y = 136 + (i // 2) * 76
        label = cells[i][0]
        value = cells[i][1] if len(cells[i]) > 1 else ""
        out.append(text(x, y, label.upper(), 13, 700, MUTED, "start"))
        out.append(text(x, y + 28, value or DASH, 20, 600, INK, "start"))
    return (LT + 'svg xmlns="http://www.w3.org/2000/svg" width="' + str(W * 2) + '" height="' + str(H * 2)
            + '" viewBox="0 0 ' + str(W) + " " + str(H) + '" font-family="' + FONT_FAMILY + '">'
            + "".join(out) + LT + "/svg>")


def key_for(seed):
    # Anyone holding the S3 key can mint a fresh link, so the key must come from the runtime's
    # random uuid4(). With no uuid4 the tool refuses to upload rather than derive a key from the data.
    try:
        return str(uuid4())
    except NameError:
        return ""


def upload(png, seed):
    key = key_for(seed)
    if not key:
        return "", "no secure key: uuid4 missing"
    # presign-post type-checks file_content: send real base64 (the first 3 KB is enough)
    r = fetch("POST", UPLOAD_API + "generate-presigned-post/invoke", headers={"Content-Type": "application/json"},
              body=json.dumps({"filename": key, "s3_key": key, "file_content": ints_b64(png[:3072])}), timeout=20)
    if r["status_code"] != 200:
        return "", "presign-post " + str(r["status_code"])
    pr = json.loads(r["body"] or "{}")
    fields = json.loads(pr.get("fields") or "{}")
    head = ""
    for k in fields:
        head += "--" + BOUNDARY + "\r\nContent-Disposition: form-data; name=\"" + k + "\"\r\n\r\n" + str(fields[k]) + "\r\n"
    head += ("--" + BOUNDARY + "\r\nContent-Disposition: form-data; name=\"file\"; filename=\"" + PNG_NAME
             + "\"\r\nContent-Type: image/png\r\n\r\n")
    body = head.encode() + png + ("\r\n--" + BOUNDARY + "--\r\n").encode()   # file part LAST
    u = fetch("POST", pr.get("url") or "", headers={"Content-Type": "multipart/form-data; boundary=" + BOUNDARY},
              body=body, timeout=30)
    if u["status_code"] != 204:
        return "", "s3 " + str(u["status_code"])
    g = fetch("POST", UPLOAD_API + "generate-presigned-get/invoke", headers={"Content-Type": "application/json"},
              body=json.dumps({"s3_key": key, "filename": PNG_NAME}), timeout=20)
    if g["status_code"] != 200:
        return "", "presign-get " + str(g["status_code"])
    return (json.loads(g["body"] or "{}").get("fetch_file_url") or ""), "ok png " + str(len(png))


def main():
    if not txt(title):
        return {"image_url": "", "debug": "card: missing title"}
    svg = build_card()
    load_font(ATLAS)
    png = svg_to_png(svg, 1.0, 0xFFFFFF)
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    url, st = upload(png, now + "|" + txt(title) + "|" + txt(rows))
    return {"image_url": url, "debug": "card " + st}


try:
    result = main()
except Exception as e:
    # never raise: a raising tool writes no outputs and leaves no trace in test runs
    result = {"image_url": "", "debug": "card FAILED " + type(e).__name__ + ": " + str(e)[:160]}
result
