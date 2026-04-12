---
title: "GEO for Technical Docs: Developer Documentation Checklist"
description: "Apply GEO to API references, tutorials, how-to guides, and pattern pages. Checklists for new pages, existing page audits, and format-specific schema selection."
tags:
  - geo
  - technique
  - tool-agnostic
  - workflows
  - long-form
---

# GEO for Technical Docs

> GEO for technical docs is the practice of structuring API references, tutorials, how-to guides, and pattern pages so AI engines can extract, quote, and cite them accurately — using format-specific schema, answer-first structure, and sourced claims matched to each content type.

Technical documentation requires the same GEO principles as any content but applies them differently across formats. An API reference page, a tutorial, and a pattern page each have different structural conventions, different user intents, and different schema types — each maps to a distinct checklist. The sections below provide format-specific checklists, schema selection guidance, and an agent-discovery loop for identifying citation gaps.

## Why Content Format Determines GEO Strategy

GEO techniques are not uniform across content types. The [arxiv GEO paper (KDD 2024)](https://arxiv.org/abs/2311.09735) found that quotation addition, statistics, and citing sources each produced 30–40% visibility gains — but the mechanism matters. A tutorial page gains most from HowTo schema and sequential answer-first steps; a pattern page gains from TechArticle schema and quotable assertions. Applying the wrong technique to the wrong format produces neutral or negative results.

The formats this site produces map to three schema types:

| Format | Primary Schema | Top GEO Technique |
|--------|---------------|-------------------|
| Pattern / concept page | TechArticle | Quotable assertions + statistics |
| Tutorial / step-by-step | HowTo | Sequential steps + prerequisites |
| Anti-pattern page | FAQPage | Question-framed headings + direct answers |
| API reference section | FAQPage | Parameter Q&A format |

## New Page Checklist

Apply these to every new page before pushing. Order reflects impact on AI citation probability.

**Structure**

- [ ] H1 title is a noun phrase, not a verb phrase — it names the concept, not the task (e.g., "Answer-First Writing", not "How to Write Answer-First")
- [ ] Opening paragraph (40–60 words) directly answers the question the title implies — no context-setting preamble
- [ ] Each H2 section opens with a 40–60 word self-contained answer before elaborating
- [ ] Page covers exactly one concept — split if two mechanisms each stand alone as distinct topics
- [ ] Headings are descriptive, not generic ("How RAG Systems Score Sections", not "Overview")

**Content quality**

- [ ] At least one statistic or quantitative claim with a source link
- [ ] At least one direct quotation from a primary source (paper, docs, or spec)
- [ ] Every technical claim links to a primary source (docs, paper, spec) — not a secondary summary
- [ ] Code examples are minimal, runnable, and tagged with a language identifier
- [ ] No "in this article we will..." or "let's explore" preamble — start with the answer

**Schema (MkDocs Material)**

- [ ] Select the correct schema for the format (see table above)
- [ ] For pattern/concept pages: add `TechArticle` JSON-LD in a `<script>` block at the bottom of the page
- [ ] For tutorial pages: `HowTo` schema with numbered steps, prerequisites, and estimated time
- [ ] For anti-pattern / Q&A pages: `FAQPage` schema with one `Question`/`Answer` pair per H2 section

Minimal `TechArticle` block to place at the end of a pattern page:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "TechArticle",
  "headline": "Answer-First Writing: Structure Content for AI Retrieval",
  "description": "How placing a direct 40–60 word answer under each heading increases RAG citation probability.",
  "dateModified": "2026-03-17",
  "author": {"@type": "Organization", "name": "Agent Patterns"}
}
</script>
```

See [Schema and Structured Data](schema-and-structured-data.md) for FAQPage and HowTo templates.

**Metadata**

- [ ] `title` frontmatter: includes the concept name and a brief qualifier
- [ ] `description` frontmatter: one sentence, answers the question "what does this page help me do?"
- [ ] `tags` frontmatter: at minimum `geo` + category tag + tool-scope tag

## Existing Page Review Checklist

Audit in priority order — highest citation impact first.

| Priority | Check | Fix |
|----------|-------|-----|
| 1 | Opening paragraph answers the H1 question in ≤60 words | Rewrite to lead with the direct answer |
| 2 | Every H2 opens with a self-contained answer | Insert 40–60 word answer before elaboration |
| 3 | At least one statistic with a source link | Add quantitative claim from primary source |
| 4 | H2 headings are descriptive (not "Overview", "Details") | Rewrite to name the specific concept |
| 5 | Correct schema type is applied | Add or correct JSON-LD block |
| 6 | `description` frontmatter is present and specific | Write one-sentence answer to the page question |
| 7 | All URLs are stable and human-readable | Fix or redirect slugs with noise |
| 8 | Page was updated within the last 90 days | Refresh statistics, examples, or sources |

## Format-Specific Guidance

### Pattern and Concept Pages

Pattern pages document a repeatable design — a mechanism, a structure, or an approach that applies across multiple contexts. GEO priority: quotable assertions and statistics, because AI tools retrieve concept definitions using short declarative matches — a direct one-sentence definition gives the retrieval model a high-confidence anchor.

- Lead with a one-sentence definition the reader can quote verbatim
- Include a quantitative outcome where available ("reduces [context pollution](../anti-patterns/session-partitioning.md) by eliminating N token categories")
- Use `TechArticle` schema with `author`, `dateModified`, and `description` fields
- Add a `## Key Takeaways` section — terminal summaries provide a self-contained chunk that can be retrieved independently from the body.

### Tutorial Pages

Tutorial pages teach a procedure through sequenced steps. GEO priority: `HowTo` schema and sequential structure. `HowTo` schema maps directly to the step-list format AI assistants use when answering procedural questions.

