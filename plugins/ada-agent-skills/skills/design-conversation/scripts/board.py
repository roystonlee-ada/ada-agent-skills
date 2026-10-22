#!/usr/bin/env python3
"""Draw an ADA-DESIGN block as a local design board, outside Ada Architect.

    python3 board.py <instance> <file>   file holds the ADA-DESIGN block, or its JSON
    python3 board.py <instance> -        read it from stdin

Writes ~/.ada-architect/<instance>/boards/<work>.html (always the latest round)
and <work>-r<round>.html (kept for reference). Opens the board once, then reloads
the same browser tab on later rounds (Chrome or Safari on a Mac). Every turn, scenario and
the board have a comment field, and the top bar's Copy button copies all comments
for pasting into chat. Comments survive a reload and are kept per round.
stderr ends in `done` or an `error:` line.
"""
from __future__ import annotations

import html
import json
import pathlib
import re
import subprocess
import sys
import webbrowser

BLOCK_RE = re.compile(r"<<<ADA-DESIGN>>>\s*(\{.*?\})\s*<<<END-ADA-DESIGN>>>", re.S)
HOME = pathlib.Path.home() / ".ada-architect"
SOCIAL = ("messenger", "whatsapp", "instagram")
e = html.escape


def load(text: str) -> dict:
    m = BLOCK_RE.search(text)
    return json.loads(m.group(1) if m else text)


def problems(design: dict) -> list[str]:
    """The same limits Architect's board applies, so a board that draws here draws there."""
    out = []
    scenarios = design.get("scenarios") or []
    if not design.get("work") or not design.get("title"):
        out.append("needs `work` and `title`")
    if not 3 <= len(scenarios) <= 6:
        out.append(f"{len(scenarios)} scenarios; the board expects 3 to 6")
    for s in scenarios:
        for t in s.get("turns") or []:
            if t.get("who") == "bot" and t.get("text", "").count("?") > 1:
                out.append(f"scenario {s.get('id')}: a bot turn asks more than one question")
    return out


def bubble(turn: dict, social: bool, index: int) -> str:
    who = turn.get("who")
    parts = []
    if turn.get("text"):
        parts.append(e(turn["text"]).replace("\n", "<br>"))
    if turn.get("image"):
        parts.append(f"<div class='img'>Photo: {e(turn['image'])}</div>")
    options = turn.get("options") or []
    if options and social:
        parts.append("<br>".join(f"{i}. {e(o)}" for i, o in enumerate(options, 1)))
    elif options:
        parts.append("<div class='opts'>" + "".join(f"<span>{e(o)}</span>" for o in options) + "</div>")
    return (f"<div class='t {e(who or '')}' data-turn='{index}'><div class='col'><div class='who'>{'Customer' if who == 'customer' else 'Agent'}</div><div class='bub'>{''.join(parts)}</div>"
            f"<input class='tc' data-k='turn-{index}' placeholder='Comment on this turn'></div></div>")


