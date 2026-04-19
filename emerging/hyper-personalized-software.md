---
title: "Hyper-Personalized Software: The Return of RAD"
description: "AI-driven development is making custom-built software economically viable again, reversing two decades of SaaS consolidation and vendor lock-in."
aliases:
  - RAD
  - Rapid Application Development
  - bespoke software
tags:
  - human-factors
  - workflows
---

# Hyper-Personalized Software: The Return of Rapid Application Development

> AI-driven development is making custom-built software economically viable again, reversing two decades of SaaS consolidation where businesses conformed to someone else's product vision.

## The Cycle

Hyper-personalized software is custom-built tooling tailored to a single business's processes — the opposite of adopting a generic SaaS product and conforming your workflow to fit it. AI coding agents are making this model economically viable again after two decades of SaaS consolidation. Software development economics move in cycles:

1. **RAD era (~1995-2005)** — Microsoft Access, Delphi, Visual Basic. Every business had hyper-personalized software. A single developer could build a custom CRM, inventory system, or reporting tool in days. The software fit the business, not the other way around.

2. **SaaS consolidation (~2005-2023)** — Web applications replaced custom tools. Businesses adopted Salesforce, Zendesk, HubSpot — generic products that required the business to adapt its processes. Integration gaps were filled with Zapier, webhook plumbing, and middleware.

3. **AI-driven RAD (~2024-present)** — Coding agents compress development cycles significantly. The economics shift: agent-driven development cost is measured per session, while SaaS subscriptions plus integration maintenance compound monthly with no ceiling.

Geoffrey Huntley argues this cycle is completing ([source](https://x.com/GeoffreyHuntley/status/2030683143360119292)): "The last time we had hyper-personalised software for business was Microsoft Access, Delphi and Visual Basic... every business had hyper-personalised software. They didn't have to bend or conform to someone else's product vision."

## The Economics Argument

SaaS has hidden costs beyond the subscription:

- **Conformity cost** — adapting business processes to fit the product's assumptions
- **Integration cost** — stitching tools together with workflow automation (Zapier, Make, custom webhooks)
- **Data fragmentation** — customer data scattered across vendors, each with its own API and export format
- **Vendor lock-in** — switching costs accumulate as integrations deepen

The shift works because LLM inference cost scales with tokens, not developer headcount. Claude Sonnet 4.6 is priced at roughly $3 per million input tokens and $15 per million output tokens ([Claude API pricing](https://platform.claude.com/docs/en/about-claude/pricing)), and enterprise telemetry puts average Claude Code spend near $13 per active developer day ([Verdent, *Claude Code Pricing 2026*](https://www.verdent.ai/guides/claude-code-pricing-2026)). SaaS subscriptions, by contrast, scale with usage and users — costs that recur every month and increase as the business grows. When an AI agent compresses the build time for a functional CRM, support desk, or analytics dashboard, the total cost of ownership comparison changes. One-time build cost shrinks; ongoing SaaS subscription and integration overhead remains fixed.

## What "Every Business Needs"

Huntley identifies a common set of business capabilities that every company needs but currently sources from separate vendors:

- Analytics
- Customer relationship management (CRM)
- Support desk
- Newsletters
- Meeting scheduling

Each is a standalone SaaS product today. In a hyper-personalized model, each becomes a first-party feature built by agents and integrated natively. See [First-Party Agent Composition](first-party-agent-composition.md) for the implementation pattern.

## Counterarguments

The RAD era ended for reasons that still apply:

- **Maintenance burden** — custom software needs ongoing updates; SaaS vendors handle this centrally
- **Security and compliance** — SaaS providers invest in SOC 2, GDPR, penetration testing; a solo builder may not
- **Scaling limits** — custom Access databases broke at hundreds of concurrent users; custom agent-built software may hit similar walls
- **Knowledge concentration** — when the one developer who built the system leaves, the system becomes unmaintainable

AI agents partially address the maintenance argument (agents can maintain what agents built), but security, compliance, and organizational knowledge remain open challenges. One important caveat: peer-reviewed research shows that iterative AI code generation increases critical vulnerabilities by 37.6% after just five refinement cycles — even security-focused prompts introduced new flaws ([Security Degradation in Iterative AI Code Generation, IEEE-ISTAS 2025](https://arxiv.org/abs/2506.11022)). Using agents to maintain agent-built code without human review between iterations may deepen the security gap rather than close it.

## Example

A small e-commerce company replaces three SaaS subscriptions — a helpdesk, a newsletter tool, and a reporting dashboard — with Claude-built first-party alternatives. The agent scaffolds a support ticket handler in a single session:

```bash
# Scaffold a support inbox handler using Claude Code
claude "Build a FastAPI endpoint that receives Stripe webhooks for failed payments,
logs them to a SQLite database, and sends a templated follow-up email via
SendGrid. Include a /tickets admin view listing open cases."
```

The resulting service runs on a $5/month VPS. The displaced SaaS stack — an entry-tier helpdesk seat (Zendesk Support Team starts at $19/agent/month, [Zendesk pricing](https://www.zendesk.com/pricing/)) plus a small newsletter plan and a hosted dashboard — adds up to roughly $80–$100/month for a single operator. The custom build is iterated by re-prompting the same agent with the existing codebase as context for ongoing maintenance (dependency updates, schema migrations).

This illustrates the economics argument: the conformity cost (adapting business processes to fit Zendesk's ticket model) is eliminated, and the integration overhead (syncing Stripe events to Zendesk via Zapier) no longer exists.

## Key Takeaways

- Software economics are cyclical: RAD (custom) → SaaS (generic) → AI-driven RAD (custom again)
- The cost comparison is shifting: agent-built custom software may be cheaper than SaaS subscriptions plus integration overhead
- The counterarguments from the end of the first RAD era (maintenance, security, scaling) still apply and are only partially addressed by AI
- This trend affects what developers build, not just how — the role shifts toward orchestrating agent-built systems rather than building SaaS products

## Related

- [First-Party Agent Composition](first-party-agent-composition.md)
- [Product-as-IDE](product-as-ide.md)
- [Cost-Aware Agent Design](../agent-design/cost-aware-agent-design.md)
