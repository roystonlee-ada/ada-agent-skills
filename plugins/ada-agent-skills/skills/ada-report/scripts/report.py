#!/usr/bin/env python3
"""Render an Ada-branded report from a JSON spec, as one self-contained HTML file.

    python3 report.py <spec.json> [-o out.html] [--open]

The spec shape is in references/report-spec.md. Tip copy comes from
references/tips.json. Transcript text is masked for emails, phone numbers and
long digit runs. stdout is the output path. stderr lists warnings and ends in
`done` or an `error:` line.
"""
from __future__ import annotations

import argparse
import html
import json
import pathlib
import re
import sys
import urllib.parse
import webbrowser

HERE = pathlib.Path(__file__).resolve().parent
TIPS = json.loads((HERE.parent / "references" / "tips.json").read_text())
e = html.escape

MASKS = [
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"), "[email]"),
    (re.compile(r"\+?\d[\d\s().-]{7,}\d"), "[number]"),
]
JARGON = re.compile(r"\b(LLM|URE|ClickHouse|generative_|reasoning engine|prompt|token|JSON|API call|endpoint|webhook)\b", re.I)
HARSH = re.compile(r"\b(fail(ed|ure|s)?|broken|bad|poor|wrong)\b", re.I)
LINK_HOSTS = ("ada.support", "ada.cx")
MAX_TIPS = 4
MAX_TRANSCRIPTS = 4


def mask(text: str, counter: list[int]) -> str:
    for pattern, label in MASKS:
        text, n = pattern.subn(label, text)
        counter[0] += n
    return text


def safe_url(url: str) -> str:
    """Return the URL only if it is https on an Ada host, else an empty string."""
    try:
        u = urllib.parse.urlparse(str(url))
    except ValueError:
        return ""
    host = (u.hostname or "").lower()
    ok = u.scheme == "https" and any(host == h or host.endswith("." + h) for h in LINK_HOSTS)
    return u.geturl() if ok else ""


def rich(text: str) -> str:
    """Escape, then turn *word* into italic: Ada emphasises with italics, not bold."""
    return re.sub(r"\*(.+?)\*", r"<em>\1</em>", e(str(text or ""))).replace("\n", "<br>")


def visible_strings(node):
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for k, v in node.items():
            if k not in ("url", "id", "tip", "kind", "who", "type", "effort", "good"):
                yield from visible_strings(v)
    elif isinstance(node, list):
        for v in node:
            yield from visible_strings(v)


def problems(spec: dict) -> list[str]:
    out = []
    for key in ("title", "customer", "period", "headline"):
        if not spec.get(key):
            out.append(f"needs `{key}`")
    if not 3 <= len(spec.get("metrics") or []) <= 6:
        out.append("metrics: use 3 to 6")
    sections = spec.get("sections") or []
    if not sections:
        out.append("needs at least one section")
    transcripts = [t for s in sections for t in s.get("transcripts") or []]
    if len(transcripts) > MAX_TRANSCRIPTS:
        out.append(f"{len(transcripts)} transcripts; more than {MAX_TRANSCRIPTS} stops being read")
    used = used_tips(spec)
    if len(used) > MAX_TIPS:
        out.append(f"{len(used)} Ada feature notes; keep to {MAX_TIPS} so they stay subtle")
    for t in used:
        if t not in TIPS:
            out.append(f"unknown tip `{t}`; see references/tips.json")
    for s in sections:
        chart = s.get("chart") or {}
        rows = chart.get("rows") or chart.get("points") or []
        if chart and len(rows) < 2:
            out.append(f"section `{s.get('title')}`: a chart needs 2 or more rows")
        for o in s.get("opportunities") or []:
            if not o.get("why"):
                out.append(f"opportunity `{o.get('title')}` has no `why`")
        for t in s.get("transcripts") or []:
            if t.get("url") and not safe_url(t["url"]):
                out.append(f"transcript `{t.get('title')}`: `url` must be https on an Ada host; the link is dropped")
            if not t.get("outcome") or not t.get("why_shown"):
                out.append(f"transcript `{t.get('title')}` needs `outcome` and `why_shown`")
            for turn in t.get("turns") or []:
                if turn.get("who") == "bot" and turn.get("text", "").count("?") > 1:
                    out.append(f"transcript `{t.get('title')}`: a bot turn asks more than one question; check it is quoted exactly")
    text = " ".join(visible_strings({k: v for k, v in spec.items() if k != "sections"})) + " " + " ".join(
        " ".join(visible_strings({k: v for k, v in s.items() if k != "transcripts"})) for s in sections)
    for m in sorted({m.group(0).lower() for m in JARGON.finditer(text)}):
        out.append(f"internal term `{m}` in the text; say what it does in plain words")
    for m in sorted({m.group(0).lower() for m in HARSH.finditer(text)}):
        out.append(f"`{m}` reads as blame; name the gap as an opportunity")
    return out