CSS = """
:root{--bg:#F9F9F9;--card:#fff;--ink:#0A0B0C;--mute:#737373;--line:#E6E6E6;--hover:#FAFAFA;
  --ok:#00543D;--okb:#E4EFEA;--warn:#8A5200;--warnb:#FCF0CC;--now:#146681;--nowb:#E1EEF3;--chip:#EFEFEF;
  --font:"Roobert","Inter",-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.55 var(--font);-webkit-font-smoothing:antialiased}
a{color:var(--now);text-underline-offset:2px} b{font-weight:500} small,.mute{color:var(--mute)}
:focus-visible{outline:2px solid var(--now);outline-offset:2px;border-radius:4px}
header{padding:28px 0 0} .in{max-width:1152px;margin:0 auto;padding:0 16px}
.eyebrow{display:flex;align-items:center;gap:8px;color:var(--mute);font-size:13px;margin-bottom:10px}
.eyebrow svg{width:18px;height:18px;color:var(--ink)}
h1{margin:0;font-size:30px;line-height:1.2;font-weight:400;letter-spacing:-.02em}
.sub{margin:6px 0 20px;color:var(--mute);font-size:14px}
.bar{position:sticky;top:0;z-index:10;background:var(--bg);border-bottom:1px solid var(--line)}
.bar .in{display:flex;align-items:center;gap:12px}
.tabs{display:flex;gap:4px;overflow-x:auto;flex:1;scrollbar-width:none} .tabs::-webkit-scrollbar{display:none}
.tabs button{background:none;border:0;border-bottom:2px solid transparent;margin-bottom:-1px;color:var(--mute);font:inherit;font-weight:500;padding:10px 14px;cursor:pointer;white-space:nowrap}
.tabs button:hover{color:var(--ink)} .tabs button.on{color:var(--ink);border-bottom-color:var(--ink)}
.cnt{font-size:12px;color:var(--mute);white-space:nowrap}
#copy{font:inherit;font-size:13px;font-weight:500;color:var(--bg);background:var(--ink);border:1px solid var(--ink);border-radius:999px;padding:6px 16px;cursor:pointer;white-space:nowrap}
#copy:hover{opacity:.88} #copy.ok{color:var(--ok);background:var(--okb);border-color:transparent}
.pane{display:none} .pane.on{display:block} .wrap{max-width:1152px;margin:0 auto;padding:8px 16px 48px}
h2{font-size:18px;font-weight:500;letter-spacing:-.01em;margin:28px 0 12px}
.lead{margin:24px 0 0;max-width:820px;font-size:19px;line-height:1.5;letter-spacing:-.005em}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px 18px;margin:12px 0}
.label{font-size:12px;color:var(--mute);margin-bottom:4px}
.b{display:inline-flex;align-items:center;gap:6px;padding:2px 10px;border-radius:999px;font-size:12px;font-weight:500;white-space:nowrap;line-height:1.6}
.b::before{content:"";width:6px;height:6px;border-radius:50%;background:currentColor;flex:none}
.b.ok{background:var(--okb);color:var(--ok)} .b.now{background:var(--nowb);color:var(--now)} .b.warn{background:var(--warnb);color:var(--warn)} .b.mute{background:var(--chip);color:var(--mute)}
.sh{display:flex;gap:10px;align-items:center;flex-wrap:wrap} .sh h2{margin:0}
.chat{display:flex;flex-direction:column;gap:10px;margin:16px 0;max-width:640px}
.t{display:flex} .t.customer{justify-content:flex-end}
.col{max-width:78%;display:flex;flex-direction:column;gap:4px} .customer .col{align-items:flex-end}
.who{font-size:12px;color:var(--mute)}
.bub{padding:9px 13px;border-radius:14px;background:var(--chip)} .customer .bub{background:var(--ink);color:var(--bg)}
.opts{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px} .opts span{border:1px solid var(--line);border-radius:999px;padding:2px 12px;font-size:13px;background:var(--card);color:var(--ink)}
.img{font-style:italic;font-size:13px}
.tc{font:inherit;font-size:13px;border:1px dashed var(--line);border-radius:8px;padding:4px 10px;background:var(--card);width:300px;max-width:100%;color:var(--ink)}
.tc:placeholder-shown{color:var(--mute)} .tc:focus{border-style:solid;border-color:var(--mute);outline:none}
.ex{background:var(--okb);color:var(--ok);border-radius:8px;padding:10px 12px;font-size:13px;margin-top:4px}
.chg{background:var(--warnb);color:var(--warn);border-radius:8px;padding:8px 12px;font-size:13px;margin-top:10px}
.warn{background:var(--warnb);color:var(--warn);border-radius:12px;padding:12px 16px;margin:16px 0}
textarea.sc{width:100%;min-height:64px;margin-top:6px;font:inherit;border:1px solid var(--line);border-radius:8px;padding:10px 12px;background:var(--card);color:var(--ink);resize:vertical}
textarea.sc:focus{border-color:var(--mute);outline:none}
ul.nl{margin:0;padding-left:18px} ul.nl li{margin:4px 0}
@media (max-width:760px){header{padding-top:20px} h1{font-size:24px} .lead{font-size:17px} .col{max-width:92%}}
"""

