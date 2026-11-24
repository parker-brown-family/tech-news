#!/usr/bin/env python3
"""Read X posts by ID, no login: x.py OUT.json handle:id ...  The author comes from the record, never from the caller."""
import sys, json, urllib.request, datetime as dt
out = sys.argv[1]
try: D = json.load(open(out))
except FileNotFoundError: D = {}
for a in sys.argv[2:]:
    h, i = a.split(":")
    try:
        r = json.loads(urllib.request.urlopen(urllib.request.Request(f"https://api.fxtwitter.com/{h}/status/{i}", headers={"User-Agent": "news-trend-reader/1.0"}), timeout=30).read())
        t = r["tweet"]; D[i] = {"author": t["author"]["name"], "handle": t["author"]["screen_name"], "followers": t["author"].get("followers"), "text": t["text"], "at": t["created_at"], "likes": t.get("likes"), "reposts": t.get("retweets"), "views": t.get("views"), "url": t["url"], "quote": (t.get("quote") or {}).get("url"), "quote_text": (t.get("quote") or {}).get("text"), "media": [m["url"] for m in (t.get("media") or {}).get("all", [])], "note": t.get("community_note"), "measured_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
    except Exception as e: D[i] = {"handle": h, "error": repr(e)[:150]}
json.dump(D, open(out, "w"), indent=1, ensure_ascii=False)
