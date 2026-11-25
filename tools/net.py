#!/usr/bin/env python3
"""The wide net: everything published in a window, as one list. Standard library only, no login, no model.

  python3 tools/net.py 2026-11-25T00:00Z 2026-11-25T17:00Z research/<edition>

Writes candidates.json (one row per story: where, when, title, the source's own first words, counts where counted) and
net-errors.json (every feed that failed or returned nothing in the window, by name). A count is null when not measured.
"""
import concurrent.futures as cf, datetime as dt, html, json, re, sys, time, urllib.parse, urllib.request, email.utils
import xml.etree.ElementTree as ET
from pathlib import Path
UTC = dt.timezone.utc; P = lambda s: dt.datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(UTC)
A, B, OUT = P(sys.argv[1]), P(sys.argv[2]), Path(sys.argv[3]); OUT.mkdir(parents=True, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) news-reader/1.0"}
g = lambda q: "https://news.google.com/rss/search?hl=en-US&gl=US&ceid=US:en&q=" + urllib.parse.quote(q + " when:1d")
FEEDS = {   # name: (url, kind). kind is where it came from, never what it is worth
 "OpenAI": ("https://openai.com/news/rss.xml", "lab"), "Google DeepMind": ("https://deepmind.google/blog/rss.xml", "lab"), "Google AI": ("https://blog.google/technology/ai/rss/", "lab"),
 "Google Research": ("https://research.google/blog/rss/", "lab"), "Microsoft Research": ("https://www.microsoft.com/en-us/research/feed/", "lab"), "NVIDIA": ("https://blogs.nvidia.com/feed/", "lab"),
 "NVIDIA developer": ("https://developer.nvidia.com/blog/feed/", "lab"), "Hugging Face": ("https://huggingface.co/blog/feed.xml", "lab"), "AWS ML": ("https://aws.amazon.com/blogs/machine-learning/feed/", "lab"),
 "Apple ML": ("https://machinelearning.apple.com/rss.xml", "lab"), "BAIR": ("https://bair.berkeley.edu/blog/feed.xml", "lab"), "GitHub": ("https://github.blog/feed/", "lab"), "Cloudflare": ("https://blog.cloudflare.com/rss/", "lab"),
 "TechCrunch AI": ("https://techcrunch.com/category/artificial-intelligence/feed/", "press"), "The Verge": ("https://www.theverge.com/rss/index.xml", "press"), "Ars Technica": ("https://feeds.arstechnica.com/arstechnica/index", "press"),
 "Wired AI": ("https://www.wired.com/feed/tag/ai/latest/rss", "press"), "MIT Tech Review": ("https://www.technologyreview.com/feed/", "press"), "The Register": ("https://www.theregister.com/headlines.atom", "press"), "404 Media": ("https://www.404media.co/rss/", "press"),
 "IEEE Spectrum": ("https://spectrum.ieee.org/feeds/feed.rss", "press"), "Nature": ("https://www.nature.com/nature.rss", "press"), "Quanta": ("https://www.quantamagazine.org/feed/", "press"), "The Guardian": ("https://www.theguardian.com/technology/artificialintelligenceai/rss", "press"),
 "BBC": ("https://feeds.bbci.co.uk/news/technology/rss.xml", "press"), "CNBC": ("https://www.cnbc.com/id/19854910/device/rss/rss.html", "press"), "NYT": ("https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml", "press"), "SemiAnalysis": ("https://newsletter.semianalysis.com/feed", "press"),
 "South China Morning Post": ("https://www.scmp.com/rss/36/feed", "press"), "Bleeping Computer": ("https://www.bleepingcomputer.com/feed/", "press"), "Import AI": ("https://importai.substack.com/feed", "press"), "Simon Willison": ("https://simonwillison.net/atom/everything/", "press"),
 "Interconnects": ("https://www.interconnects.ai/feed", "press"), "Zvi": ("https://thezvi.substack.com/feed", "press"), "ChinaTalk": ("https://www.chinatalk.media/feed", "press"), "The Decoder": ("https://the-decoder.com/feed/", "press"),
 "search: AI": (g("artificial intelligence"), "search"), "search: labs": (g("OpenAI OR Anthropic OR DeepMind OR xAI OR Mistral"), "search"), "search: chips": (g("AI chip OR Nvidia OR TSMC OR HBM"), "search"), "search: research": (g("AI breakthrough OR researchers AI model study"), "search"),
 "search: law": (g("AI lawsuit OR AI regulation OR AI executive order"), "search"), "search: China": (g("DeepSeek OR Qwen OR Moonshot OR Zhipu"), "search"), "search: deploy": (g("deploys AI agents OR rolls out AI"), "search"), "search: robots": (g("humanoid robot OR robotaxi AI"), "search"),
 "search: people": (g("AI CEO resigns OR AI researcher leaves OR AI feud"), "search"), "search: money": (g("AI startup raises OR AI acquisition OR AI IPO"), "search"), "search: science": (g("AI drug OR AI mathematics OR AI materials discovery"), "search"), "search: local": (g("local AI model OR open weights OR llama.cpp OR Ollama OR on-device AI"), "search"),
 "llama.cpp releases": ("https://github.com/ggml-org/llama.cpp/releases.atom", "lab"),
 "Ollama releases": ("https://github.com/ollama/ollama/releases.atom", "lab"),
 "vLLM releases": ("https://github.com/vllm-project/vllm/releases.atom", "lab"),
 "MLX releases": ("https://github.com/ml-explore/mlx/releases.atom", "lab"),
 "search: energy": (g("AI data center power OR nuclear AI"), "search"),
}
ERR, ROWS = {}, []
def get(u): return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30).read()
strip = lambda s: re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", html.unescape(s or "")))).strip()
def when(s):
    s = (s or "").strip()
    if not s: return None
    try: d = email.utils.parsedate_to_datetime(s)
    except Exception:
        try: d = dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
        except Exception: return None
    return (d if d.tzinfo else d.replace(tzinfo=UTC)).astimezone(UTC)
