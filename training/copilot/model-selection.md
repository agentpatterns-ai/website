---
title: "GitHub Copilot: Model Selection, Routing, and Costs"
description: "Understand the Copilot model roster, premium multipliers, when to override Auto, cascade routing, the reasoning sandwich, and coding agent cost."
tags:
  - training
  - copilot
---

# GitHub Copilot: Model Selection & Routing

> Model selection determines cost, quality, and speed for every Copilot interaction. Matching the right model tier to each task — budget for exploration, balanced for implementation, powerful for architecture — prevents both wasted spend and wasted rework.

GitHub Copilot exposes models from multiple providers across every surface: VS Code chat, the coding agent, CLI, custom agents, and GitHub.com. Each model carries a premium request multiplier that compounds across actions, making selection a first-order cost lever. The strategies below assume familiarity with the core training modules — particularly Module E's cost management section.

---

## The Model Roster

### What's available

GitHub Copilot supports models from multiple providers. The roster changes frequently — models are added, retired, and re-priced. Check the [supported models page](https://docs.github.com/en/copilot/reference/ai-models/supported-models) for the current list.

As of March 2026, the general shape:

| Tier | Models (examples) | Premium multiplier | Character |
|------|------------------|-------------------|-----------|
| **Free** | GPT-4o, GPT-4.1 | 0x | Unlimited routine completions and chat |
| **Budget** | Claude Haiku 4.5 | 0.33x | Fast, cheap, good for exploration and simple tasks |
| **Balanced** | Claude Sonnet 4/4.5, GPT-4.1 | 1x | Default workhorse — most tasks |
| **Powerful** | Claude Opus 4.5/4.6, Gemini 2.5 Pro | 3x+ | Complex reasoning, architecture, large codebase analysis |
| **Ultra** (our label) | Claude Opus 4.6 fast (preview, Pro+/Enterprise) | 30x | Maximum capability, maximum cost |

**Auto mode** provides a 10% multiplier discount on Copilot Chat (in VS Code, GitHub.com, and JetBrains on paid plans) and routes to the model Copilot judges best for the task. Unless you have a specific reason to override, Auto is the default recommendation.

### Where models are selected

| Surface | How to select |
|---------|--------------|
| **VS Code chat** | Model picker in the chat panel. Reasoning models show a "Thinking Effort" submenu (Low/Medium/High) as of [v1.113](https://code.visualstudio.com/updates/v1_113). |
| **Coding agent** | Model picker when assigning a task. Falls back to Auto for `@copilot` mentions and issue assignments. |
| **CLI** | `/model` command in interactive mode, `--model` flag in programmatic mode |
| **Custom agents** | `model` field in `.agent.md` frontmatter |
| **GitHub.com chat** | Model picker in the chat interface |

---

## When to Override Auto

Auto mode handles most tasks well. Override it when:

| Situation | Override to | Why |
|-----------|-----------|-----|
| **Exploration / file search** | Budget model (Haiku) | Reading files and searching code doesn't need reasoning power. Save premium requests. |
| **Architecture / novel design** | Powerful model (Opus) | Complex reasoning benefits from larger models. The cost of a wrong architectural decision exceeds the cost of the model. |
| **Long multi-file refactor** | Balanced model (Sonnet) | Good reasoning at reasonable cost. Opus is overkill for systematic, well-defined refactors. |
| **Generating tests** | Balanced model (Sonnet) | Tests follow patterns. Balanced models handle them well. |
| **Security review** | Powerful model (Opus) | Security reasoning benefits from deeper analysis. Worth the premium. |
| **Routine bug fix** | Auto | Let the system route. No reason to override. |

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

**Naming convention**: Use display names (`claude-opus-4-5`) not pinned version IDs. Pinned IDs break silently when models are retired. Display names map to the current version automatically.

---

## Routing by Task Complexity

### The three-tier model

Match model capability to task complexity:

| Tier | Task type | Model | Example |
|------|-----------|-------|---------|
| **Simple** | Fact finding, file search, code navigation | Budget (Haiku) | "Find all usages of `validateToken`" |
| **Standard** | Implementation, test generation, refactoring, bug fixes | Balanced (Sonnet) | "Add input validation to the upload handler" |
| **Complex** | Architecture, novel design, security audit, multi-system reasoning | Powerful (Opus) | "Design the migration strategy from monolith to microservices" |

### Cascade routing

Start with a cheaper model. Escalate only when the task fails validation:

```
Task arrives
  → Try with balanced model (Sonnet)
  → Run tests / linter / type check
  → If all pass → done (1x cost)
  → If fail after 2 attempts → escalate to powerful model (Opus, 3x cost)
```

This is the cost-aware version of the [Ralph Wiggum Loop](../../agent-design/ralph-wiggum-loop.md) (Module D). The key insight: if the [backpressure](../../agent-design/agent-backpressure.md) system (tests, linter, types) provides binary pass/fail feedback, you can start cheap and escalate on failure. The test suite is the routing signal.

**When cascade works**: Tasks with verifiable outcomes — tests pass, types check, linter clean. The feedback loop tells you whether the cheaper model was sufficient.

**When cascade doesn't work**: Tasks without binary feedback — architecture design, documentation quality, code review. There's no automated signal to trigger escalation. Use the powerful model directly for these.

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

Concentrating reasoning at decision points outperforms both maximum reasoning throughout and uniform reduced reasoning. Maximum reasoning throughout is counterproductive — the model spends so long reasoning about each step that it risks exhausting token budgets before completing the task. Reasoning is most valuable where decisions are made, not where they're executed.

### How to apply it in Copilot

**In VS Code — Plan mode first**:

1. Start in **Plan mode** — high reasoning on the approach
2. Review the plan. Approve it.
3. Plan mode hands off to **Agent mode** — standard execution
4. After implementation, switch to **Ask mode** — review the changes critically

**With custom agents**:
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

**In the CLI**:

1. Start in plan mode (`Shift+Tab` to cycle) — produces the approach
2. Switch to standard mode — execute
3. Use `/compact` before a final review prompt to reset attention

### The key insight

Don't run maximum reasoning throughout. It's expensive and counterproductive. Concentrate reasoning budget where decisions are made (planning, verification) and reduce it where execution is mechanical (writing code the plan already specifies).

---

## Model Selection for the Coding Agent

The coding agent runs asynchronously in GitHub Actions. Model selection affects:

- **Cost**: Premium request multiplier applies to each action the agent takes
- **Quality**: More capable models make fewer mistakes, reducing back-and-forth
- **Speed**: Budget models are faster per action, but may need more actions to converge

### Recommendations by task type

| Task | Recommended model | Reasoning |
|------|------------------|-----------|
| Well-defined bug fix with test | Auto or Balanced | Clear task, verifiable outcome. The test suite provides backpressure. |
| Add tests for existing code | Auto or Balanced | Pattern-following task. Tests have clear success criteria. |
| Documentation updates | Budget | Low reasoning requirement. Mostly template-filling. |
| Feature implementation with spec | Balanced | Standard implementation work with defined requirements. |
| Refactoring without clear spec | Powerful | Needs to understand architecture and make design decisions. |
| Security-sensitive changes | Powerful | Higher stakes justify higher cost. |

### The cost multiplier matters more for the coding agent

The coding agent takes many actions per task — reading files, running commands, making edits, running tests, iterating. Each action consumes premium requests at the model's multiplier. A task that takes 50 actions:

- At 0.33x (Haiku): ~17 premium requests
- At 1x (Sonnet): 50 premium requests
- At 3x (Opus): 150 premium requests

For routine tasks where a balanced model succeeds, using Opus costs 3x more without proportional quality improvement. Reserve Opus for tasks where the reasoning improvement justifies the multiplier.

---

## Competitive Evaluation

### When to compare models

The Agents page lets you assign the same task to different agents (Copilot, Anthropic Claude, OpenAI Codex). Use this to:

- **Discover strengths**: Run the same 5–10 representative tasks through different models. See which produces better results for your codebase's patterns.
- **Validate defaults**: Before standardising on a model for a custom agent, test it against alternatives on real tasks.
- **High-stakes decisions**: For critical changes, run two agents independently and compare their approaches.

### Spot-check vs always-on

- **Spot-check** (recommended): Run competitive evaluation on a sample of tasks (e.g., 1 in 10) to calibrate. Then standardise on the winner for routine work.
- **Always-on** (expensive): Run both agents on every task. Only justified when the cost of a wrong approach exceeds double the agent cost — security-sensitive or architecture-critical changes.

---

## Example

A team receives a bug report: the `/api/upload` endpoint silently drops files larger than 50 MB. Here is how model selection plays out across the fix lifecycle.

**1. Triage — Budget model (Haiku, 0.33x)**

Open VS Code chat, switch to Haiku, and ask it to locate the upload handler and any size-limit constants. Haiku reads files and searches code quickly without burning premium requests on reasoning.

**2. Root-cause analysis — Powerful model (Opus, 3x)**

The upload handler delegates to three middleware layers. Switch to Opus and ask it to trace the request path, identify where the size check occurs, and explain why large files are silently dropped instead of returning a 413 error. Opus's deeper reasoning catches the interaction between the streaming middleware and the error handler that swallows the exception.

**3. Implementation — Balanced model (Sonnet, 1x) via cascade**

Assign the fix to the coding agent with Sonnet. The agent edits the middleware, adds a proper 413 response, and runs the test suite. Tests pass on the first attempt — cascade routing never escalates.

**4. Review — Powerful model (Opus, 3x)**

Switch back to Opus in Ask mode to review the diff. Opus identifies that the fix handles the content-length header check but misses chunked transfer encoding. The agent makes a second pass to cover that edge case.

**Cost**: ~20 premium requests total (3 Haiku + 8 Sonnet + 9 Opus equivalent). Running Opus throughout would have cost ~60 equivalent premium requests — 3x more for the same outcome.

---

## Key Takeaways

- **Auto mode is the default**. Override only when you have a specific reason — exploration (go cheaper), architecture (go more powerful), security (go more powerful).
- **Use display names, not pinned IDs** in custom agent definitions. Models retire; display names map to the current version automatically.
- **Cascade routing** starts cheap and escalates on failure. It works when backpressure (tests, types, linters) provides binary feedback. For tasks without automated feedback, use the powerful model directly.
- **The reasoning sandwich** (high planning → standard execution → high verification) outperforms uniform reasoning. Use Plan mode for planning, Agent mode for execution, Ask mode for review.
- **The coding agent's cost multiplier compounds** across many actions per task. A 3x multiplier on 50 actions is significant. Reserve expensive models for tasks where reasoning quality matters.
- **Spot-check competitive evaluation** before standardising. Run representative tasks through different models to discover which fits your codebase best.

## Related

**Training**

- [GitHub Copilot: Team Adoption & Governance](team-adoption.md) — cost management section
- [GitHub Copilot: Customization Primitives](customization-primitives.md) — custom agents with model overrides
- [GitHub Copilot: Harness Engineering](harness-engineering.md) — backpressure as the cascade routing signal

**Patterns**

- [Cost-Aware Agent Design](../../agent-design/cost-aware-agent-design.md) — big.LITTLE routing, cascade patterns, token economics
- [Reasoning Budget Allocation](../../agent-design/reasoning-budget-allocation.md) — the reasoning sandwich, dual-mode operation
- [Heuristic Effort Scaling](../../agent-design/heuristic-effort-scaling.md) — self-classifying complexity tiers
- [Cross-Vendor Competitive Routing](../../agent-design/cross-vendor-competitive-routing.md) — spot-check vs always-on evaluation
