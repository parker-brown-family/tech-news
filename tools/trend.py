#!/usr/bin/env python3
"""Measure what is trending. Standard library only; no login.

  python3 tools/trend.py 2026-11-20 2026-11-25 research/2026-11-24

Writes hn.json, lobsters.json, reddit.json, advisories.json, kev.json, hf.json, errors.json.
Counts are true at `measured_at` only. A feed that failed is in errors.json, never an empty list that looks like "nothing there".
"""
import json, sys, time, urllib.parse, urllib.request, datetime as dt, re
from pathlib import Path
A, B, OUT = sys.argv[1], sys.argv[2], Path(sys.argv[3]); OUT.mkdir(parents=True, exist_ok=True)
ts = lambda d: int(dt.datetime.fromisoformat(d + "T00:00:00-08:00").timestamp())
NOW = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"); ERR = {}
UA = {"User-Agent": "news-trend-reader/1.0"}
def get(u, raw=False):
    r = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=40).read()
    return r.decode("utf-8", "replace") if raw else json.loads(r)
def safe(name, f):
    try: v = f()
    except Exception as e: ERR[name] = repr(e)[:300]; return None
    return v
def save(n, v):
    if v is not None: (OUT / n).write_text(json.dumps({"measured_at": NOW, "window": [A, B], "items": v}, indent=1, ensure_ascii=False))
def hn():
    seen = {}
    Q = [""] + "AI,LLM,security,vulnerability,CVE,prompt injection,agent,MCP,ollama,llama.cpp,vLLM,local model,open weights,Hugging Face,backdoor,supply chain,npm,PyPI,malware,jailbreak,exploit,Claude,OpenAI,Gemini,Qwen,DeepSeek,Mistral,Nvidia,breach,zero-day,LM Studio,GGUF,OpenClaw,ransomware,Kimi,GLM,Gemma,Anthropic,Cursor,Copilot".split(",")
    for q in Q:
        for p in range(3 if q == "" else 1):
            def one():
                n = f"numericFilters=created_at_i>{ts(A)},created_at_i<{ts(B)}" + (",points>25" if q == "" else ",points>3")
                return get(f"https://hn.algolia.com/api/v1/search?query={urllib.parse.quote(q)}&tags=story&hitsPerPage=200&page={p}&{n}")
            d = safe(f"hn:{q}:{p}", one)
            for h in (d or {}).get("hits", []):
                seen[h["objectID"]] = {"id": h["objectID"], "title": h["title"], "url": h.get("url"), "points": h["points"], "comments": h["num_comments"], "at": h["created_at"], "hn": "https://news.ycombinator.com/item?id=" + h["objectID"]}
            time.sleep(.15)
    return sorted(seen.values(), key=lambda x: -(x["points"] or 0))
def reddit():
    o = []
    for s in "LocalLLaMA,LocalLLM,ollama,netsec,cybersecurity,MachineLearning,selfhosted,StableDiffusion,artificial,hacking".split(","):
        d = safe("reddit:" + s, lambda: get(f"https://www.reddit.com/r/{s}/top.json?t=week&limit=60"))
        for c in ((d or {}).get("data") or {}).get("children", []):
            x = c["data"]
            if ts(A) <= x["created_utc"] < ts(B): o.append({"sub": s, "title": x["title"], "score": x["score"], "comments": x["num_comments"], "url": x["url"], "permalink": "https://www.reddit.com" + x["permalink"], "at": dt.datetime.fromtimestamp(x["created_utc"], dt.timezone.utc).isoformat()})
        if d is None:
            t = safe("redditrss:" + s, lambda: get(f"https://www.reddit.com/r/{s}/top/.rss?t=week&limit=60", True))
            for e in re.findall(r"<entry>(.*?)</entry>", t or "", re.S):
                m = lambda k: (re.search(k, e, re.S) or [None, None])[1]
                o.append({"sub": s, "title": m(r"<title>(.*?)</title>"), "score": None, "comments": None, "permalink": m(r'<link href="(.*?)"'), "at": m(r"<published>(.*?)<")})
        time.sleep(2)
    return sorted(o, key=lambda x: -(x["score"] or 0)) or None
def lob():
    o = []
    for p in range(1, 8):
        for x in safe(f"lob{p}", lambda: get(f"https://lobste.rs/newest/page/{p}.json")) or []:
            if A <= x["created_at"][:10] < B: o.append({"title": x["title"], "url": x["url"], "score": x["score"], "comments": x["comment_count"], "tags": x["tags"], "at": x["created_at"], "page": x["short_id_url"]})
    return sorted(o, key=lambda x: -x["score"]) or None
def adv():
    import subprocess
    r = subprocess.run(["gh", "api", "--paginate", f"/advisories?type=reviewed&published={A}..{B}&per_page=100"], capture_output=True, text=True, timeout=120)
    if r.returncode: raise RuntimeError(r.stderr)
    t = r.stdout.replace("][", ",")
    return [{"ghsa": a["ghsa_id"], "cve": a["cve_id"], "severity": a["severity"], "cvss": (a.get("cvss") or {}).get("score"), "summary": a["summary"], "packages": sorted({(v.get("package") or {}).get("name") or "?" for v in a["vulnerabilities"]}), "published": a["published_at"], "url": a["html_url"]} for a in json.loads(t)]
def kev():
    d = get("https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json")
    return [v for v in d["vulnerabilities"] if A <= v["dateAdded"] < B]
def hf():
    d = get("https://huggingface.co/api/trending?type=model&limit=30")
    return [x["repoData"] | {"authorData": None} for x in d["recentlyTrending"]]
for n, f in [("hn", hn), ("lobsters", lob), ("reddit", reddit), ("advisories", adv), ("kev", kev), ("hf", hf)]: save(n + ".json", safe(n, f))
(OUT / "errors.json").write_text(json.dumps(ERR, indent=1)); print({p.name: len(json.loads(p.read_text()).get("items", [])) for p in OUT.glob("*.json") if p.name != "errors.json"}, "errors:", ERR)
