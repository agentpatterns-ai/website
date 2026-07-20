---
title: "AI Crawler Policy: robots.txt for the Three-Tier Crawler Landscape"
term: "AI Crawler Policy"
description: "Configure robots.txt to allow AI search and retrieval crawlers while blocking training scrapers — user-agent strings, decision matrix, compliance caveats."
aliases:
  - "robots.txt for AI crawlers"
  - "AI bot blocking policy"
tags:
  - geo
  - technique
  - tool-agnostic
  - workflows
last_reviewed: 2026-06-13
maturity: established
---

# AI Crawler Policy: robots.txt for the Three-Tier Crawler Landscape

> AI crawlers split into retrieval bots (allow for citations), training scrapers (disallow), and non-compliant bots (WAF block) — each requiring a distinct robots.txt strategy.

Related lesson: [Four Engines, Four Backends](https://learn.agentpatterns.ai/geo/four-engines-four-backends/) — this concept features in a hands-on lesson with quizzes.

## The three-tier taxonomy

AI crawlers are not monolithic. Each major provider now operates separate bots for distinct purposes, each with its own user-agent string:

| Tier | Purpose | User-agents | robots.txt behaviour |
|------|---------|-------------|----------------------|
| Tier 1 — User-facing retrieval | Powers real-time citations in AI chat and search | `ChatGPT-User`*, `OAI-SearchBot`, `Claude-User`, `Claude-SearchBot`, `PerplexityBot`†, `Perplexity-User`† | Allow — drives referral traffic and AI citations |
| Tier 2 — Training scrapers | Ingests content for model training datasets | `GPTBot`, `ClaudeBot`, `Google-Extended`, `Meta-ExternalAgent` | Disallow — no citation benefit; opts out of training data |
| Tier 3 — Non-compliant bots | Crawlers documented to ignore robots.txt | `Bytespider` (ByteDance) | CDN/WAF block — robots.txt is ineffective |

The tier distinction matters. You can block training crawlers without blocking retrieval bots. That keeps your content eligible for AI search citations while opting out of training datasets.

\* As of OpenAI's December 2025 policy update, `ChatGPT-User` no longer respects robots.txt; disallow rules are ignored ([coverage](https://ppc.land/openai-revises-chatgpt-crawler-documentation-with-significant-policy-changes/)).

† Cloudflare documented Perplexity rotating user-agents and ASNs to bypass robots.txt ([August 2025 report](https://blog.cloudflare.com/perplexity-is-using-stealth-undeclared-crawlers-to-evade-website-no-crawl-directives/)). Use WAF for hard blocks.

## Decision matrix

| Goal | Action |
|------|--------|
| Appear in AI search answers (ChatGPT, Claude, Perplexity) | Allow Tier 1 |
| Prevent content entering training datasets | Disallow Tier 2 |
| Stop ByteDance/Bytespider from crawling | WAF custom rule |
| Opt out of everything | Disallow all AI user-agents + WAF |

The emerging practitioner consensus for documentation sites: allow Tier 1, disallow Tier 2.

## Reference configuration

This site's `robots.txt` implements the three-tier policy:

```text
# ── Default: allow all standard crawlers ──────────────────────────────────────
User-agent: *
Allow: /

# ── Tier 1: User-facing retrieval bots (ALLOW) ────────────────────────────────

User-agent: ChatGPT-User
Allow: /

User-agent: OAI-SearchBot
Allow: /

User-agent: Claude-User
Allow: /

User-agent: Claude-SearchBot
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Perplexity-User
Allow: /

# ── Tier 2: Training scrapers (DISALLOW) ──────────────────────────────────────

User-agent: GPTBot
Disallow: /

User-agent: ClaudeBot
Disallow: /

User-agent: Google-Extended
Disallow: /

User-agent: Meta-ExternalAgent
Disallow: /

# ── Tier 3: CDN-level block (robots.txt ineffective) ──────────────────────────
# Bytespider — configure WAF custom rule: User-Agent contains "Bytespider" → Block

Sitemap: https://agentpatterns.ai/sitemap.xml
```

## Compliance caveats

robots.txt is advisory, not enforceable. Watch for these caveats:

- Major providers comply: OpenAI (GPTBot, OAI-SearchBot), Anthropic (ClaudeBot, Claude-SearchBot, Claude-User), and Google (Google-Extended) respect robots.txt directives.
- ChatGPT-User exempt (December 2025): OpenAI's updated [crawler documentation](https://platform.openai.com/docs/bots) reclassified `ChatGPT-User` as a user-initiated agent and [removed its robots.txt compliance requirement](https://ppc.land/openai-revises-chatgpt-crawler-documentation-with-significant-policy-changes/). Disallow rules for `ChatGPT-User` are now ignored. You can only block interactive ChatGPT browsing at the CDN/WAF layer.
- Perplexity stealth crawling documented: [Cloudflare reported in August 2025](https://blog.cloudflare.com/perplexity-is-using-stealth-undeclared-crawlers-to-evade-website-no-crawl-directives/) that Perplexity rotates user-agents and ASNs to evade blocks and has been observed ignoring robots.txt. Treat allow-listing `PerplexityBot` and `Perplexity-User` as directional only, and use WAF rules for any hard block.
- Bytespider ignores it: ByteDance's Bytespider is documented to not respect robots.txt, so block it at the CDN/WAF level. See [Cloudflare WAF custom rules](https://developers.cloudflare.com/waf/custom-rules/) for setup.
- No legal enforcement: robots.txt does not prevent crawling. It signals intent. Legal protection requires ToS, CFAA claims, or contractual agreements.
- EU AI Act alignment: the EU regulatory framework encourages GPAI providers to document and respect publisher opt-out signals, and a `robots.txt` disallow for training crawlers is the de facto mechanism. Verify specific commitments against the published Code of Practice text as obligations evolve.

## Provider user-agent reference

| Provider | Training | Search index | User retrieval |
|----------|----------|-------------|----------------|
| OpenAI | `GPTBot` | `OAI-SearchBot` | `ChatGPT-User`* |
| Anthropic | `ClaudeBot` | `Claude-SearchBot` | `Claude-User` |
| Google | `Google-Extended` | *(standard Googlebot)* | `Google-CloudVertexBot` |
| Perplexity | *(PerplexityBot serves both)* | `PerplexityBot` | `Perplexity-User` |
| Meta | `Meta-ExternalAgent` | `Meta-ExternalFetcher` | — |

*ChatGPT-User — no longer bound by robots.txt as of OpenAI's December 2025 policy update; block at CDN/WAF if required.

## Why allow Tier 1

Blocking all AI crawlers has a compounding cost:

- Retrieval bots power citation-eligible AI answers — being absent means competitors fill that space
- AI-referred sessions grew substantially year over year through 2025, so blocking Tier 1 opts out of this traffic source entirely
- [Cloudflare data](https://blog.cloudflare.com/control-content-use-for-ai-training/) shows the crawl-to-referral ratio for OpenAI is ~1,700:1 and Anthropic ~73,000:1 — training crawlers give no referral return; retrieval bots give direct search traffic

## FAQ

**Why not just block all AI crawlers instead of picking tiers?**

Blocking everything cuts off Tier 1 retrieval bots too, which power citation-eligible AI answers — absence there just lets competitors fill the space. AI-referred traffic grew substantially through 2025, and [Cloudflare data](https://blog.cloudflare.com/control-content-use-for-ai-training/) shows Anthropic's crawl-to-referral ratio near 73,000:1, meaning training crawlers give no referral return while retrieval bots drive direct search traffic. Blanket blocking forfeits that entirely.

**Does robots.txt actually stop Bytespider from crawling my site?**

No. Bytespider (ByteDance) is documented to ignore robots.txt directives entirely, so a Disallow rule has no effect on it. The only effective control is a CDN or WAF custom rule that blocks requests where the User-Agent contains "Bytespider" — see [Cloudflare WAF custom rules](https://developers.cloudflare.com/waf/custom-rules/) for setup. robots.txt covers Tier 1 and Tier 2 bots; Tier 3 requires enforcement at the network layer.

**Is a robots.txt disallow for training crawlers legally enforceable?**

No — robots.txt is advisory, not a legal mechanism; it signals intent but doesn't prevent crawling on its own. Legal protection instead requires ToS terms, CFAA claims, or contractual agreements. The EU AI Act encourages GPAI providers to honor publisher opt-out signals like a robots.txt disallow, but site owners should verify specific commitments against the published Code of Practice text as obligations evolve.

**Does disallowing Google-Extended hurt my site's ranking in Google Search?**

No. Google-Extended is a separate, training-only user-agent from standard Googlebot, which handles search indexing and ranking — the reference table lists them separately. Disallowing Google-Extended in robots.txt opts your content out of AI training use without touching Googlebot's crawl for search results; the two directives are independent, so blocking one has no effect on the other.

## Key Takeaways

- The three-tier taxonomy (retrieval / training / non-compliant) maps directly to three distinct robots.txt strategies: allow / disallow / CDN block
- Blocking training crawlers does not block retrieval bots — they use separate user-agent strings
- robots.txt compliance is voluntary; most major providers respect it, but `ChatGPT-User` was exempted in December 2025 and Perplexity has been documented evading blocks — use CDN/WAF rules when hard enforcement is required
- The default strategy for documentation sites: allow Tier 1, disallow Tier 2, WAF-block Bytespider

## Related

- [How AI Engines Cite](how-ai-engines-cite.md)
- [llms.txt: Spec, Adoption, and Honest Limitations](llms-txt.md)
- [Agent-Readiness Discovery Surfaces](agent-readiness-discovery-surfaces.md)
- [GSC Search Console Monitoring](gsc-search-console-monitoring.md)
- [URL Fetch Public Index Gate](../security/url-fetch-public-index-gate.md)
- [SEO vs GEO](seo-vs-geo.md)
- [What Is GEO?](what-is-geo.md)
- [Measuring GEO Performance](measuring-geo-performance.md)
- [GEO for Technical Docs](geo-for-technical-docs.md)
