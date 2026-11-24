# Tech News

News about local AI, AI security and other tech, with the sources behind every claim. Made by [Parker Brown](https://x.com/parkerbrowndev) at Brown Family Sports.

**Are our facts whack?** [Leave an issue](https://github.com/parker-brown-family/tech-news/issues/new?template=fact-check.md). Corrections are welcome from anyone, and from anyone named in a story most of all.

**Checking something a film said?** Find the story below. Its file lists who made each claim, where they made it, and how far we got in checking it. Each claim carries one of four marks: `read` (we read the document), `counted` (we counted or added it up), `said` (someone says so and we have not confirmed it) and `open`.

**Reading with an agent?** Pull one file, a [JSON Feed](https://jsonfeed.org) with every story, claim and source:

```bash
curl -s https://raw.githubusercontent.com/parker-brown-family/tech-news/main/feed.json
```

Claude, made by Anthropic, helped with this research. Some stories are about Anthropic.

## Who Read Your Prompt?

The first film, dated 24 November 2026. Where a prompt goes after you send it, and who can keep it.

Research: HD Moore and the Dragos research team. Canarytokens: Thinkst. The llama.cpp flaws and fixes: Adam Bedard, zent and ServeurpersoCom. Thank you.

### Its sources

**[Two million baited prompts show where prompts go](stories/prompt-canaries.json)** (2026-11-19). A researcher put unique secrets in about two million AI prompts, then watched who used them. The report says attackers were stealing data from three hosting providers. It names none.

- [Dragos](https://www.dragos.com/blog/ai-supply-chain-security-canary-tokens)
- [Ars Technica](https://arstechnica.com/security/2026/11/a-leaky-ai-supply-chain-is-exposing-secret-user-data-at-an-alarming-rate/)
- [HD Moore on X](https://x.com/hdmoore/status/2123451306685661416)
- [Menlo Ventures, an OpenRouter investor](https://menlovc.com/perspective/openrouter-now-processes-more-than-a-quadrillion-tokens-a-year/)

**[The providers answer, and their accounts differ](stories/providers-answer.json)** (2026-11-24). Five providers have published notices. MiniMax said today that its security system opened the links; two resellers tell users to treat secrets as exposed.

- [OpenRouter](https://openrouter.ai/blog/announcements/data-processing-incidents-on-inference-providers/)
- [MiniMax](https://www.minimax.io/blog/update-on-url-access-in-forwarded-api-requests-20261124)
- [Novita AI](https://novita.ai/blog/minimax-requests-privacy-notice/)
- [Atlas Cloud](https://www.atlascloud.ai/blog/ai-updates/security-and-privacy-commitment)
- [Together AI](https://www.together.ai/blog/security-event-prompt-leakage-for-requests-in-june-and-july-of-2026)
- [Phala](https://phala.com/posts/phala-november-preliminary-incident-report)
- [Mia on X](https://x.com/MiaAI_lab/status/2124054476893851731)

**[Who advises what about leaking prompts](stories/prompt-advice.json)** (2026-11-24). The researcher, the router, two hosts, a government agency, a developer and a privacy writer give different advice.

- [Dragos](https://www.dragos.com/blog/ai-supply-chain-security-canary-tokens)
- [Alex Atallah on X](https://x.com/alexatallah/status/2124318002594054196)
- [Nate Berkopec on X](https://x.com/nateberkopec/status/2123636569198457293)
- [UK National Cyber Security Centre](https://www.ncsc.gov.uk/blog-post/chatgpt-and-large-language-models-whats-the-risk)
- [Atlas Cloud](https://www.atlascloud.ai/blog/ai-updates/security-and-privacy-commitment)
- [Together AI](https://www.together.ai/blog/security-event-prompt-leakage-for-requests-in-june-and-july-of-2026)
- [Micah Lee](https://micahflee.com/heres-how-anyone-can-easily-use-private-open-weight-models/)
- [Phala](https://phala.com/posts/phala-november-preliminary-incident-report)

**[Inkling 2 Mini runs on a laptop](stories/inkling-2-mini.json)** (2026-11-20). Thinking Machines released a 26.4-billion-parameter open-weight model that it says needs about 20 GB. Others have made much smaller builds.

- [Thinking Machines](https://thinkingmachines.ai/news/inkling-2-mini/)
- [Hugging Face](https://huggingface.co/thinkingmachines/Inkling-2-Mini)
- [LookAtMyQuant on GitHub](https://github.com/ShinMegamiBoson/lookatmyquant)
- [Unsloth on Hugging Face](https://huggingface.co/unsloth/Inkling-2-Mini-GGUF)
- [Thinking Machines on X](https://x.com/thinkymachines/status/2123871643797995872)
- [Ahmad on X](https://x.com/TheAhmadOsman/status/2123936559447920931)

**[Opening a bad model file could run code in llama.cpp](stories/model-file-flaws.json)** (2026-11-13). Three flaws in how llama.cpp reads model files were published on November 13. All three were already fixed.

- [Zero Day Initiative](https://www.zerodayinitiative.com/advisories/ZDI-26-975/)
- [CVE record for ZDI-26-976](https://www.cve.org/CVERecord?id=CVE-2026-126975)
- [Zero Day Initiative](https://www.zerodayinitiative.com/advisories/ZDI-26-954/)
- [llama.cpp on GitHub](https://github.com/ggml-org/llama.cpp/pull/31336)
- [llama.cpp on GitHub](https://github.com/ggml-org/llama.cpp/commit/e2e7a9b2d04e0404131e551243d4bd399ccfe606)

## The other stories

### Who Gets to Run Open AI?

Who decides which models a person may download and run?

- **[LeCun says Amodei wants open models made illegal](stories/lecun-amodei.json)** (2026-11-22). Yann LeCun’s post answers a clip of Dario Amodei that is being shared as new. In July, Amodei wrote that Anthropic has never advocated a ban.
- **[A House report wants Chinese open models out of federal systems](stories/house-open-weights.json)** (2026-11-20). Two committees published 12 recommendations. They cover federal systems, federal contracts and high-risk infrastructure, and ask for an American open-weight program.

### The Attackers Have Agents

What are attackers' AI agents doing, and what has been proven?

- **[AI agents found a zero-day and used it](stories/monai-agents.json)** (2026-11-23). Amazon says attackers’ agents found an unknown flaw in MONAI Label, a medical-imaging research server. CISA listed it on Monday, the day after a fixed release.
- **[An npm package installed an AI agent as the backdoor](stories/hermes-npm.json)** (2026-11-19). A fake CRM client installed an open-source agent and took orders over Telegram. It was removed after nine versions in one day.
- **[Microsoft’s agent toolkit was poisoned on PyPI](stories/microsoft-agent-framework.json)** (2026-11-17). Two releases carried a credential stealer for under an hour. Wiz says they went through Microsoft’s own publishing system.
- **[Amazon’s decoys recorded attackers’ agents thinking](stories/artex-madpot.json)** (2026-11-05). Fake AI endpoints received requests from attack agents, which carried the agents’ own records. Stolen AI keys paid for the search for more.

### Your Agent, Your Problem

Who pays when a personal AI agent sees or does too much?

- **[Signal blocks phone AI from reading its screens](stories/signal-blocks-agents.json)** (2026-11-20). Signal prevents screenshots on iOS 27 and blocks assistants it can detect on Android. It says it cannot do the same on macOS.
- **[Banks say an agent’s mistakes are yours](stories/banks-agents.json)** (2026-11-18). Citi, PNC, JPMorgan and Bank of America have changed terms for outside AI agents. A viral post says banks won’t refund you, which is broader than what was reported.
