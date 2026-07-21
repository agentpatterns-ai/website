---
title: "Agent Extension Conflicts: When Installed Skills and MCP Servers Fight Each Other"
term: "Agent Extension Conflicts"
description: "Extensions that pass their own evals can combine to degrade an agent — per-extension testing misses the combinatorial failure between context budget, vocabulary, and instruction surfaces."
tags:
  - agent-design
  - anti-pattern
  - tool-agnostic
aliases:
  - agent extension interference
  - extension composition tax
  - skill and MCP cross-extension conflict
last_reviewed: 2026-06-23
maturity: adopted
---

# Agent Extension Conflicts: When Installed Skills and MCP Servers Fight Each Other

> Extensions that each pass their own evals can combine to degrade an agent — the failure lives in the composition, so per-extension tests miss it.

Agent extension conflicts are the degradation that appears when you install independently-tested skills, MCP servers, or plugin tools together on one agent. Each extension passes its own evals. The combination loses accuracy, predictability, or context headroom because the extensions compete for the same finite substrate — context budget, descriptive vocabulary, and instruction surface. Microsoft Developer Blog names this overhead the composition tax and warns that the model "doesn't process your extension's content in isolation" but "attends to everything at once" ([Microsoft Developer Blog, 2026](https://developer.microsoft.com/blog/when-your-agent-extensions-fight-each-other)).

The failure is structurally distinct from over-stacking scaffold components inside a single agent design ([Cross-Component Interference](cross-component-interference.md)) and from catalog governance over time ([Agent Sprawl](agent-sprawl.md)). It is the marketplace-shaped failure at the extension boundary: you install N extensions, each one tested in isolation, and the agent gets worse.

## The three mechanisms

### 1. Context-budget contention

Every installed extension injects tokens before the agent reads its first turn. Each MCP tool costs 550–1,400 tokens for name, description, JSON schema, field descriptions, and enums — 5–15× more than the minimum-viable schema for the same tool ([Layered, 2026](https://layered.dev/mcp-tool-schema-bloat-the-hidden-token-tax-and-how-to-fix-it/)). GitHub's official MCP server consumes ~17,600 tokens of tool definitions per request; connecting several servers reaches 30,000+ tokens of metadata before any work happens ([StackOne, 2026](https://www.stackone.com/blog/mcp-token-optimization/)). Anthropic confirms the mechanism: "as the number of connected tools grows, loading all tool definitions upfront and passing intermediate results through the context window slows down agents and increases costs" and "in cases where agents are connected to thousands of tools, they'll need to process hundreds of thousands of tokens before reading a request" ([Anthropic, 2026](https://www.anthropic.com/engineering/code-execution-with-mcp)). The mechanism reproduces in real harnesses: [claude-code#60141](https://github.com/anthropics/claude-code/issues/60141) reports that subagent context budget is "blown by eagerly-materialized MCP tool schemas and skill listing" — Explore and general-purpose subagents become unusable when you install a moderate MCP and skill set.

### 2. Vocabulary collision

Two extensions that describe similar capabilities in similar terms produce ambiguous routing, which the model resolves stochastically. Microsoft's worked case: "The developer asks 'set up auth for my app.' Both tools match the intent, the model picks one, and it might not be yours." ([Microsoft, 2026](https://developer.microsoft.com/blog/when-your-agent-extensions-fight-each-other)). Anthropic states the same: "when tools overlap in function or have a vague purpose, agents can get confused about which ones to use" and "too many tools or overlapping tools can distract agents from pursuing efficient strategies" ([Anthropic, 2025](https://www.anthropic.com/engineering/writing-tools-for-agents)). The collision is invisible to per-extension evals because each extension is tested with only its own vocabulary present.

### 3. Silent guidance conflict

Extensions inject instructions through tool descriptions, `.github/copilot-instructions.md`, `CLAUDE.md`, or system-prompt additions. Contradictory guidance resolves without an error path — Microsoft warns "the outcome depends on context ordering and phrasing strength, filtered through whatever the model's training data says" ([Microsoft, 2026](https://developer.microsoft.com/blog/when-your-agent-extensions-fight-each-other)). The Arbiter study analyzed Claude Code, Codex CLI, and Gemini CLI system prompts and surfaced 152 interference findings in undirected scouring plus 21 hand-labeled interference patterns; one Arbiter finding corresponded to a Google-filed Gemini CLI memory-system patch, though the patch addressed symptoms rather than the structural conflict ([Hilden, 2026](https://arxiv.org/abs/2603.08993)). The authors conclude that prompt policies should be treated as testable control artifacts — per-instruction compliance is not enough, so you must test the interactions between standing rules.

## Why it works

The three mechanisms compound on one substrate: the finite attention budget, where n² token-pair cost makes a packed context computationally thinner ([Anthropic, 2025](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)). Extensions add tokens, descriptions, and instructions that compete with the task — the same dilution mechanism [Cross-Component Interference](cross-component-interference.md) documents for scaffold components, now at the extension-installation layer. Per-extension evals miss it because each extension was tested with the rest of the budget free and the rest of the vocabulary absent.

## How to detect it

Use additive measurement: baseline with no extensions, add one at a time and re-measure, then pairwise-isolate any regression ([Microsoft, 2026](https://developer.microsoft.com/blog/when-your-agent-extensions-fight-each-other)). The metric is net lift versus expected additive gains; a negative net lift is the composition tax. Re-run on schedule — extensions evolve independently, so last quarter's safe stack regresses without warning.

## When this backfires

The framing fires too early under four conditions:

- Strong progressive-disclosure harness already in place. Claude Code's MCP Tool Search auto-triggers when MCP definitions exceed 10% of context, loading tool definitions on demand and cutting MCP context overhead by roughly 85% ([Anthropic, 2026](https://www.anthropic.com/engineering/code-execution-with-mcp)). Skills load only YAML at startup (~100 tokens per skill); body, scripts, and reference material stay out of context until the agent decides they are relevant. Under progressive disclosure the context-budget mechanism approaches zero and pre-emptive pruning may cost more than it saves.
- Disjoint domains, no overlapping affordances. Twenty extensions serving Slack, Linear, Datadog, AWS, and other non-overlapping services with no descriptive vocabulary collision do not produce the routing failure. The conflict framing applies when extensions compete for the same intent; vendor-curated namespacing (`asana_search` vs `jira_search`) keeps the collision rate low ([Anthropic, 2025](https://www.anthropic.com/engineering/writing-tools-for-agents)).
- Curated single-vendor stack. A first-party extension set tested together as a release artifact has neither the marketplace governance gap nor the descriptive-vocabulary diversity that produces silent conflicts. Curated skills improve performance by +16.2pp on average; the regression comes from self-generated or third-party skills, not curated ones ([SkillsBench, 2026](https://arxiv.org/html/2602.12670v1)).
- Frontier-scale model with abundant headroom. The maximally-equipped agent's gap over smaller subsets shrinks with model strength — 32% at 8B, 19% at 70B, ~0% at Haiku-class scale — though it never inverts ([Liu, 2026 via Cross-Component Interference](cross-component-interference.md)). Frontier models tolerate extension stacking; they do not benefit from it. If the cost of measuring per-stack lift exceeds the modeled regression, leaving extensions installed may be the pragmatic choice on the strongest tier.

## Example

Same user prompt — "open an issue for the broken auth flow" — under two install postures:

| | Eager / unscoped | Progressive / scoped |
|---|---|---|
| Installed | github-mcp + jira-mcp + linear-mcp, all with overlapping `search` / `create_issue` / `add_comment` | tool-search + jira-mcp only |
| Schemas in context at turn 0 | 143K / 200K tokens (72%) — one team's report ([StackOne, 2026](https://www.stackone.com/blog/mcp-token-optimization/)) | ~2K tokens (98.7% reduction) ([Anthropic, 2026](https://www.anthropic.com/engineering/code-execution-with-mcp)) |
| Routing | Picks `linear-mcp/create_issue` — but the team tracks bugs in Jira | `jira_create_issue` is the only candidate |
| Outcome | Wrong tracker; 57K tokens left for the session | Correct tracker; 195K headroom |

The right-hand column applies all four mitigations below: scope (one tracker), lazy-load (Tool Search), namespace (`jira_*` prefix), and prune.

## Mitigations

- Prune. Default to uninstalled. Only carry an extension whose net lift over baseline is measured and positive on tasks you actually run. One team replaced eleven MCP servers with six Claude skills and reported a faster, cheaper, smarter workflow — the win was removing extensions, not adding ([Valev, 2026](https://medium.com/@danielvalev/diagram-of-eleven-cluttered-mcp-servers-being-replaced-by-six-clean-claude-skills-folders-in-a-e8ea93361040)).
- Scope. Install per-project, not globally. An extension that helps in one repository may regress another by dragging in vocabulary the second repository never needed.
- Lazy-load. Use progressive-disclosure mechanisms — MCP Tool Search, on-demand skill body loading, code execution with MCP — to keep tool definitions out of context until the agent decides they are relevant ([Anthropic, 2026](https://www.anthropic.com/engineering/code-execution-with-mcp)). See [MCP Eager vs JIT Loading](../../tool-engineering/mcp-eager-vs-jit-loading.md).
- Namespace tools. Prefix tools by service and resource (`asana_search`, `asana_projects_search`) so the model can disambiguate without inferring from vague descriptions ([Anthropic, 2025](https://www.anthropic.com/engineering/writing-tools-for-agents)).
- Test the combination, not the unit. Run an additive measurement pass before any extension change and again after — per-extension evals are necessary but not sufficient.

## Key Takeaways

- Extension conflicts are a composition-tax failure mode — individual extensions pass evals; their combination degrades the agent.
- Three mechanisms compound: context-budget contention (each MCP tool costs 550–1,400 tokens; 30 tools eats 30K+ before turn 1), vocabulary collision (overlapping descriptions produce stochastic routing), and silent guidance conflict (contradictory instructions resolve with no error path).
- Per-extension evals are blind to the failure — detection requires additive measurement against a baseline plus pairwise isolation.
- Progressive disclosure (Claude Code's MCP Tool Search, on-demand skill body loading) cuts the context-budget mechanism by ~85% and shifts the dominant remaining failure to vocabulary collision.
- The framing is overkill on disjoint-domain stacks, curated single-vendor sets, and capable-model + curated-tool universes; default to uninstalled and measure before adding.

## Related

- [Cross-Component Interference in Agent Scaffolds](cross-component-interference.md) — sibling failure mode at the scaffold-component layer (planning/memory/retrieval) rather than the extension layer.
- [Agent Sprawl: Unmanaged Sub-Agent and Skill Proliferation](agent-sprawl.md) — catalog and fleet governance over time; extension conflicts are the per-decision failure shape, sprawl is the cumulative catalog failure.
- [The Infinite Context](infinite-context.md) — same attention-dilution mechanism at the context-window layer.
- [Dynamic Tool Fetching Breaks KV Cache](dynamic-tool-fetching-cache-break.md) — sibling MCP-layer failure mode; the cache-break is the cost when lazy-loading is implemented naively.
- [Context Budget Allocation](../../context-engineering/context-budget-allocation.md) — the budget framing this anti-pattern violates at the extension boundary.
- [MCP Eager vs JIT Loading](../../tool-engineering/mcp-eager-vs-jit-loading.md) — the lazy-load mitigation as a tool-engineering decision.
- [Assuming Loaded Skills Stay Enforced in Long Contexts](assuming-loaded-skills-stay-enforced.md) — a single loaded skill silently sheds its own requirements as the trajectory grows, a failure that appears even without a second conflicting extension.
