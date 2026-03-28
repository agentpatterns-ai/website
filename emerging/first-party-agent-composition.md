---
title: "First-Party Agent Composition: Agent-Built Features"
description: "Instead of integrating third-party SaaS products and stitching them together with webhooks, instruct coding agents to build each capability as a native, first-party feature within your application."
tags:
  - agent-design
  - cost-performance
---

# First-Party Agent Composition: Replace SaaS Stitching with Agent-Built Features

> Instead of integrating third-party SaaS products and stitching them together with webhooks, instruct coding agents to build each capability as a native, first-party feature within your application.

First-party agent composition is an approach where coding agents generate the CRM, analytics, and support tooling your product needs directly in your own codebase, storing all data in a single database. This eliminates the integration layer — no webhooks, no API rate limits, no cross-vendor data sync — and lets business-automation agents operate across the full dataset without translation overhead.

## The Pattern

Traditional approach:

```
Need CRM → subscribe to Pipedrive → integrate API → sync data via webhooks
Need analytics → subscribe to PostHog → embed tracking → export data for reports
Need support → subscribe to Zendesk → integrate API → sync customer records
```

First-party agent composition:

```
Need CRM → tell the coding agent "build customer management with these fields"
Need analytics → tell the coding agent "add first-party analytics tracking"
Need support → tell the coding agent "build a support desk with ticket management"
```

The data lives in your own database. Features share the same data model. No webhook plumbing, no vendor API rate limits, no data sync failures.

## How It Works

Geoffrey Huntley demonstrates this approach at Latent Patterns ([source](https://x.com/GeoffreyHuntley/status/2030683143360119292)):

1. **Describe the capability** — rough instruction to the coding harness: "I want Pipedrive, Trello, and Zendesk"
2. **Agent builds it** — the coding agent implements the feature against the existing codebase and data model
3. **Data stays first-party** — all customer records, analytics events, support tickets, and meeting notes live in the same database
4. **Layer agents on top** — with all data in one place, business automation agents can operate across the full dataset (e.g. customer enrichment feeds into sales prioritization feeds into automated follow-up)

## The Integration Advantage

When data is first-party, cross-cutting concerns become straightforward:

| Capability | SaaS-stitched | First-party |
|-----------|--------------|-------------|
| Show customer context on support ticket | API call to CRM, match by email, handle failures | Database join |
| Enrich customer profile from meeting notes | Export from transcription tool, import to CRM, map fields | Write to same customer record |
| Prioritize sales outreach by engagement | Export analytics, export CRM, merge in spreadsheet | Query across tables |

The elimination of integration middleware (Zapier, Make, custom webhooks) removes an entire failure surface.

## Agent-Layered Business Automation

First-party data enables agent automation that would require complex multi-vendor orchestration otherwise:

- **Customer enrichment** — enrich profiles via data providers (e.g. People Data Labs), store directly in customer records
- **Meeting transcription** — bot joins calls, transcribes, extracts action items, writes to the same CRM record
- **Sales analysis** — apply LLM prompts (Challenger, SPIN Selling frameworks) to transcripts, generate follow-up plans
- **Engagement scoring** — combine analytics, support history, and meeting notes into a unified priority score

Each layer reads from and writes to the same data model. No API translation, no webhook failures, no data sync lag.

## Trade-Offs

This pattern has real costs:

- **Maintenance is yours** — no vendor handles security patches, scaling, or compliance certifications for your custom features
- **Quality ceiling** — a purpose-built SaaS product (Zendesk, PostHog) has years of refinement; an agent-built clone may lack edge case handling
- **Scaling limits** — custom implementations may not handle the load that dedicated SaaS infrastructure handles
- **Rebuild risk** — if the agent builds something poorly, you debug it; with SaaS, you file a support ticket

## Where It Fits

First-party agent composition works best when:

- You are a small team or solo operator where integration overhead exceeds build cost
- Your data model is the competitive advantage and you cannot afford to fragment it across vendors
- The capabilities you need are standard (CRUD, dashboards, notifications) rather than domain-specialized (e.g. advanced email deliverability)

It is less appropriate when:

- Compliance requires vendor-certified infrastructure (SOC 2, HIPAA)
- The capability requires deep domain expertise (payment processing, advanced analytics)
- You need to scale to thousands of concurrent users immediately

## Example

A solo operator running a B2B SaaS product needs basic CRM and support-ticket tracking. Instead of subscribing to HubSpot and Zendesk, they use a coding agent (Claude with an [agent harness](../agent-design/agent-harness.md)):

**Prompt to the coding agent:**

```
Add a customer management module to this Rails app:
- customers table: id, name, email, company, tier (free/pro/enterprise), created_at
- support_tickets table: id, customer_id, subject, body, status (open/closed), created_at
- Admin views: customer list with ticket count, ticket detail with customer sidebar
- No external integrations -- all data in the existing PostgreSQL database
```

**The agent produces:**

```
db/migrate/20240901_add_crm.rb         -- migration for customers and tickets
app/models/customer.rb                 -- has_many :support_tickets
app/models/support_ticket.rb           -- belongs_to :customer
app/controllers/admin/customers_controller.rb
app/controllers/admin/support_tickets_controller.rb
app/views/admin/customers/index.html.erb  -- table with ticket count column
app/views/admin/support_tickets/show.html.erb  -- ticket + customer panel
```

**What this enables:** A second agent prompt adds engagement scoring because the data is unified:

```
Add an engagement_score column to customers. Populate it nightly:
  score = (support_tickets last 30 days x 2) + (logins last 30 days x 1)
Use the existing customers and support_tickets tables.
```

No webhook setup, no API key management, no data export. The scoring agent reads directly from the same schema.

## Key Takeaways

- First-party agent composition replaces SaaS integration with agent-built native features
- The core advantage is data locality: all data in one database enables cross-cutting automation without webhook plumbing
- Agent-layered business automation (enrichment, transcription, analysis) becomes straightforward when data is first-party
- Trade-offs include maintenance burden, quality ceiling, and scaling limits
- Best suited for small teams where integration overhead exceeds build cost

## Related

- [Hyper-Personalized Software](hyper-personalized-software.md)
- [Product-as-IDE](product-as-ide.md)
- [Cost-Aware Agent Design](../agent-design/cost-aware-agent-design.md)
- [Agent Harness](../agent-design/agent-harness.md)
