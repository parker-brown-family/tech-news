#!/usr/bin/env python3
"""Check every story and write feed.json and correlations.json. Standard library only.

  python3 tools/build.py [--check]

The claim and source rules are omarchy-news's own (imported, never copied), so a mark means the same in both.
"""
import importlib.util, json, sys
from pathlib import Path
R, SIB = Path(__file__).resolve().parent.parent, Path.home() / "Work/omarchy-news"
sp = importlib.util.spec_from_file_location("omnews", SIB / "tools/build.py"); om = importlib.util.module_from_spec(sp); sp.loader.exec_module(om)
om.R = R; om.FIELDS = om.FIELDS | {"trend", "omarchy"}
load = lambda n: json.loads((R / n).read_text())

def main():
    S, T, V = om.stories(), load("topics.json"), load("videos.json")
    bad = om.problems(S, T, V)
    theirs = {p.stem for p in (SIB / "stories").glob("*.json")}
    ttop = {t["id"] for t in json.loads((SIB / "topics.json").read_text())}
    for s in S:
        if s["id"] in theirs: bad.append(f"{s['id']}: id is already an Omarchy story")
        for o in s["omarchy"]:
            if o["story"] not in theirs: bad.append(f"{s['id']}: no Omarchy story {o['story']}")
        for k in ("hn", "lobsters", "x"):
            if k not in s["trend"]: bad.append(f"{s['id']}: trend.{k} missing; null means not measured")
    for t in T:
        if t["id"] in ttop: bad.append(f"topic {t['id']} is also an Omarchy topic")
    if bad: print("\n".join(bad)); return 1
    cor = {}
    for s in S:
        for o in s["omarchy"]: cor.setdefault(o["story"], []).append({"story": s["id"], "title": s["title"], "why": o["why"]})
    feed = {"version": "https://jsonfeed.org/version/1.1", "title": "Tech News", "description": "Local AI, AI security and tech news with sources.", "_tech_news": {"topics": T, "videos": V},
            "items": [{"id": s["id"], "title": s["title"], "content_text": s["summary"], "date_published": s["date"] + "T00:00:00Z", "tags": [t["id"] for t in s["topics"]], "_tech_news": s} for s in S]}
    want = {"feed.json": feed, "correlations.json": dict(sorted(cor.items()))}
    want = {n: json.dumps(v, indent=1, ensure_ascii=False) + "\n" for n, v in want.items()}
    stale = [n for n, t in want.items() if not (R / n).exists() or (R / n).read_text() != t]
    if "--check" in sys.argv: print("out of date: " + ", ".join(stale) if stale else f"ok: {len(S)} stories, {sum(len(s['claims']) for s in S)} claims, {sum(len(s['sources']) for s in S)} sources, {len(cor)} Omarchy links"); return bool(stale)
    for n in stale: (R / n).write_text(want[n])
    print(f"{len(S)} stories; wrote {', '.join(stale) or 'nothing'}"); return 0
if __name__ == "__main__": sys.exit(main())
