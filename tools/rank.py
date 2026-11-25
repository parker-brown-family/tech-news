#!/usr/bin/env python3
"""Cluster the net, drop what is not AI, and let Jev score what is left for how much it could change the industry.

  python3 tools/rank.py research/2026-11-25-morning [--cap 0.009]

Code does the clustering, the filter, the arithmetic and the cap. Jev answers four typed questions per story. It ranks;
it never picks: an agent reads the primary sources of the top of each lane and chooses. Writes ranked.json.
"""
import concurrent.futures as cf, json, os, re, sys, threading
from pathlib import Path
J = Path.home() / "Work/jev-integrations"; sys.path.insert(0, str(J))
for ln in (J / ".env").read_text().splitlines():
    if ln.startswith("OPENROUTER_API_KEY="): os.environ["OPENROUTER_API_KEY"] = ln.split("=", 1)[1].strip().strip('"')
from jev.client import JevClient
from jev.ports import HostedPort
D = Path(sys.argv[1]); CAP = float(sys.argv[sys.argv.index("--cap") + 1]) if "--cap" in sys.argv else .009
I = json.loads((D / "candidates.json").read_text())["items"]
AI = re.compile(r"\b(A\.?I\.?|artificial intelligence|machine learning|neural|LLMs?|language models?|GPT|ChatGPT|OpenAI|Anthropic|Claude|Gemini|DeepMind|xAI|Grok|Mistral|DeepSeek|Qwen|Kimi|Moonshot|Zhipu|GLM|Llama|Nvidia|GPUs?|TPU|HBM|chatbots?|agentic|agents?|robotaxi|humanoid|robots?|diffusion|transformers?|inference|open.weights?|Hugging Face|Copilot|Cursor|MCP|data cent(?:er|re)s?|superintelligence|AGI)\b", re.I)
DULL = re.compile(r"\b(stocks? to buy|price target|shares (?:rise|fall|jump|slip)|buy rating|best .{0,20}deals?|black friday|horoscope|webinar|opinion:|podcast|how to|top \d+|market size|CAGR|forecast to 20\d\d|quiz|coupon|ETF|analyst(?:s)? says?|should you)\b", re.I)
STOP = set("the a an of to in for on and with is are as at by from its it that this be new says said will how why what after over more has have was amid into not ai".split())
tok = lambda s: frozenset(w for w in re.findall(r"[a-z0-9]{2,}", s.lower()) if w not in STOP)
keep = [r for r in I if AI.search(r["title"] + " " + (r["said"] if r["kind"] != "paper" else "")) or r["kind"] in ("paper", "lab", "model") or (r["points"] or 0) >= 40 or re.search(r"github\.com/(openai|google|google-research|google-deepmind|anthropics|meta|microsoft|deepseek-ai|QwenLM)\b", r["url"] or "")]   # the biggest story of the first morning had no AI word in its title
keep = [r for r in keep if not DULL.search(r["title"])]
CL = []
for r in sorted([r for r in keep if r["kind"] != "paper"], key=lambda r: {"lab": 0, "press": 1, "hn": 2, "model": 3, "search": 4}[r["kind"]]):
    t = tok(r["title"]); best = max(CL, key=lambda c: len(t & c["t"]) / max(1, min(len(t), len(c["t"]))), default=None)
    if best and len(t & best["t"]) >= 3 and len(t & best["t"]) / min(len(t), len(best["t"])) >= .5: best["rows"].append(r)
    else: CL.append({"t": t, "rows": [r]})