def feed(name, url, kind):
    t = ET.fromstring(get(url).lstrip()); n = lambda e: e.tag.split("}")[-1]; out = []; seen = 0
    for e in t.iter():
        if n(e) not in ("item", "entry"): continue
        seen += 1; d = {}
        for c in e:
            k = n(c); v = c.get("href") if k == "link" and c.get("href") else "".join(c.itertext()); d.setdefault(k, v)
        at = when(d.get("pubDate") or d.get("published") or d.get("date") or d.get("updated"))
        if at is None or not A <= at < B: continue
        src, title = name, strip(d.get("title"))
        if kind == "search" and d.get("source"): src = strip(d["source"]); title = re.sub(r" - " + re.escape(src) + r"$", "", title)
        txt = "" if kind == "search" else strip(d.get("description") or d.get("summary") or d.get("content"))[:420]
        out.append({"title": title, "said": txt, "url": (d.get("link") or "").strip(), "source": src, "kind": kind, "at": at.isoformat(timespec="minutes"), "points": None, "comments": None})
    if not seen: ERR[name] = "the feed holds no entries"
    elif not out: ERR[name] = f"{seen} entries, none in the window"
    return out
def papers():
    out = []
    for day in {A.date(), B.date()}:
        try:
            for x in json.loads(get(f"https://huggingface.co/api/daily_papers?date={day}&limit=100")):
                p = x["paper"]; out.append({"title": strip(p["title"]), "said": strip(p.get("summary"))[:700], "url": "https://arxiv.org/abs/" + p["id"], "source": "Hugging Face daily papers", "kind": "paper", "at": x.get("publishedAt") or str(day), "points": p.get("upvotes"), "comments": x.get("numComments")})
        except Exception as e: ERR[f"HF papers {day}"] = repr(e)[:150]
    return out
