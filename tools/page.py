#!/usr/bin/env python3
"""Fetch a page and keep its readable text: page.py OUTDIR name=url ..."""
import sys, re, html, urllib.request, gzip
out = sys.argv[1]
for a in sys.argv[2:]:
    n, u = a.split("=", 1)
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) news-reader", "Accept-Encoding": "identity"}), timeout=40)
        t = r.read().decode("utf-8", "replace")
        t = re.sub(r"(?is)<(script|style|svg|nav|footer|head)\b.*?</\1>", " ", t)
        t = re.sub(r"(?i)<(p|br|li|h\d|div|tr)\b[^>]*>", "\n", t)
        t = html.unescape(re.sub(r"<[^>]+>", " ", t)); t = re.sub(r"[ \t]+", " ", t); t = re.sub(r"\n\s*\n+", "\n", t).strip()
        open(f"{out}/{n}.txt", "w").write(f"SOURCE {u}\n{t}\n"); print(n, r.status, len(t))
    except Exception as e: print(n, "FAILED", repr(e)[:120])