def used_tips(spec: dict) -> list[str]:
    seen = []
    def add(t):
        if t and t not in seen:
            seen.append(t)
    for s in spec.get("sections") or []:
        add(s.get("tip"))
        for o in s.get("opportunities") or []:
            add(o.get("tip"))
        for tr in s.get("transcripts") or []:
            for turn in tr.get("turns") or []:
                add((turn.get("moment") or {}).get("tip"))
    return seen


def tip_body(tid: str) -> str:
    t = TIPS.get(tid)
    if not t:
        return ""
    return (f"<p>{e(t['what'])}</p><p class='why'><em>Why it matters:</em> {e(t['why'])}</p>"
            f"<p class='try'><em>Try next:</em> {e(t['try'])}</p>")


def metric_card(m: dict) -> str:
    good = m.get("good")
    cls = "ok" if good is True else "warn" if good is False else "mute"
    delta = f"<span class='d {cls}'>{e(m['delta'])}</span>" if m.get("delta") else ""
    note = f"<div class='note'>{rich(m['note'])}</div>" if m.get("note") else ""
    return (f"<div class='metric'><div class='label'>{e(m.get('label', ''))}</div>"
            f"<div class='val'>{e(str(m.get('value', '')))} {delta}</div>{note}</div>")


def bars(chart: dict) -> str:
    rows = chart.get("rows") or []
    top = max((float(r.get("value", 0)) for r in rows), default=1) or 1
    unit = chart.get("unit", "")
    out = []
    for r in rows:
        v = float(r.get("value", 0))
        note = f"<div class='bn'>{rich(r['note'])}</div>" if r.get("note") else ""
        out.append(f"<div class='row'><div class='bl'>{e(r.get('label', ''))}</div>"
                   f"<div class='track'><div class='fill' style='width:{v / top * 100:.1f}%'></div></div>"
                   f"<div class='bv'>{v:g}{e(unit)}</div>{note}</div>")
    return f"<div class='bars' role='img' aria-label='{e(chart.get('title', 'Bar chart'))}'>{''.join(out)}</div>"


def line(chart: dict) -> str:
    pts = chart.get("points") or []
    vals = [float(p.get("value", 0)) for p in pts]
    lo, hi = min(vals), max(vals)
    pad = (hi - lo) * 0.2 or 1
    lo, hi = lo - pad, hi + pad
    w, h, mx, my = 640, 200, 36, 24
    xs = [mx + i * (w - 2 * mx) / max(len(pts) - 1, 1) for i in range(len(pts))]
    ys = [h - my - (v - lo) / (hi - lo) * (h - 2 * my) for v in vals]
    path = " ".join(f"{x:.1f},{y:.1f}" for x, y in zip(xs, ys))
    unit = chart.get("unit", "")
    dots = "".join(
        f"<circle cx='{x:.1f}' cy='{y:.1f}' r='4' class='dot'/>"
        f"<text x='{x:.1f}' y='{y - 10:.1f}' text-anchor='middle' class='tv'>{v:g}{e(unit)}</text>"
        f"<text x='{x:.1f}' y='{h - 4}' text-anchor='middle' class='tl'>{e(p.get('label', ''))}</text>"
        for x, y, v, p in zip(xs, ys, vals, pts))
    return (f"<svg viewBox='0 0 {w} {h}' class='line' role='img' aria-label='{e(chart.get('title', 'Trend'))}'>"
            f"<polyline points='{path}' class='ln'/>{dots}</svg>")