def arxiv():   # the announcement feeds carry one day's listing; the listing day is what "published" means here
    out, ids = [], set()
    for c in ("cs.AI", "cs.LG", "cs.CL", "cs.RO", "cs.CR", "cs.CV", "cs.DC", "quant-ph", "q-bio.BM"):
        try:
            t = ET.fromstring(get(f"https://rss.arxiv.org/rss/{c}"))
            for e in t.iter("item"):
                kind = next((x.text for x in e if x.tag.endswith("announce_type")), "new"); link = e.findtext("link")
                if kind not in ("new", "cross") or link in ids: continue
                ids.add(link); out.append({"title": strip(e.findtext("title")), "said": strip(e.findtext("description")).split("Abstract:")[-1].strip()[:700], "url": link, "source": f"arXiv {c}", "kind": "paper", "at": e.findtext("pubDate"), "points": None, "comments": None})
        except Exception as e: ERR["arXiv " + c] = repr(e)[:150]
        time.sleep(.5)
    return out
def hn():
    seen = {}
    for q in [""] + "AI,LLM,agent,model,local,llama.cpp,ollama,GGUF,Claude,OpenAI,Gemini,Anthropic,Nvidia,robot,open weights,inference,GPU,security,DeepSeek,Qwen,Mistral".split(","):
        try:
            n = f"numericFilters=created_at_i>{int(A.timestamp())},created_at_i<{int(B.timestamp())},points>4"
            for h in json.loads(get(f"https://hn.algolia.com/api/v1/search?query={urllib.parse.quote(q)}&tags=story&hitsPerPage=200&{n}"))["hits"]:
                seen[h["objectID"]] = {"title": h["title"], "said": "", "url": h.get("url") or "https://news.ycombinator.com/item?id=" + h["objectID"], "source": "Hacker News", "kind": "hn", "at": h["created_at"], "points": h["points"], "comments": h["num_comments"], "hn": h["objectID"]}
        except Exception as e: ERR["HN " + q] = repr(e)[:150]
        time.sleep(.15)
    return list(seen.values())
def models():
    out = []
    try:
        for x in json.loads(get("https://huggingface.co/api/models?sort=trendingScore&limit=40")):
            at = when(x.get("createdAt"))
            if at and A <= at < B: out.append({"title": "New model on Hugging Face: " + x["id"], "said": " ".join(x.get("tags", []))[:200], "url": "https://huggingface.co/" + x["id"], "source": "Hugging Face", "kind": "model", "at": x["createdAt"], "points": x.get("likes"), "comments": None})
    except Exception as e: ERR["HF models"] = repr(e)[:150]
    return out
def run(name, f):
    try: return f()
    except Exception as e: ERR[name] = repr(e)[:150]; return []
with cf.ThreadPoolExecutor(12) as ex:
    J = [ex.submit(run, n, (lambda n=n, u=u, k=k: feed(n, u, k))) for n, (u, k) in FEEDS.items()] + [ex.submit(run, f.__name__, f) for f in (papers, arxiv, hn, models)]
    for j in J: ROWS += j.result()
key = lambda t: " ".join(sorted(set(re.findall(r"[a-z0-9]{3,}", t.lower())))); D = {}
for r in ROWS:
    k = key(r["title"])
    if k in D: D[k]["also"] = sorted(set(D[k].get("also", []) + [r["source"]])); D[k]["points"] = r["points"] if D[k]["points"] is None else D[k]["points"]; D[k]["said"] = D[k]["said"] or r["said"]
    else: D[k] = r
out = [{"id": f"c{i:04d}", **r} for i, r in enumerate(D.values())]
(OUT / "candidates.json").write_text(json.dumps({"window": [A.isoformat(), B.isoformat()], "read_at": dt.datetime.now(UTC).isoformat(timespec="seconds"), "items": out}, indent=1, ensure_ascii=False))
(OUT / "net-errors.json").write_text(json.dumps(ERR, indent=1))
from collections import Counter
print(len(out), "candidates", dict(Counter(r["kind"] for r in out))); print("missed:", {k: v for k, v in ERR.items() if "none in the window" not in v})