JS = r"""
const KEY='ada-board:'+WORK+':r'+ROUND;
const fields=[...document.querySelectorAll('[data-k]')];
let saved={};try{saved=JSON.parse(localStorage.getItem(KEY)||'{}')}catch(_){}
const count=()=>fields.filter(f=>f.value.trim()).length;
const show=()=>{document.getElementById('n').textContent=count()+' comment'+(count()==1?'':'s')};
fields.forEach(f=>{const id=(f.closest('[data-sc]')||document.body).dataset.sc+'|'+f.dataset.k;f.dataset.id=id;
  if(saved[id])f.value=saved[id];
  f.addEventListener('input',()=>{saved[id]=f.value;try{localStorage.setItem(KEY,JSON.stringify(saved))}catch(_){};show()})});
show();
const tabs=[...document.querySelectorAll('.tabs button')];
function open(id){tabs.forEach(b=>b.classList.toggle('on',b.dataset.tab===id));
  document.querySelectorAll('.pane').forEach(p=>p.classList.toggle('on',p.id==='tab-'+id));
  try{history.replaceState(null,'','#'+id)}catch(_){}}
tabs.forEach(b=>b.addEventListener('click',()=>open(b.dataset.tab)));
if(location.hash&&document.getElementById('tab-'+location.hash.slice(1)))open(location.hash.slice(1));
function build(){
  const out=['Comments on "'+TITLE+'" (work: '+WORK+', round '+ROUND+')',''];
  const all=document.querySelector('[data-k=overall]').value.trim();
  if(all)out.push('Overall: '+all,'');
  document.querySelectorAll('[data-sc]').forEach(sec=>{
    const lines=[];
    const o=sec.querySelector('textarea.sc').value.trim();
    if(o)lines.push('  Overall: '+o);
    sec.querySelectorAll('[data-turn]').forEach(t=>{
      const c=t.querySelector('.tc').value.trim();
      if(c){const who=t.classList.contains('customer')?'customer':'agent';
        const b=t.querySelector('.bub').cloneNode(true);b.querySelectorAll('.opts').forEach(x=>x.remove());const txt=b.textContent.trim().slice(0,70);
        lines.push('  Turn '+t.dataset.turn+' ('+who+': "'+txt+'"): '+c)}});
    if(lines.length)out.push(sec.dataset.title+':',...lines,'')});
  if(out.length<=2)out.push('No comments.');
  return out.join('\n').trim()+'\n'}
document.getElementById('copy').addEventListener('click',async()=>{
  const text=build();let ok=false;
  try{await navigator.clipboard.writeText(text);ok=true}catch(_){
    const ta=document.createElement('textarea');ta.value=text;document.body.appendChild(ta);ta.select();
    try{ok=document.execCommand('copy')}catch(_){}ta.remove()}
  const b=document.getElementById('copy');b.textContent=ok?'Copied':'Copy failed';b.classList.toggle('ok',ok);
  setTimeout(()=>{b.textContent='Copy comments';b.classList.remove('ok')},1600)});
"""


LOGO = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 439.11 447.37" fill="currentColor" role="img" aria-label="Ada">\n  <path d="M219.53-.08h0C73.31-.08-.05,130.39,0,216.37v231.02s99.19,0,99.19,0c0-121.48,240.87-121.2,240.87,0,0,0,99.05,0,99.05,0v-230.84C439.11,130.39,365.76-.08,219.53-.08ZM219.6,316.69c-58.42.04-105.79-47.33-105.75-105.75.04-57.44,48.15-105.56,105.6-105.6,58.42-.04,105.79,47.33,105.75,105.75-.04,57.44-48.15,105.56-105.6,105.6Z"/>\n</svg>'