def bubble(turn: dict, counter: list[int]) -> str:
    who = turn.get("who", "bot")
    parts = []
    if turn.get("text"):
        parts.append(e(mask(turn["text"], counter)).replace("\n", "<br>"))
    if turn.get("image"):
        parts.append(f"<div class='img'>Photo: {e(mask(turn['image'], counter))}</div>")
    if turn.get("options"):
        parts.append("<div class='opts'>" + "".join(f"<span>{e(mask(o, counter))}</span>" for o in turn["options"]) + "</div>")
    moment = ""
    m = turn.get("moment")
    if m:
        moment = (f"<details class='moment'><summary>{e(mask(m.get('label', ''), counter))}</summary>"
                  f"<div class='mb'>{tip_body(m.get('tip', ''))}</div></details>")
    return (f"<div class='t {e(who)}'><div class='col'><div class='who'>{'Customer' if who == 'customer' else 'Ada'}</div>"
            f"<div class='bub'>{''.join(parts)}</div>{moment}</div></div>")


def transcript(t: dict, counter: list[int]) -> str:
    turns = "".join(bubble(x, counter) for x in t.get("turns") or [])
    url = safe_url(t.get("url", "")) if t.get("url") else ""
    link = f" · <a href='{e(url)}' rel='noopener noreferrer'>Open in dashboard</a>" if url else ""
    return (f"<article class='card convo'><div class='sh'><h3>{e(mask(t.get('title', ''), counter))}</h3>"
            f"<span class='b'>{e(t.get('outcome', ''))}</span></div>"
            f"<p class='mute'>{rich(mask(t.get('why_shown', ''), counter))} · {e(t.get('channel', 'Web chat'))}{link}</p>"
            f"<div class='chat'>{turns}</div></article>")


def opportunity(o: dict) -> str:
    tip = f"<details class='moment'><summary>How this works in Ada</summary><div class='mb'>{tip_body(o['tip'])}</div></details>" if o.get("tip") else ""
    effort = f"<span class='b'>{e(o['effort'])} effort</span>" if o.get("effort") else ""
    return (f"<div class='card opp'><div class='sh'><h3>{e(o.get('title', ''))}</h3>{effort}</div>"
            f"<p>{rich(o.get('why', ''))}</p>{tip}</div>")


def section(s: dict, counter: list[int]) -> str:
    sid = e(re.sub(r"[^a-z0-9]+", "-", s.get("title", "").lower()).strip("-"))
    body = []
    if s.get("intro"):
        body.append(f"<p class='intro'>{rich(s['intro'])}</p>")
    chart = s.get("chart")
    if chart:
        body.append(f"<div class='card'>{line(chart) if chart.get('type') == 'line' else bars(chart)}</div>")
    if s.get("bullets"):
        body.append("<ul class='nl'>" + "".join(f"<li>{rich(b)}</li>" for b in s["bullets"]) + "</ul>")
    body += [transcript(t, counter) for t in s.get("transcripts") or []]
    if s.get("opportunities"):
        body.append("<div class='grid'>" + "".join(opportunity(o) for o in s["opportunities"]) + "</div>")
    if s.get("tip"):
        body.append(f"<details class='moment'><summary>How this works in Ada</summary><div class='mb'>{tip_body(s['tip'])}</div></details>")
    return f"<section id='{sid}'><h2>{e(s.get('title', ''))}</h2>{''.join(body)}</section>"


def how_ada_works(spec: dict) -> str:
    used = [t for t in used_tips(spec) if t in TIPS]
    if not used:
        return ""
    items = "".join(f"<div class='card'><h3>{e(TIPS[t]['name'])}</h3>{tip_body(t)}</div>" for t in used)
    return f"<section id='how-ada-works'><h2>How Ada worked in these conversations</h2><div class='grid'>{items}</div></section>"


