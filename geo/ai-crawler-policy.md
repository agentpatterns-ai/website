---
title: "AI Crawler Policy: robots.txt for the Three-Tier Crawler Landscape"
description: "Configure robots.txt to allow AI search and retrieval crawlers while blocking training scrapers — user-agent strings, decision matrix, compliance caveats."
aliases:
  - "robots.txt for AI crawlers"
  - "AI bot blocking policy"
tags:
  - geo
  - technique
  - tool-agnostic
  - workflows
---

# AI Crawler Policy: robots.txt for the Three-Tier Crawler Landscape

> AI crawlers split into retrieval bots (allow for citations), training scrapers (disallow), and non-compliant bots (WAF block) — each requiring a distinct robots.txt strategy.

## The Three-Tier Taxonomy

AI crawlers are not monolithic. Each major provider now operates separate bots for distinct purposes, each with its own user-agent string:

| Tier | Purpose | User-agents | robots.txt behaviour |
|------|---------|-------------|----------------------|
| **Tier 1 — User-facing retrieval** | Powers real-time citations in AI chat and search | `ChatGPT-User`, `OAI-SearchBot`, `Claude-User`, `Claude-SearchBot`, `PerplexityBot`, `Perplexity-User` | **Allow** — drives referral traffic and AI citations |
| **Tier 2 — Training scrapers** | Ingests content for model training datasets | `GPTBot`, `ClaudeBot`, `Google-Extended`, `Meta-ExternalAgent` | **Disallow** — no citation benefit; opts out of training data |
| **Tier 3 — Non-compliant bots** | Crawlers documented to ignore robots.txt | `Bytespider` (ByteDance) | **CDN/WAF block** — robots.txt is ineffective |

The tier distinction matters: blocking training crawlers without also blocking retrieval bots keeps your content eligible for AI search citations while opting out of model training datasets.

## Decision Matrix

| Goal | Action |
|------|--------|
| Appear in AI search answers (ChatGPT, Claude, Perplexity) | Allow Tier 1 |
| Prevent content entering training datasets | Disallow Tier 2 |
| Stop ByteDance/Bytespider from crawling | WAF custom rule |
| Opt out of everything | Disallow all AI user-agents + WAF |

The emerging practitioner consensus for documentation sites: allow Tier 1, disallow Tier 2.

## Reference Configuration

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

## Compliance Caveats

robots.txt is **advisory, not enforceable**. Key nuances:

- **Major providers comply**: OpenAI (GPTBot, OAI-SearchBot), Anthropic (ClaudeBot, Claude-SearchBot, Claude-User), and Google (Google-Extended) respect robots.txt directives.
- **OpenAI caveat**: `ChatGPT-User` robots.txt compliance status is not documented consistently across OpenAI's crawler pages — verify against current [OpenAI crawler documentation](https://platform.openai.com/docs/bots) before relying on it. Only `GPTBot` and `OAI-SearchBot` are listed in OpenAI's main robots.txt guidance.
- **Bytespider ignores it**: ByteDance's Bytespider is documented to not respect robots.txt — block at CDN/WAF level. See [Cloudflare WAF custom rules](https://developers.cloudflare.com/waf/custom-rules/) for setup.
- **No legal enforcement**: robots.txt does not prevent crawling. It signals intent. Legal protection requires ToS, CFAA claims, or contractual agreements.
- **EU AI Act alignment**: The EU regulatory framework encourages GPAI providers to document and respect publisher opt-out signals — robots.txt disallow for training crawlers is the de facto mechanism. Verify specific commitments against the published Code of Practice text as obligations evolve.

## Provider User-Agent Reference

| Provider | Training | Search index | User retrieval |
|----------|----------|-------------|----------------|
| OpenAI | `GPTBot` | `OAI-SearchBot` | `ChatGPT-User`* |
| Anthropic | `ClaudeBot` | `Claude-SearchBot` | `Claude-User` |
| Google | `Google-Extended` | *(standard Googlebot)* | `Google-CloudVertexBot` |
| Perplexity | *(PerplexityBot serves both)* | `PerplexityBot` | `Perplexity-User` |
| Meta | `Meta-ExternalAgent` | `Meta-ExternalFetcher` | — |

*ChatGPT-User — verify compliance status against current OpenAI crawler documentation.

## Why Allow Tier 1

Blocking all AI crawlers has a compounding cost:

- Retrieval bots power citation-eligible AI answers — being absent means competitors fill that space
- AI-referred sessions grew substantially year-over-year through 2025; blocking Tier 1 opts out of this traffic source entirely
- [Cloudflare data](https://blog.cloudflare.com/control-content-use-for-ai-training/) shows the crawl-to-referral ratio for OpenAI is ~1,700:1 and Anthropic ~73,000:1 — training crawlers give no referral return; retrieval bots give direct search traffic

## Key Takeaways

- The three-tier taxonomy (retrieval / training / non-compliant) maps directly to three distinct robots.txt strategies: allow / disallow / CDN block
- Blocking training crawlers does not block retrieval bots — they use separate user-agent strings
- robots.txt compliance is voluntary; major providers respect it, Bytespider does not
- The default strategy for documentation sites: allow Tier 1, disallow Tier 2, WAF-block Bytespider

## Related

- [How AI Engines Cite](how-ai-engines-cite.md)
- [llms.txt: Spec, Adoption, and Honest Limitations](llms-txt.md)
- [GSC Search Console Monitoring](../workflows/gsc-search-console-monitoring.md)
- [URL Fetch Public Index Gate](../security/url-fetch-public-index-gate.md)
- [SEO vs GEO](seo-vs-geo.md)
- [What Is GEO?](what-is-geo.md)
- [Measuring GEO Performance](measuring-geo-performance.md)
- [GEO for Technical Docs](geo-for-technical-docs.md)