- H1 must name the goal, not the process ("Bootstrapping a GEO-Optimized Page", not "How to Bootstrap")
- List prerequisites explicitly before step 1 — prerequisite lists are discrete, structured chunks that retrieval models can extract without parsing surrounding prose.
- Number steps; avoid prose that buries the sequence
- Each step: one action + one expected output — no compound steps
- Include estimated time in `HowTo` schema `totalTime` field (ISO 8601, e.g., `PT20M`)

### Anti-Pattern Pages

Anti-pattern pages describe what goes wrong and why. GEO priority: `FAQPage` schema, because the natural structure of an anti-pattern (symptom → cause → fix) matches the Q&A retrieval pattern.

- Frame each H2 as a question the failing developer would ask ("Why does my agent lose context mid-task?")
- Answer directly in the first sentence of each section
- Include a "What to do instead" section — corrective guidance answers a different (and more actionable) query than the failure description alone, increasing the range of questions this page can answer.
- Apply `FAQPage` schema with one `Question`/`Answer` pair per H2 section

### API Reference Sections

API reference pages document parameters, endpoints, and return values. GEO priority: scannable structure and `FAQPage` schema on troubleshooting subsections.

- One concept per page — do not document multiple endpoints on the same page
- Parameter tables: `Parameter | Type | Description | Example` — include the example column
- Common errors section: frame each error as a question ("What does `403 Forbidden` mean here?") and answer in ≤60 words
- Apply `FAQPage` schema to the errors/troubleshooting subsection only

## The Agent-Discovery Loop

The agent-discovery loop is a repeatable workflow for identifying which topics on this site are missing AI citation coverage, then feeding those gaps into content production.

```mermaid
graph LR
    A[Select a topic area] --> B[Query AI assistant with<br>developer questions]
    B --> C{Site cited?}
    C -- Yes --> D[Record: coverage confirmed]
    C -- No --> E[Note the question and<br>missing coverage]
    E --> F[/pipeline — create issue<br>from coverage gap]
    F --> A
```

**Step 1: Pick a topic area** (e.g., "agent context engineering", "tool calling patterns")

**Step 2: Query representative questions** — the questions a developer would ask when encountering this topic:

- "What is [concept]?"
- "How do I [task]?"
- "What's the difference between [A] and [B]?"
- "What are common mistakes with [pattern]?"

**Step 3: Check whether the site is cited.** Use at least two AI tools (ChatGPT, Perplexity, Claude). Note: absence of citation does not always mean a coverage gap — it may mean a GEO quality issue on an existing page.

**Step 4: Classify the gap.** Missing topic → create a new issue via `/pipeline`. Existing page not cited → apply the existing page review checklist first.

**Step 5: Feed into `/pipeline`.** A topic string from step 2 becomes a pipeline issue.

## When This Backfires

GEO techniques developed for general web content do not transfer uniformly to all technical documentation formats.

- **Versioned API references**: answer-first structure and JSON-LD schema add maintenance cost on every release cycle. For frequently-versioned endpoints, the cost often outweighs citation gains — internal developer portals rarely earn external AI citations regardless of optimization.
- **HowTo schema on linear tutorials**: numbering steps and adding `totalTime` estimates is only worthwhile when the tutorial covers a self-contained task. Multi-page tutorials or modular guides do not map cleanly to a single `HowTo` block; forcing the schema produces malformed structured data.
- **Statistics requirement on thin pages**: the GEO paper ([arxiv.org/abs/2311.09735](https://arxiv.org/abs/2311.09735)) measured visibility gains for statistics on general web content. For narrow technical reference pages (a single API parameter, one error code), forcing a statistic into a section that does not call for one degrades readability without confirmed citation benefit.
- **Internal-only documentation**: GEO techniques apply to content indexed by AI crawlers. Private or intranet documentation is not in scope — applying GEO structure there wastes editorial effort.

## Sources

- [GEO: Generative Engine Optimization (arxiv.org/abs/2311.09735)](https://arxiv.org/abs/2311.09735) — KDD 2024; 9 techniques benchmarked; quotation addition +41%, statistics +30–40%, keyword stuffing counterproductive
- [GitBook GEO Guide](https://gitbook.com/docs/guides/seo-and-llm-optimization/geo-guide) — section length, heading style, review checklist for documentation sites
- [Schema Markup for GEO/AEO (hashmeta.ai)](https://www.hashmeta.ai/en/blog/schema-markup-for-geo-aeo-implementing-faqpage-howto-and-article-schema-types) — FAQPage, HowTo, TechArticle implementation guidance
- [FAQ Schema and AI Search (frase.io)](https://www.frase.io/blog/faq-schema-ai-search-geo-aeo) — FAQPage as priority schema for AI citation probability
- [LLM-Optimized Content Structures (averi.ai)](https://www.averi.ai/how-to/llm%E2%80%91optimized-content-structures-tables-faqs-snippets) — optimal answer block size (40–60 words), citation lift statistics

## Related

- [Context Engineering](../context-engineering/context-engineering.md)
- [What is GEO?](what-is-geo.md)
- [Answer-First Writing](answer-first-writing.md)
- [Assertion Density](assertion-density.md)
- [Atomic Pages and Chunking](atomic-pages-and-chunking.md)
- [Schema and Structured Data](schema-and-structured-data.md)
- [Measuring GEO Performance](measuring-geo-performance.md)
- [How AI Engines Cite](how-ai-engines-cite.md)
- [SEO vs GEO](seo-vs-geo.md)
- [Topical Authority](topical-authority.md)
- [AI Crawler Policy](ai-crawler-policy.md)
- [llms.txt](llms-txt.md)
- [Content & Skills Audit Workflow](../workflows/content-skills-audit.md)