CSS = """
:root{--bg:#F9F9F9;--card:#fff;--ink:#0A0B0C;--mute:#737373;--line:#E6E6E6;--chip:#EFEFEF;
  --ok:#00543D;--okb:#E4EFEA;--warn:#8A5200;--warnb:#FCF0CC;--now:#146681;--nowb:#E1EEF3;
  --font:"Roobert","Inter",-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.6 var(--font);-webkit-font-smoothing:antialiased}
a{color:var(--now);text-underline-offset:2px} em{font-style:italic} .mute{color:var(--mute)}
:focus-visible{outline:2px solid var(--now);outline-offset:2px;border-radius:4px}
.in{max-width:1000px;margin:0 auto;padding:0 20px}
header{padding:40px 0 8px}
.eyebrow{display:flex;align-items:center;gap:10px;color:var(--mute);font-size:13px;margin-bottom:18px}
.eyebrow svg{width:20px;height:20px;color:var(--ink)}
h1{margin:0;font-size:34px;line-height:1.2;font-weight:400;letter-spacing:-.02em;max-width:820px}
.lead{margin:16px 0 0;max-width:760px;font-size:18px;line-height:1.55;color:var(--ink)}
nav.toc{display:flex;gap:18px;flex-wrap:wrap;margin:28px 0 0;padding:12px 0;border-top:1px solid var(--line);border-bottom:1px solid var(--line);font-size:13px}
nav.toc a{color:var(--mute);text-decoration:none} nav.toc a:hover{color:var(--ink)}
h2{font-size:22px;font-weight:400;letter-spacing:-.01em;margin:48px 0 14px}
h3{font-size:16px;font-weight:500;margin:0}
.intro{max-width:760px;margin:0 0 14px}
.metrics{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin:32px 0 0}
.metric,.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px 18px}
.card{margin:12px 0}
.label{font-size:12px;color:var(--mute);margin-bottom:4px}
.val{font-size:30px;line-height:1.2;letter-spacing:-.02em}
.d{font-size:13px;margin-left:6px;letter-spacing:0} .d.ok{color:var(--ok)} .d.warn{color:var(--warn)} .d.mute{color:var(--mute)}
.note{font-size:13px;color:var(--mute);margin-top:6px}
.b{display:inline-flex;align-items:center;padding:2px 10px;border-radius:999px;font-size:12px;background:var(--nowb);color:var(--now);white-space:nowrap}
.sh{display:flex;gap:10px;align-items:center;justify-content:space-between;flex-wrap:wrap}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:12px}
.grid .card{margin:0}
.bars .row{display:grid;grid-template-columns:minmax(120px,200px) 1fr 56px;gap:4px 12px;align-items:center;margin:10px 0}
.track{background:var(--chip);border-radius:999px;height:10px} .fill{background:var(--now);height:10px;border-radius:999px}
.bv{text-align:right;font-size:14px} .bn{grid-column:2 / 4;font-size:13px;color:var(--mute)}
.line{width:100%;height:auto} .ln{fill:none;stroke:var(--now);stroke-width:2.5} .dot{fill:var(--now)}
.tv{font-size:12px;fill:var(--ink)} .tl{font-size:12px;fill:var(--mute)}
.chat{display:flex;flex-direction:column;gap:10px;margin:16px 0 4px;max-width:640px}
.t{display:flex} .t.customer{justify-content:flex-end}
.col{max-width:80%;display:flex;flex-direction:column;gap:4px} .customer .col{align-items:flex-end}
.who{font-size:12px;color:var(--mute)}
.bub{padding:9px 13px;border-radius:14px;background:var(--chip)} .customer .bub{background:var(--ink);color:var(--bg)}
.opts{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px} .opts span{border:1px solid var(--line);border-radius:999px;padding:2px 12px;font-size:13px;background:var(--card);color:var(--ink)}
.img{font-style:italic;font-size:13px}
details.moment{font-size:13px;color:var(--mute);margin-top:2px}
details.moment summary{cursor:pointer;list-style:none;display:inline-flex;align-items:center;gap:6px;padding:1px 0}
details.moment summary::-webkit-details-marker{display:none}
details.moment summary::before{content:"";width:6px;height:6px;border-radius:50%;background:var(--now);flex:none}
details.moment summary:hover{color:var(--ink)}
details.moment[open]{background:var(--nowb);color:var(--ink);border-radius:10px;padding:6px 12px 8px}
.mb p{margin:6px 0 0} .mb p:first-child{margin-top:4px}
ul.nl{margin:0 0 12px;padding-left:20px} ul.nl li{margin:6px 0}
.warnbox{background:var(--warnb);color:var(--warn);border-radius:12px;padding:12px 16px;margin:20px 0}
footer{margin:56px 0 40px;padding-top:16px;border-top:1px solid var(--line);color:var(--mute);font-size:13px}
@media (max-width:640px){h1{font-size:26px} .lead{font-size:16px} .col{max-width:92%} .bars .row{grid-template-columns:1fr 56px} .track{grid-column:1 / 3;order:3} .bn{grid-column:1 / 3}}
@media print{body{background:#fff} nav.toc{display:none} details.moment{display:none} section,.card{break-inside:avoid}}
"""