def pack(rows): return {"id": rows[0]["id"], "title": rows[0]["title"], "said": next((r["said"] for r in rows if r["said"]), ""), "outlets": sorted({r["source"] for r in rows}), "points": max((r["points"] for r in rows if r["points"] is not None), default=None), "comments": max((r["comments"] for r in rows if r["comments"] is not None), default=None), "kind": rows[0]["kind"], "rows": [{k: r[k] for k in ("title", "url", "source", "at")} for r in rows][:8]}
S = [pack(c["rows"]) for c in CL]
# news worth a question: seen in more than one place, or a lab or a paper of record said it, or people gathered on it
news = [s for s in S if len(s["outlets"]) > 1 or s["kind"] in ("lab", "model") or (s["points"] or 0) >= 15 or (s["kind"] == "press")]
news = sorted(news, key=lambda s: -(len(s["outlets"]) * 3 + min(60, (s["points"] or 0)) / 6 + {"lab": 4, "press": 2}.get(s["kind"], 0)))[:120]
BIG = re.compile(r"\b(first|prove[sd]?|proof|theorem|scal(?:es|ing law)|order[s]? of magnitude|\d+\s?[x×]|without (?:gradient|training|backprop)|continual|self-improv|autonomous(?:ly)? discover|real[- ]world (?:robot|deployment)|clinical|zero-day|exploit|jailbreak|open-source|consumer (?:GPU|hardware)|frontier|novel (?:drug|material|protein)|world model|superhuman|reproduc|fails? to|we (?:find|show) that)\b", re.I)
pap = sorted([r for r in keep if r["kind"] == "paper"], key=lambda r: -((r["points"] or 0) * 1.0 + 3 * len(set(m.lower() for m in BIG.findall(r["title"] + " " + r["said"])))))[:70]
T = news + [pack([r]) for r in pap]
Q = {
 "change": {"type": "score", "instructions": "If what `title` and `said` report is true and lasts, how much would it change what the artificial intelligence industry builds, buys, or is allowed to do?",
   "criteria": ["it would change nothing outside one company, product or narrow benchmark", "it would change how some companies or researchers in one area work", "it would change how most of the artificial intelligence industry works, what it costs, who leads it, or what is lawful"]},
 "lane": {"type": "choice", "instructions": "Which one kind of story is `title` mainly, reading `said` for context?",
   "criteria": {"drama": "people or companies in open conflict: a feud, accusation, lawsuit, firing, leak, scandal or backlash", "research": "a scientific or engineering result: a paper, method, measurement, proof, discovery or new model with reported results", "corporate": "a business or government act: a deal, funding, earnings, hire, policy, law, chip supply or launch plan", "use": "artificial intelligence put to work: a deployment, tool, product or technique people are already using, and how it works", "none": "not about artificial intelligence, or an opinion, advertisement, listicle or stock tip"}},
 "concrete": {"type": "noul", "instructions": "`title` and `said` together name a specific thing that has happened, with a named person or organization or a stated result, rather than a prediction, a trend piece or an opinion."},
}
client = JevClient("https://openrouter.ai/api", port=HostedPort("jev-latest"), api_key_env="OPENROUTER_API_KEY", timeout_s=30)
spent, lock, n = [0.0], threading.Lock(), [0]; unk = [0]
post = client._post
def metered(body, h=None):
    with lock:
        if spent[0] >= CAP: return None, "error:cap", 0.0
    p, why, ms = post(body, h)
    with lock:
        c = ((p or {}).get("usage") or {}).get("cost")
        if c is None: unk[0] += 1; c = .00006        # a call whose price did not come back is charged high, never zero
        spent[0] += c; n[0] += 1
    return p, why, ms
client._post = metered
def one(s):
    r = client.ask_many({"title": s["title"][:200], "said": s["said"][:420] or "(the feed carried only the title)"}, Q)
    s["jev"] = {k: (d.value if d.usable else None) for k, d in r.items()}; s["jev_why"] = sorted({d.reason for d in r.values() if d.reason}); s["lane_p"] = r["lane"].probabilities; return s
with cf.ThreadPoolExecutor(8) as ex: T = list(ex.map(one, T))
got = [s for s in T if all(v is not None for v in s["jev"].values())]
for s in got: s["rank"] = round(s["jev"]["change"] * (.35 + .65 * s["jev"]["concrete"]), 3)
got.sort(key=lambda s: -s["rank"])
(D / "ranked.json").write_text(json.dumps({"net": len(I), "ai": len(keep), "clusters": len(S), "asked": len(T), "answered": len(got), "jev_calls": n[0], "jev_usd": round(spent[0], 5), "jev_calls_without_a_price": unk[0], "stories": got, "unanswered": [{k: s[k] for k in ("title", "jev_why")} for s in T if s not in got]}, indent=1, ensure_ascii=False))
print(f"{len(I)} net, {len(keep)} AI, {len(S)} news clusters, {len(T)} asked, {len(got)} answered, {n[0]} calls, ${spent[0]:.5f} ({unk[0]} unpriced)")
for lane in ("drama", "research", "corporate", "use"):
    print("\n##", lane)
    for s in [s for s in got if s["jev"]["lane"] == lane][:16]: print(f"{s['rank']:.2f} c{s['jev']['change']:.2f} k{s['jev']['concrete']:.2f} hn{s['points']} o{len(s['outlets'])} {s['id']} [{s['kind']}] {s['title'][:125]} | {s['outlets'][0]}")
