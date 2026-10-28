#!/usr/bin/env python3
"""Fetch help center articles to Markdown, download their images, write manifest.json.

Usage: python3 -I extract_help_center.py (--urls urls.txt | --discover INDEX_URL) --out DIR
urls.txt holds one article URL per line. --discover follows same-host links from an
index page (category, folder, article) and collects article URLs. Standard library only.
"""

import argparse
import hashlib
import json
import re
import struct
import sys
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

UA = {"User-Agent": "Mozilla/5.0 (help-center-import)"}
SKIP_TAGS = {"script", "style", "nav", "footer", "header", "aside", "form", "noscript", "svg"}
MIN_IMAGE_PX = 48


def image_size(data):
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return struct.unpack(">II", data[16:24])
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return struct.unpack("<HH", data[6:10])
    if data[:2] == b"\xff\xd8":
        i = 2
        while i + 9 < len(data):
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
                h, w = struct.unpack(">HH", data[i + 5 : i + 9])
                return w, h
            i += 2 + struct.unpack(">H", data[i + 2 : i + 4])[0]
    return None


def discover(index_url, max_pages=200):
    host = urllib.parse.urlsplit(index_url).netloc
    seen, queue, articles = set(), [index_url], []
    while queue and len(seen) < max_pages:
        page = queue.pop(0)
        if page in seen:
            continue
        seen.add(page)
        try:
            html = fetch(page)[0].decode("utf-8", errors="replace")
        except Exception:
            continue
        for href in re.findall(r'href="([^"#]+)"', html):
            link = urllib.parse.urljoin(page, href).split("?")[0]
            parts = urllib.parse.urlsplit(link)
            if parts.netloc != host:
                continue
            if "/articles/" in parts.path:
                if link not in articles:
                    articles.append(link)
            elif "/solutions/" in parts.path and link not in seen:
                queue.append(link)
    return articles


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read(), resp.headers.get("Content-Type", "")


class Extractor(HTMLParser):
    def __init__(self, base):
        super().__init__(convert_charrefs=True)
        self.base = base
        self.skip = 0
        self.lines = []
        self.cur = []
        self.images = []
        self.title = ""
        self.in_title = False
        self.list_stack = []

    def flush(self):
        text = re.sub(r"\s+", " ", "".join(self.cur)).strip()
        if text:
            self.lines.append(text)
        self.cur = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title":
            self.in_title = True
        if tag in SKIP_TAGS:
            self.skip += 1
            return
        if self.skip:
            return
        if tag in {"h1", "h2", "h3", "h4"}:
            self.flush()
            self.cur.append("#" * int(tag[1]) + " ")
        elif tag in {"p", "div", "br", "section", "article", "table", "tr"}:
            self.flush()
        elif tag in {"ol", "ul"}:
            self.flush()
            self.list_stack.append([tag, 0])
        elif tag == "li":
            self.flush()
            if self.list_stack:
                kind = self.list_stack[-1]
                kind[1] += 1
                self.cur.append(f"{kind[1]}. " if kind[0] == "ol" else "- ")
        elif tag == "img":
            src = a.get("src") or a.get("data-src") or ""
            if not src or src.startswith("data:") or "/assets/" in src:
                return
            w = int(a.get("width") or 0) if str(a.get("width") or "").isdigit() else 0
            if 0 < w < MIN_IMAGE_PX:
                return
            idx = len(self.images) + 1
            self.images.append(
                {
                    "n": idx,
                    "src": urllib.parse.urljoin(self.base, src),
                    "alt": (a.get("alt") or "").strip(),
                    "after_line": len(self.lines),
                }
            )
            self.cur.append(f" [IMAGE {idx}] ")

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        if tag in SKIP_TAGS:
            self.skip = max(0, self.skip - 1)
            return
        if self.skip:
            return
        if tag in {"ol", "ul"} and self.list_stack:
            self.list_stack.pop()
        if tag in {"h1", "h2", "h3", "h4", "li", "p", "div", "tr"}:
            self.flush()

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        elif not self.skip:
            self.cur.append(data)