LOGO = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 439.11 447.37" fill="currentColor" role="img" aria-label="Ada"><path d="M219.53-.08h0C73.31-.08-.05,130.39,0,216.37v231.02s99.19,0,99.19,0c0-121.48,240.87-121.2,240.87,0,0,0,99.05,0,99.05,0v-230.84C439.11,130.39,365.76-.08,219.53-.08ZM219.6,316.69c-58.42.04-105.79-47.33-105.75-105.75.04-57.44,48.15-105.56,105.6-105.6,58.42-.04,105.79,47.33,105.75,105.75-.04,57.44-48.15,105.56-105.6,105.6Z"/></svg>'


def render(spec: dict, warnings: list[str], counter: list[int]) -> str:
    sections = [section(s, counter) for s in spec.get("sections") or []]
    toc = "".join(f"<a href='#{re.sub(r'[^a-z0-9]+', '-', s.get('title', '').lower()).strip('-')}'>{e(s.get('title', ''))}</a>"
                  for s in spec.get("sections") or [])
    warn = ("<div class='warnbox'><em>Fix before sharing:</em><ul class='nl'>" + "".join(f"<li>{e(mask(w, counter))}</li>" for w in warnings) + "</ul></div>") if warnings else ""
    steps = ""
    if spec.get("next_steps"):
        steps = "<section id='next-steps'><h2>Next steps</h2><ul class='nl'>" + "".join(f"<li>{rich(s)}</li>" for s in spec["next_steps"]) + "</ul></section>"
    foot = e(spec.get("footer") or f"Prepared for {spec.get('customer', '')} · {spec.get('period', '')}")
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(spec.get('title', 'Ada report'))}</title><style>{CSS}</style></head><body>
<header><div class="in"><div class="eyebrow">{LOGO}<span>{e(spec.get('customer', ''))} · {e(spec.get('period', ''))}</span></div>
<h1>{e(spec.get('headline', ''))}</h1><p class="lead">{rich(spec.get('lead', ''))}</p>
<nav class="toc">{toc}</nav></div></header>
<main class="in">{warn}<div class="metrics">{''.join(metric_card(m) for m in spec.get('metrics') or [])}</div>
{''.join(sections)}{how_ada_works(spec)}{steps}
<footer>{foot}</footer></main></body></html>"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("-o", "--out")
    ap.add_argument("--open", action="store_true")
    a = ap.parse_args()
    try:
        spec = json.loads(pathlib.Path(a.spec).read_text())
    except (OSError, json.JSONDecodeError) as err:
        print(f"error: cannot read spec: {err}", file=sys.stderr)
        return 1
    warnings = problems(spec)
    counter = [0]
    page = render(spec, warnings, counter)
    slug = re.sub(r"[^a-z0-9]+", "-", (spec.get("title") or "report").lower()).strip("-")
    out = pathlib.Path(a.out) if a.out else pathlib.Path("ada-reports") / f"{slug}.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page)
    if counter[0]:
        print(f"masked {counter[0]} email, phone or number value(s) in transcripts", file=sys.stderr)
    for w in warnings:
        print(f"warning: {w}", file=sys.stderr)
    print(out.resolve())
    if a.open:
        webbrowser.open(out.resolve().as_uri())
    print("done", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
