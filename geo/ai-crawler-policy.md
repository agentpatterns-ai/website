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
last_reviewed: 2026-11-03
maturity: established
---

# AI Crawler Policy: robots.txt for the Three-Tier Crawler Landscape

> AI crawlers split into retrieval bots (allow), training scrapers (disallow), and bots to WAF-block — each needs a distinct robots.txt strategy.

Related lesson: [Four Engines, Four Backends](https://learn.agentpatterns.ai/geo/four-engines-four-backends/) — this concept features in a hands-on lesson with quizzes.

## The three-tier taxonomy

AI crawlers are not monolithic. Most major providers operate separate bots for distinct purposes, each with its own user-agent string. Google is the exception: `Google-Extended` is a robots.txt token, not a separate user-agent.

| Tier | Purpose | User-agents | robots.txt behavior |
|------|---------|-------------|----------------------|
| Tier 1 — User-facing retrieval | Powers real-time citations in AI chat and search | `ChatGPT-User`*, `OAI-SearchBot`, `Claude-User`, `Claude-SearchBot`, `PerplexityBot`‡, `Perplexity-User`‡ | Allow — keeps pages eligible for AI answers and citations (`ChatGPT-User` may ignore the rule*) |
| Tier 2 — Training scrapers | Ingests content for model training datasets | `GPTBot`, `ClaudeBot`, `Google-Extended`†, `Meta-ExternalAgent` | Disallow — opts out of training data (`Google-Extended` also opts out of Gemini grounding) |
| Tier 3 — Optional hard block | Bots you want out whatever robots.txt says | `Bytespider` (ByteDance) | CDN/WAF block — a WAF rule enforces what robots.txt only requests |

The tier distinction matters. You can block most training crawlers without blocking retrieval bots. That keeps your content eligible for AI search citations while opting out of training datasets. `Google-Extended` is the exception: it also controls grounding in Gemini Apps and Vertex AI, so it does not map cleanly to one tier.

\* OpenAI says `ChatGPT-User` actions are user-initiated and "robots.txt rules may not apply" ([OpenAI crawler documentation](https://platform.openai.com/docs/bots)). Treat a Disallow rule for it as unreliable.

† Google documents `Google-Extended` as a standalone product token that controls training and grounding (content from the Google Search index supplied to the model at prompt time) in Gemini Apps and Vertex AI. It does not affect Google Search inclusion or ranking ([Google](https://developers.google.com/search/docs/crawling-indexing/google-common-crawlers)).

‡ Cloudflare documented Perplexity rotating user-agents and ASNs to bypass robots.txt ([August 2025 report](https://blog.cloudflare.com/perplexity-is-using-stealth-undeclared-crawlers-to-evade-website-no-crawl-directives/)). Use WAF for hard blocks.

## Decision matrix

| Goal | Action |
|------|--------|
| Appear in AI search answers (ChatGPT, Claude, Perplexity) | Allow Tier 1 |
| Prevent content entering training datasets | Disallow Tier 2 (`Google-Extended` also limits Gemini grounding) |
| Block ByteDance/Bytespider | WAF custom rule |
| Opt out of everything | Disallow all AI user-agents + WAF |

## Reference configuration

A three-tier `robots.txt` looks like this:

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

# ── Tier 3: CDN-level block (optional) ────────────────────────────────────────
# Bytespider — configure WAF custom rule: User-Agent contains "Bytespider" → Block

Sitemap: https://agentpatterns.ai/sitemap.xml
```

### What this site's robots.txt does

This site's [`robots.txt`](../robots.txt) does not use the Tier 2 rules above. One group allows `/` for `GPTBot`, `ClaudeBot`, `Google-Extended`, and the retrieval bots, and a `User-agent: *` group allows `/` for everything else, `Meta-ExternalAgent` included. Both groups carry `Content-Signal: ai-train=yes`. `Bytespider` has no named group, so the wildcard group allows it in the file. The file's header comment says a Cloudflare WAF rule blocks it.

`Allow: /` is the crawl control. `Content-Signal` is a preference signal. The file has no `__usage_ai-training` group, the token that [AI Training Preference Signals](ai-training-preference-signals.md) describes.

## Compliance caveats

robots.txt is advisory, not enforceable. Watch for these caveats:

- Provider documentation names robots.txt as the control for these bots: OpenAI for [GPTBot and OAI-SearchBot](https://platform.openai.com/docs/bots), Anthropic for [ClaudeBot, Claude-SearchBot and Claude-User](https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler), and Google for [Google-Extended](https://developers.google.com/search/docs/crawling-indexing/google-common-crawlers).
- ChatGPT-User is user-initiated: OpenAI's [crawler documentation](https://platform.openai.com/docs/bots) says robots.txt rules "may not apply" to it, and [coverage](https://ppc.land/openai-revises-chatgpt-crawler-documentation-with-significant-policy-changes/) reports the December 2025 change. To block interactive ChatGPT browsing, use a CDN/WAF rule.
- Perplexity stealth crawling documented: [Cloudflare reported in August 2025](https://blog.cloudflare.com/perplexity-is-using-stealth-undeclared-crawlers-to-evade-website-no-crawl-directives/) that Perplexity rotates user-agents and ASNs to evade blocks and has been observed ignoring robots.txt. Treat allow-listing `PerplexityBot` and `Perplexity-User` as directional only, and use WAF rules for any hard block.
- Meta-ExternalFetcher may bypass it: Meta's [crawler documentation](https://developers.facebook.com/docs/sharing/webmasters/web-crawlers/) says this user-requested fetcher "may bypass robots.txt".
- Hard blocks need the network layer: a CDN/WAF rule blocks a user-agent such as `Bytespider` whatever robots.txt says. See [Cloudflare WAF custom rules](https://developers.cloudflare.com/waf/custom-rules/) for setup. Vercel's changelog lists managed rules in Vercel Firewall that control AI crawlers and AI assistants separately ([Vercel changelog](https://vercel.com/changelog/block-ai-crawlers-and-assistants-independently-with-managed-rules)).
- No enforcement: robots.txt does not prevent crawling. It signals intent.

## Provider user-agent reference

| Provider | Training | Search index | User retrieval |
|----------|----------|-------------|----------------|
| OpenAI | `GPTBot` | `OAI-SearchBot` | `ChatGPT-User`* |
| Anthropic | `ClaudeBot` | `Claude-SearchBot` | `Claude-User` |
| Google | `Google-Extended` (token only; also controls Gemini grounding) | *(standard Googlebot)* | — |
| Perplexity | — | `PerplexityBot` | `Perplexity-User` |
| Meta | `Meta-ExternalAgent` | — | `Meta-ExternalFetcher`‡ |

*ChatGPT-User — OpenAI says robots.txt rules may not apply; block at CDN/WAF if required.

‡ Meta says this fetcher may bypass robots.txt.

Sources: [OpenAI](https://platform.openai.com/docs/bots), [Anthropic](https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler), [Google](https://developers.google.com/search/docs/crawling-indexing/google-common-crawlers), [Perplexity](https://docs.perplexity.ai/guides/bots), [Meta](https://developers.facebook.com/docs/sharing/webmasters/web-crawlers/).

## Why allow Tier 1

Blocking all AI crawlers has a cost:

- Retrieval bots power citation-eligible AI answers — a site that blocks them is absent from those answers
- [Cloudflare data](https://blog.cloudflare.com/control-content-use-for-ai-training/) shows a June 2025 crawl-to-referral ratio of ~1,700:1 for OpenAI and ~73,000:1 for Anthropic. Crawling returns few visits, which is the argument for disallowing Tier 2 rather than for allowing Tier 1

## FAQ

**Why not just block all AI crawlers instead of picking tiers?**

Blocking everything cuts off Tier 1 retrieval bots too, which power citation-eligible AI answers. [Cloudflare data](https://blog.cloudflare.com/control-content-use-for-ai-training/) shows a June 2025 crawl-to-referral ratio near 73,000:1 for Anthropic, which is a reason to disallow training crawlers. Blocking only Tier 2 keeps retrieval bots in.

**How do I block Bytespider?**

Use a CDN or WAF custom rule that blocks requests where the User-Agent contains "Bytespider" — see [Cloudflare WAF custom rules](https://developers.cloudflare.com/waf/custom-rules/) for setup. A robots.txt Disallow only asks. A WAF rule enforces, so it works whether or not the bot reads robots.txt.

**Does a robots.txt disallow for training crawlers stop them?**

Not by itself. robots.txt is advisory: it signals intent and does not prevent crawling. Providers that name it as their control (see Compliance caveats) honor it. For hard enforcement, use a CDN/WAF rule, which blocks the request before it reaches your content. OpenAI also says robots.txt rules may not apply to ChatGPT-User, a fetcher that acts on a user's request.

**Does disallowing Google-Extended hurt my site's ranking in Google Search?**

No. Google-Extended is a robots.txt product token, not a separate HTTP user-agent. It controls training and grounding in Gemini Apps and Vertex AI. Blocking it does not affect Google Search inclusion, and Google states it is not used as a ranking signal. The block only opts your content out of that training and grounding ([Google](https://developers.google.com/search/docs/crawling-indexing/google-common-crawlers)).

## Key Takeaways

- The three-tier taxonomy (retrieval / training / optional hard block) maps to three strategies: allow / disallow / CDN block
- Blocking training crawlers does not block retrieval bots — they use separate user-agent strings. The exception is `Google-Extended`, a robots.txt token that also controls Gemini grounding
- robots.txt compliance is voluntary; OpenAI, Anthropic and Google document it as their control, but OpenAI says `ChatGPT-User` may not follow it, Meta says `Meta-ExternalFetcher` may bypass it, and Cloudflare reported Perplexity evading blocks — use CDN/WAF rules when hard enforcement is required
- The strategy this page describes: allow Tier 1, disallow Tier 2, and WAF-block any bot (such as Bytespider) you want out regardless of robots.txt

## Related

- [AI Training Preference Signals in robots.txt](ai-training-preference-signals.md)
- [How AI Engines Cite](how-ai-engines-cite.md)
- [llms.txt: Spec, Adoption, and Honest Limitations](llms-txt.md)
- [Agent-Readiness Discovery Surfaces](agent-readiness-discovery-surfaces.md)
- [GSC Search Console Monitoring](gsc-search-console-monitoring.md)
- [URL Fetch Public Index Gate](../security/url-fetch-public-index-gate.md)
- [SEO vs GEO](seo-vs-geo.md)
- [Measuring GEO Performance](measuring-geo-performance.md)