def main_block(html):
    for pat in (r"(?is)<article\b.*?</article>", r"(?is)<main\b.*?</main>"):
        m = re.search(pat, html)
        if m:
            return m.group(0)
    return html


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60] or "article"


def process(url, out):
    body, ctype = fetch(url)
    html = body.decode("utf-8", errors="replace")
    warnings = []
    visible = re.sub(r"(?is)<script.*?</script>", "", html)
    if "__next_f" in html and len(re.sub(r"(?s)<[^>]+>", "", visible).strip()) < 500:
        warnings.append("Next.js RSC page: content sits in script tags. Parse the payload, do not trust this scrape.")
    ex = Extractor(url)
    ex.feed(main_block(html))
    ex.flush()
    h1 = re.search(r"(?is)<h1[^>]*>(.*?)</h1>", html)
    page_title = re.search(r"(?is)<title[^>]*>(.*?)</title>", html)
    raw_title = (h1.group(1) if h1 else page_title.group(1) if page_title else "")
    title = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", raw_title)).strip() or url
    ident = re.search(r"/(\d{6,})", url)
    slug = slugify(title) + (f"-{ident.group(1)}" if ident else "-" + hashlib.sha1(url.encode()).hexdigest()[:8])
    folder = out / slug
    (folder / "images").mkdir(parents=True, exist_ok=True)

    for img in ex.images:
        try:
            data, ct = fetch(img["src"])
        except Exception as exc:
            img["error"] = str(exc)
            continue
        ext = (ct.split(";")[0].split("/")[-1] or "bin").replace("jpeg", "jpg").replace("svg+xml", "svg")
        name = f"{img['n']:02d}-{hashlib.sha1(data).hexdigest()[:8]}.{ext}"
        (folder / "images" / name).write_bytes(data)
        img["file"] = f"images/{name}"
        img["bytes"] = len(data)
        size = image_size(data)
        if size:
            img["width"], img["height"] = size
            img["too_tall_for_chat"] = size[1] > 1.3 * size[0] or size[1] > 900
        img["convert_needed"] = ext not in {"png", "jpg", "gif"}

    (folder / "article.md").write_text("\n\n".join(ex.lines) + "\n", encoding="utf-8")
    words = sum(len(line.split()) for line in ex.lines)
    if words < 80:
        warnings.append(f"Only {words} words extracted. The page may render client-side or be an index page. Open it and check, or use the help center API.")
    modified = re.search(r"Modified on ([^\n]+)", "\n".join(ex.lines[:6]))
    return {
        "url": url,
        "title": title,
        "modified": modified.group(1).strip() if modified else None,
        "folder": slug,
        "words": words,
        "images": ex.images,
        "warnings": warnings,
        "label": None,
        "reason": None,
    }


def main():
    ap = argparse.ArgumentParser()
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--urls")
    src.add_argument("--discover")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    if args.discover:
        urls = discover(args.discover)
        (out / "urls.txt").write_text("\n".join(urls) + "\n")
        print(f"discovered {len(urls)} article URLs", file=sys.stderr)
    else:
        urls = [u.strip() for u in Path(args.urls).read_text().splitlines() if u.strip() and not u.startswith("#")]
    manifest = []
    for url in urls:
        try:
            entry = process(url, out)
        except Exception as exc:
            entry = {"url": url, "error": str(exc)}
        manifest.append(entry)
        flag = " WARN" if entry.get("warnings") else ""
        print(f"{url} -> {entry.get('folder', 'ERROR')} ({len(entry.get('images', []))} images){flag}", file=sys.stderr)
        for w in entry.get("warnings", []):
            print(f"  {w}", file=sys.stderr)
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(f"wrote {out / 'manifest.json'}", file=sys.stderr)


if __name__ == "__main__":
    main()
