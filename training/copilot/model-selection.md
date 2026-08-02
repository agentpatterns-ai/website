---
title: "GitHub Copilot: Model Selection, Routing, and Costs"
description: "Understand the Copilot model roster, AI credit token economics, when to override Auto, cascade routing, the reasoning sandwich, and coding agent cost."
tags:
  - training
  - cost-performance
  - copilot
last_reviewed: 2026-07-28
---

# GitHub Copilot: Model Selection & Routing

> Model selection determines cost, quality, and speed for every Copilot interaction. Matching the right model tier to each task — budget for exploration, balanced for implementation, powerful for architecture — prevents both wasted spend and wasted rework.

GitHub Copilot exposes models from multiple providers across every surface: VS Code chat, the coding agent, CLI, custom agents, and GitHub.com. Since 2026-06-01, Copilot [bills usage in AI credits rather than premium requests](https://github.blog/news-insights/company-news/github-copilot-is-moving-to-usage-based-billing/): what an interaction costs depends on the model and the input, cached, and output tokens it consumes, priced at that model's published rate. That makes model choice a first-order cost lever — Claude Opus 5 output runs $25 per million tokens against Claude Haiku 4.5's $5.00, a 5x spread on the same work. The strategies below assume familiarity with the core training modules — particularly Module E's cost management section.

---

## The Model Roster

### What's available

GitHub Copilot supports models from multiple providers. The roster changes frequently — models are added, retired, and re-priced. Check the [supported models page](https://docs.github.com/en/copilot/reference/ai-models/supported-models) for the current list.

Spend is denominated in AI credits, where [1 credit = $0.01](https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing). Code completions and next edit suggestions consume no credits at all and stay unlimited on every paid plan, so everything below concerns chat, agent, and CLI turns.

As of July 2026, the published Copilot rates (USD per 1M tokens):

| Tier | Model | Input / cached input / output | Character |
|------|-------|-------------------------------|-----------|
| Budget | GPT-5 mini | $0.25 / $0.025 / $2.00 | Cheapest turn on the roster |
| Budget | Claude Haiku 4.5 | $1.00 / $0.10 / $5.00 | Fast — exploration, search, simple edits |
| Balanced | Gemini 2.5 Pro | $1.25 / $0.125 / $10.00 | Long-context reading |
| Balanced | Gemini 3.5 Flash | $1.50 / $0.15 / $9.00 | High-throughput iteration |
| Balanced | Claude Sonnet 5 | $2.00 / $0.20 / $10.00 | Default workhorse — most tasks |
| Balanced | GPT-5.4 | $2.50 / $0.25 / $15.00 | Reasoning at mid-tier cost |
| Powerful | Claude Opus 5 | $5.00 / $0.50 / $25.00 | Architecture, large-codebase analysis |
| Powerful | GPT-5.5 | $5.00 / $0.50 / $30.00 | Most expensive output on the roster |

Rates from the [models and pricing reference](https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing); tier labels are ours. Two structural facts fall out of the table. Cached input costs a tenth of fresh input on every model, so a long conversation that reuses context is much cheaper per turn than its raw token count suggests. And output is the expensive leg — priced at 5x its own input rate on every Claude tier and 6x to 8x on the GPT and Gemini rows — so a verbose model on an expensive tier is where budgets go.

[Auto mode](../../patterns/agent-design/auto-model-selection.md) takes [10% off model costs on individual plans](https://docs.github.com/en/copilot/concepts/billing/usage-based-billing-for-individuals) and routes to the model Copilot judges best for the task. Unless you have a specific reason to override, Auto is the default recommendation.

### Where models are selected

| Surface | How to select |
|---------|--------------|
| VS Code chat | Model picker in the chat panel. Reasoning models show a "Thinking Effort" submenu (Low/Medium/High) as of [v1.113](https://code.visualstudio.com/updates/v1_113). |
| Coding agent | Model picker when assigning a task. Falls back to Auto for `@copilot` mentions and issue assignments. |
| CLI | `/model` command in interactive mode, `--model` flag in programmatic mode |
| Custom agents | `model` field in `.agent.md` frontmatter |
| GitHub.com chat | Model picker in the chat interface |

---

## When to Override Auto

Auto mode handles most tasks well. Override it when:

| Situation | Override to | Why |
|-----------|-----------|-----|
| Exploration / file search | Budget model (Haiku) | Reading files and searching code doesn't need reasoning power. Save credits for the turns that do. |
| Architecture / novel design | Powerful model (Opus) | Complex reasoning benefits from larger models. The cost of a wrong architectural decision exceeds the cost of the model. |
| Long multi-file refactor | Balanced model (Sonnet) | Good reasoning at reasonable cost. Opus is overkill for systematic, well-defined refactors. |
| Generating tests | Balanced model (Sonnet) | Tests follow patterns. Balanced models handle them well. |
| Security review | Powerful model (Opus) | Security reasoning benefits from deeper analysis. Worth the higher token rate. |
| Routine bug fix | Auto | Let the system route. No reason to override. |

### The model override in custom agents

[Custom agents](../../tools/copilot/custom-agents-skills.md) (Module B) can specify a model in their frontmatter:

```markdown
---
description: Reviews code for security vulnerabilities
model: claude-opus-4-5
tools:
  - read_file
  - search_code
---
```

This ensures the security reviewer always uses a powerful model, regardless of what the user's default is set to. Use this for agents where model capability directly affects output quality.

Naming convention: Use display names (`claude-opus-4-5`) not pinned version IDs. Pinned IDs break silently when models are retired. Display names map to the current version automatically.

---

## Routing by Task Complexity

### The three-tier model

Match model capability to task complexity:

| Tier | Task type | Model | Example |
|------|-----------|-------|---------|
| Simple | Fact finding, file search, code navigation | Budget (Haiku) | "Find all usages of `validateToken`" |
| Standard | Implementation, test generation, refactoring, bug fixes | Balanced (Sonnet) | "Add input validation to the upload handler" |
| Complex | Architecture, novel design, security audit, multi-system reasoning | Powerful (Opus) | "Design the migration strategy from monolith to microservices" |

### Cascade routing

Start with a cheaper model. Escalate only when the task fails validation:

```
Task arrives
  → Try with balanced model (Sonnet 5)
  → Run tests / linter / type check
  → If all pass → done, at Sonnet token rates
  → If fail after 2 attempts → escalate to Opus 5 (2.5x Sonnet's input and output rates)
```

This is the cost-aware version of the [Ralph Wiggum Loop](../../loop-engineering/ralph-wiggum-loop.md) (Module D). The key insight: if the [backpressure](../../patterns/agent-design/agent-backpressure.md) system (tests, linter, types) provides binary pass/fail feedback, you can start cheap and escalate on failure. The test suite is the routing signal.

When cascade works: tasks with verifiable outcomes, where tests pass, types check, and the linter is clean. The feedback loop, the same [backpressure](harness-engineering.md) that gates the cascade, tells you whether the cheaper model was sufficient.

When cascade doesn't work: Tasks without binary feedback — architecture design, documentation quality, code review. There's no automated signal to trigger escalation. Use the powerful model directly for these, or read the cheap model's partial trajectory to decide when to escalate — see [Trajectory-Conditioned Model Escalation](../../patterns/agent-design/trajectory-conditioned-model-escalation.md).

---

## The Reasoning Sandwich

### What it is

Allocate reasoning budget unevenly across task phases: high for planning, standard for execution, high for verification. This outperforms both uniform high reasoning and uniform low reasoning.

```
Planning phase    → high reasoning (understand the problem, choose the approach)
Execution phase   → standard reasoning (implement the chosen approach)
Verification phase → high reasoning (review the implementation critically)
```

### Why it works

Concentrating reasoning at decision points, the [reasoning budget allocation](../../patterns/agent-design/reasoning-budget-allocation.md) pattern, outperforms both maximum reasoning throughout and uniform reduced reasoning. Maximum reasoning throughout is counterproductive: the model spends so long reasoning about each step that it risks exhausting token budgets before completing the task. Reasoning is most valuable where decisions are made, not where they're executed.

### How to apply it in Copilot

In VS Code — Plan mode first:

1. Start in **Plan mode** — high reasoning on the approach
2. Review the plan. Approve it.
3. Plan mode hands off to **Agent mode** — standard execution
4. After implementation, switch to **Ask mode** — review the changes critically

With custom agents:
```markdown
---
description: Plans architecture changes before implementation
model: claude-opus-4-5
tools:
  - read_file
  - search_code
---

You are an architecture planner. Your job is to:
1. Read the relevant code
2. Produce a detailed implementation plan
3. Identify risks and edge cases

Do NOT implement anything. Planning only.
```

Then hand off to a standard agent (Sonnet) for implementation, and use the planner again for review.

In the CLI:

1. Start in plan mode (`Shift+Tab` to cycle) — produces the approach
2. Switch to standard mode — execute
3. Use `/compact` before a final review prompt to reset attention

### The key insight

Don't run maximum reasoning throughout. It's expensive and counterproductive. Concentrate reasoning budget where decisions are made (planning, verification) and reduce it where execution is mechanical (writing code the plan already specifies).

---

## Model Selection for the Coding Agent

The coding agent runs asynchronously in GitHub Actions. Model selection affects:

- Cost: the session bills for every token it consumes end to end — reading files, running commands, editing, iterating
- Quality: More capable models make fewer mistakes, reducing back-and-forth
- Speed: Budget models are faster per action, but may need more actions to converge

### Recommendations by task type

| Task | Recommended model | Reasoning |
|------|------------------|-----------|
| Well-defined bug fix with test | Auto or Balanced | Clear task, verifiable outcome. The test suite provides backpressure. |
| Add tests for existing code | Auto or Balanced | Pattern-following task. Tests give Sonnet clear success criteria. |
| Documentation updates | Budget | Low reasoning requirement. Mostly template-filling. |
| Feature implementation with spec | Balanced | Standard implementation work with defined requirements. |
| Refactoring without clear spec | Powerful (Opus) | Needs to understand architecture and make design decisions. |
| Security-sensitive changes | Powerful | Higher stakes justify higher cost. |

### Why session length is the cost driver

A coding agent session is long: it reads files, runs commands, makes edits, runs tests, and iterates. Under the retired request-based model that entire session cost [one premium request per session, not one per action](https://docs.github.com/en/copilot/concepts/billing/copilot-requests); the per-action reading was a widespread misconception that made agent runs look far more expensive than they were. Under AI credits there is no per-session unit at all: cost rises with every token the session reads and writes, so session length rather than action count is what you manage.

Take a session consuming 2M input tokens and 200K output tokens, a plausible shape for a multi-file fix with a few test cycles. The token volumes are an illustrative assumption; the rates are the published ones.

| Model | Input | Output | Session cost |
|-------|-------|--------|--------------|
| Claude Haiku 4.5 | $2.00 | $1.00 | $3.00 (300 credits) |
| Claude Sonnet 5 | $4.00 | $2.00 | $6.00 (600 credits) |
| Claude Opus 5 | $10.00 | $5.00 | $15.00 (1,500 credits) |

A [$19 Copilot Business seat includes 1,900 credits](https://docs.github.com/en/copilot/concepts/billing/usage-based-billing-for-organizations-and-enterprises), or 3,000 promotionally through 2026-09-01, pooled across the organization rather than held per user. One Opus session of this size consumes half to four-fifths of a seat's monthly allowance depending on which figure applies; the same session on Haiku consumes a tenth to a sixth of it. That is the argument for reserving Opus for work where deeper reasoning changes the outcome, and for keeping context cached, since cached input bills at a tenth of fresh input.

---

## Competitive Evaluation

### When to compare models

The Agents page lets you assign the same task to different agents (Copilot, Anthropic Claude, OpenAI Codex). Use this to:

- Discover strengths: Run the same 5–10 representative tasks through different models. See which produces better results for your codebase's patterns.
- Validate defaults: Before standardizing on a model for a custom agent, test it against alternatives on real tasks.
- High-stakes decisions: For critical changes, run two agents independently and compare their approaches.

### Spot-check vs always-on

- Spot-check (recommended): Run competitive evaluation on a sample of tasks (e.g., 1 in 10) to calibrate. Then standardize on the winner for routine work.
- Always-on (expensive): Run both agents on every task. Only justified when the cost of a wrong approach exceeds double the agent cost — security-sensitive or architecture-critical changes.

---

## Example

A team receives a bug report: the `/api/upload` endpoint silently drops files larger than 50 MB. Here is how model selection plays out across the fix lifecycle. Assume each interactive turn consumes roughly 100K input tokens (the handler plus its middleware) and 10K output tokens, and the agent session five times that.

1. Triage — Claude Haiku 4.5

Open VS Code chat, switch to Haiku, and ask it to locate the upload handler and any size-limit constants. Reading files and searching code needs no reasoning power. 100K input at $1.00 plus 10K output at $5.00 comes to $0.15, or 15 credits.

2. Root-cause analysis — Claude Opus 5

The upload handler delegates to three middleware layers. Switch to Opus and ask it to trace the request path, identify where the size check occurs, and explain why large files are silently dropped instead of returning a 413 error. Opus's deeper reasoning catches the interaction between the streaming middleware and the error handler that swallows the exception. The same turn at Opus rates costs $0.75, or 75 credits.

3. Implementation — Claude Sonnet 5 via cascade

Assign the fix to the coding agent with Sonnet — a tightly scoped session, roughly a quarter the size of the multi-file illustration above. The agent edits the middleware, adds a proper 413 response, and runs the test suite. Tests pass on the first attempt — cascade routing never escalates. At 500K input and 50K output that is $1.00 plus $0.50, or 150 credits.

4. Review — Claude Opus 5

Switch back to Opus in Ask mode to review the diff. Opus identifies that the fix handles the content-length header check but misses chunked transfer encoding. The agent makes a second pass to cover that edge case. Another $0.75, or 75 credits.

Cost: $3.15, or 315 credits. Running Opus for all four phases at the same token volumes costs $6.00 (600 credits) — nearly double for the same outcome. Running Haiku throughout costs $1.20, but Haiku would not have found the middleware interaction in step 2, and a single round of rework costs more than the $1.95 saved.

---

## Key Takeaways

- Auto mode is the default and takes 10% off model costs on individual plans. Override only when you have a specific reason — exploration (go cheaper), architecture (go more powerful), security (go more powerful).
- Use display names, not pinned IDs in custom agent definitions. Models retire; display names (`claude-opus-4-5`) map to the current version automatically.
- Cascade routing starts cheap and escalates on failure. It works when backpressure (tests, types, linters) provides binary feedback. For tasks without automated feedback, use the powerful model directly.
- The [reasoning sandwich](../../patterns/agent-design/reasoning-budget-allocation.md) (high planning → standard execution → high verification) outperforms uniform reasoning. Use Plan mode for planning, Agent mode for execution, Ask mode for review.
- The coding agent bills by total tokens across the whole session, not per action, so session length is the cost driver. Reserve expensive models for work where reasoning quality changes the outcome.
- Spot-check competitive evaluation before standardizing. Run representative tasks through different models to discover which fits your codebase best.

## Related

- [GitHub Copilot: Team Adoption & Governance](team-adoption.md) — cost management section
- [GitHub Copilot: Customization Primitives](customization-primitives.md) — custom agents with model overrides
- [GitHub Copilot: Harness Engineering](harness-engineering.md) — backpressure as the cascade routing signal
- [Copilot vs Claude Billing Semantics](../../human/copilot-vs-claude-billing-semantics.md) — AI credits, per-model rates, credit pooling and forfeiture, budget controls
- [Cost-Aware Agent Design](../../token-engineering/cost-aware-agent-design.md) — big.LITTLE routing, cascade patterns, token economics
- [Reasoning Budget Allocation](../../patterns/agent-design/reasoning-budget-allocation.md) — the reasoning sandwich, dual-mode operation
- [Heuristic Effort Scaling](../../patterns/agent-design/heuristic-effort-scaling.md) — self-classifying complexity tiers
- [Cross-Vendor Competitive Routing](../../patterns/agent-design/cross-vendor-competitive-routing.md) — spot-check vs always-on evaluation
