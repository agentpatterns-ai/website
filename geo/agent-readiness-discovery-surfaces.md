---
title: "Agent-Readiness Discovery Surfaces for Docs Sites"
term: "Agent-Readiness Discovery Surfaces"
description: "Which machine-readable discovery surfaces a content site should publish for AI agents — and why the API, auth, and MCP family only applies when you run a service."
aliases:
  - "agent discovery surfaces"
  - "machine-readable discovery surfaces"
  - "agent-ready discovery layer"
tags:
  - geo
  - technique
  - tool-agnostic
last_reviewed: 2026-07-20
maturity: emerging
---

# Agent-Readiness Discovery Surfaces for Docs Sites

> Publish the discovery surfaces that match your site — a content corpus advertises crawler signals, Link headers, and markdown, not API or MCP metadata.

Agent-readiness scanners score a site on the machine-readable surfaces it exposes so AI agents can discover how to consume it. The core judgment is publishing the surfaces that describe what your site actually is, not publishing more surfaces.

## Match the surface to the site

Discovery surfaces fall into two families, and only one applies to a static content corpus.

| Family | Surfaces | Applies to a docs site? |
|--------|----------|-------------------------|
| Content-corpus | Content Signals, `Link` headers, markdown alternates, agent-skills index | Yes — the site is the content |
| Service | OpenAPI / API catalog, OAuth metadata, MCP server card | Only if you run a callable service |

Cloudflare's Agent Readiness score scans four dimensions — Discoverability, Content, Bot Access Control, and Capabilities. It marks the Commerce checks optional on non-commerce sites and excludes them from the score when no commerce signals exist ([Cloudflare](https://blog.cloudflare.com/agent-readiness/)). That exclusion is the applicability split in miniature. A scanner that always demanded every surface would penalize a docs site for lacking a checkout API it has no reason to expose.

## The content-corpus surfaces

A documentation site should publish these, because each describes content it already has:

- Content Signals — `robots.txt` directives (`search`, `ai-input`, `ai-train`) that state how AI systems may use content after access. An IETF draft (`draft-romm-aipref-contentsignals`, AIPREF working group), declarative and not enforced ([contentsignals.org](https://contentsignals.org/), [IETF draft](https://datatracker.ietf.org/doc/draft-romm-aipref-contentsignals/)).
- `Link` headers — RFC 8288 web-linking relations such as `alternate` (a markdown twin) and `describedby` (an llms.txt index), pointing agents to machine-friendly views ([RFC 8288](https://www.rfc-editor.org/info/rfc8288/)).
- Markdown alternates — a plain-markdown copy of each page beside its HTML, so an agent fetches prose without parsing site chrome. See [llms.txt: Spec, Adoption, and Honest Limitations](llms-txt.md) for the companion index convention.
- Agent-skills index — `/.well-known/agent-skills/index.json`, published only if the site ships skills. Each entry carries a name, type, `url`, and `sha256` digest per the [Cloudflare Agent Skills Discovery RFC](https://github.com/cloudflare/agent-skills-discovery-rfc).

## The service surfaces

The rest of the discovery layer describes a callable service, not a corpus. Publish these only when a real backend answers behind them:

- API catalog — `/.well-known/api-catalog`, a linkset pointing to OpenAPI specs and docs ([RFC 9727](https://www.rfc-editor.org/info/rfc9727/)).
- OAuth metadata — `/.well-known/oauth-protected-resource` and authorization-server metadata for protected APIs ([RFC 9728](https://datatracker.ietf.org/doc/html/rfc9728), RFC 8414).
- MCP server card — `/.well-known/mcp.json`, describing an HTTP MCP server's capabilities before connection ([SEP-1649](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1649)).

Earlier-stage proposals sit in the same family: DNS-AID advertises agents through SVCB `_agents` DNS records ([IETF draft](https://datatracker.ietf.org/doc/draft-mozleywilliams-dnsop-dnsaid/)), and WebMCP exposes in-page tools. Both are drafts with thin consumer bases today, so treat them as emerging rather than baseline.

## Why it works

These surfaces work because they relocate consumption metadata to predictable, machine-readable locations, chiefly the `/.well-known/` URI prefix defined by RFC 8615 ([RFC 8615](https://www.rfc-editor.org/info/rfc8615/), [Agent Skills Discovery RFC](https://github.com/cloudflare/agent-skills-discovery-rfc)). An agent then finds what a site offers without prior configuration or URL guessing. The payoff holds only under two conditions: a real consumer reads the surface, and something real sits behind it. A surface that names a capability the site does not have is a dangling pointer. It signals nothing an agent can act on.

## When this backfires

Publishing surfaces that do not match the site is the same failure mode as keyword stuffing, and it fails for the same reason:

- Empty service metadata — an OAuth or MCP card on a site with no callable service points agents at nothing; adding one purely to raise a scanner score is decorative ([No Hacks](https://nohacks.co/blog/cloudflare-agent-readiness-score)).
- Thin consumer base — Content Signals is declarative and not enforced, and no major provider has confirmed reading llms.txt at inference time, so effort on immature surfaces buys little until a real consumer arrives ([contentsignals.org](https://contentsignals.org/), [How AI Engines Cite](how-ai-engines-cite.md)).
- Stale indexes — an agent-skills index or llms.txt pointing at deleted artifacts is worse than none, because an agent follows it and fails.

## Example

The agentpatterns.ai site ran an [isitagentready.com](https://isitagentready.com/) scan and actioned only the content-corpus findings. It added Content Signals to `robots.txt`, an RFC 8288 `Link` header, build-time markdown twins for every page, and an agent-skills index advertising its public skills shelf. It rejected the API catalog, OAuth metadata, and MCP server-card findings as not applicable. The site is a static corpus with no service to call, so those surfaces would have been dangling pointers. Publishing them to lift a score would have added maintenance cost for no agent-facing signal.

## Key Takeaways

- Discovery surfaces split into content-corpus surfaces and service surfaces; a docs site publishes the first family and skips the second unless it runs a service.
- The `/.well-known/` prefix (RFC 8615) makes surfaces discoverable without configuration — but only when a real consumer and a real backend both exist.
- Publishing empty API, auth, or MCP metadata to chase an agent-readiness score is the keyword-stuffing anti-pattern in a new form.
- Most of these standards are drafts with thin adoption; mark provenance honestly rather than overstating who consumes each surface today.

## Related

- [AI Crawler Policy](ai-crawler-policy.md)
- [llms.txt: Spec, Adoption, and Honest Limitations](llms-txt.md)
- [Schema and Structured Data](schema-and-structured-data.md)
- [How AI Engines Cite](how-ai-engines-cite.md)
- [GEO for Technical Docs](geo-for-technical-docs.md)
- [What Is GEO?](what-is-geo.md)