def render(design: dict, warnings: list[str]) -> str:
    channels = design.get("channels") or ["Web chat"]
    social = any(c.lower().startswith(SOCIAL) for c in channels[:1])
    notes = "".join(f"<li>{e(n)}</li>" for n in design.get("notes") or [])
    scenarios = design.get("scenarios") or []
    tabs = ["<button class='on' data-tab='overview'>Overview</button>"]
    panes = []
    for s in scenarios:
        sid = str(s.get("id", ""))
        tabs.append(f"<button data-tab='{e(sid)}'>{e(s.get('title', ''))}</button>")
        turns = "".join(bubble(t, social, i) for i, t in enumerate(s.get("turns") or [], 1))
        kind = s.get("kind", "edge")
        badge = {"main": "ok", "edge": "now"}.get(kind, "mute")
        changed = f"<div class='chg'><b>Changed:</b> {e(s['changed'])}</div>" if s.get("changed") else ""
        panes.append(
            f"<section class='pane' id='tab-{e(sid)}' data-sc='{e(sid)}' data-title='{e(s.get('title', ''))}'><div class='wrap'>"
            f"<div class='sh'><h2>{e(s.get('title', ''))}</h2><span class='b {badge}'>{e(kind)}</span></div>{changed}"
            f"<div class='chat'>{turns}</div>"
            f"<div class='ex'><b>Pass looks like:</b> {e(s.get('expect', ''))}</div>"
            f"<div class='card'><div class='label'>Comment on this whole scenario</div>"
            f"<textarea class='sc' data-k='scenario' placeholder='Write a comment'></textarea></div></div></section>")
    warn = ("<div class='warn'><b>Architect would reject or flag this board:</b><ul class='nl'>"
            + "".join(f"<li>{e(w)}</li>" for w in warnings) + "</ul></div>") if warnings else ""
    work, rnd, title = design.get("work", ""), design.get("round", 1), design.get("title", "Design board")
    overview = (
        f"<section class='pane on' id='tab-overview'><div class='wrap'>{warn}"
        f"<p class='lead'>{e(design.get('goal', ''))}</p>"
        + (f"<h2>Notes</h2><div class='card'><ul class='nl'>{notes}</ul></div>" if notes else "")
        + "<h2>Overall comment</h2><div class='card'><div class='label'>Comment on the whole board</div>"
        "<textarea class='sc' data-k='overall' placeholder='Write a comment'></textarea></div>"
        "<p class='mute'>Press Copy comments, paste into chat, or say \"approved\" to build it.</p></div></section>")
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><style>{CSS}</style></head><body>
<header><div class="in"><div class="eyebrow">{LOGO}<span>Design board</span></div><h1>{e(title)}</h1>
<p class="sub">Round {e(str(rnd))} · {e(', '.join(channels))} · {e(work)}</p></div></header>
<div class="bar"><div class="in"><nav class="tabs">{''.join(tabs)}</nav><span class="cnt" id="n">0 comments</span>
<button id="copy" type="button">Copy comments</button></div></div>
{overview}{''.join(panes)}
<script>const WORK={json.dumps(work)},ROUND={json.dumps(rnd)},TITLE={json.dumps(title)};{JS}</script></body></html>"""


def show(path: pathlib.Path) -> None:
    """Reload the board's tab if a browser already has it open, else open it once."""
    url = path.as_uri()
    if sys.platform != "darwin":
        webbrowser.open(url)
        return
    chrome = f'''
tell application "Google Chrome"
  repeat with w in windows
    set i to 0
    repeat with t in tabs of w
      set i to i + 1
      if (URL of t) starts with "{url}" then
        tell t to reload
        set active tab index of w to i
        set index of w to 1
        activate
        return "found"
      end if
    end repeat
  end repeat
end tell
return "none"'''
    safari = f'''
tell application "Safari"
  repeat with w in windows
    repeat with t in tabs of w
      if (URL of t) starts with "{url}" then
        set current tab of w to t
        do JavaScript "location.reload()" in t
        set index of w to 1
        activate
        return "found"
      end if
    end repeat
  end repeat
end tell
return "none"'''
    for app, script in (("Google Chrome", chrome), ("Safari", safari)):
        check = subprocess.run(["osascript", "-e", f'application "{app}" is running'], capture_output=True, text=True)
        if check.stdout.strip() != "true":
            continue
        run = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
        if run.stdout.strip() == "found":
            return
    subprocess.run(["open", str(path)], check=False)


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__, file=sys.stderr)
        return 2
    instance, source = sys.argv[1], sys.argv[2]
    try:
        text = sys.stdin.read() if source == "-" else pathlib.Path(source).read_text()
        design = load(text)
    except (OSError, ValueError) as err:
        print(f"error: could not read a design block: {err}", file=sys.stderr)
        return 1
    warnings = problems(design)
    work = re.sub(r"[^a-z0-9-]+", "-", str(design.get("work", "board")).lower()).strip("-") or "board"
    boards = HOME / instance / "boards"
    boards.mkdir(parents=True, exist_ok=True)
    page = render(design, warnings)
    out = boards / f"{work}-r{design.get('round', 1)}.html"
    out.write_text(page)
    latest = boards / f"{work}.html"
    latest.write_text(page)
    show(latest)
    print(json.dumps({"board": str(latest), "round_copy": str(out), "scenarios": len(design.get("scenarios") or []), "warnings": warnings}))
    print("done", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
