---
title: "Hyper-Personalized Software: The Return of Rapid Application Development"
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

3. **AI-driven RAD (~2024-present)** — Coding agents can produce functional software in minutes. The economics shift: building a custom feature may cost less than a monthly SaaS subscription plus integration maintenance.

Geoffrey Huntley argues this cycle is completing ([source](https://x.com/GeoffreyHuntley/status/2030683143360119292)): "The last time we had hyper-personalised software for business was Microsoft Access, Delphi and Visual Basic... every business had hyper-personalised software. They didn't have to bend or conform to someone else's product vision."

## The Economics Argument

SaaS has hidden costs beyond the subscription:

- **Conformity cost** — adapting business processes to fit the product's assumptions
- **Integration cost** — stitching tools together with workflow automation (Zapier, Make, custom webhooks)
- **Data fragmentation** — customer data scattered across vendors, each with its own API and export format
- **Vendor lock-in** — switching costs accumulate as integrations deepen

When an AI agent can build a functional CRM, support desk, or analytics dashboard in hours, the total cost of ownership comparison changes. The build cost drops; the SaaS overhead stays constant.

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

AI agents partially address the maintenance argument (agents can maintain what agents built), but security, compliance, and organizational knowledge remain open challenges.

## Example

A small e-commerce company replaces three SaaS subscriptions — a helpdesk, a newsletter tool, and a reporting dashboard — with Claude-built first-party alternatives. The agent scaffolds a support ticket handler in a single session:

```bash
# Scaffold a support inbox handler using Claude Code
claude "Build a FastAPI endpoint that receives Stripe webhooks for failed payments,
logs them to a SQLite database, and sends a templated follow-up email via
SendGrid. Include a /tickets admin view listing open cases."
```

The resulting service runs on a $5/month VPS. Monthly SaaS equivalent (Zendesk Lite + Mailchimp Essentials) was $85/month. The custom build took 4 hours including review; ongoing maintenance (dependency updates, schema migrations) is handled by re-prompting the same agent with the existing codebase as context.

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
