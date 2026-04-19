---
title: "Harness Engineering: Environments Where Agents Succeed"
description: "Designing development environments where agents succeed by default through legibility, mechanical enforcement, and constrained solution spaces."
tags:
  - training
  - agent-design
  - tool-agnostic
---
# Harness Engineering

> The discipline of designing development environments where agents succeed by default -- through legibility, mechanical enforcement, and constrained solution spaces.

Harness engineering is the practice of shaping the development environment -- type systems, test suites, linters, CI pipelines, repo structure, and session scaffolding -- so that agents self-correct rather than requiring manual inspection. Where [Prompt Engineering](prompt-engineering.md) covers how to instruct agents and [Context Engineering](context-engineering.md) covers how to feed them information, harness engineering covers the layer underneath both: the environment itself.

The core thesis: **environment design beats prompt tuning**. LangChain improved Terminal Bench 2.0 scores from 52.8% to 66.5% through pure harness changes -- no model change ([LangChain](https://blog.langchain.com/improving-deep-agents-with-harness-engineering/)). OpenAI shipped roughly one million lines of production code without manually written source in a five-month experiment; the enabler was environment design, not prompt sophistication ([InfoQ](https://www.infoq.com/news/2026/02/openai-harness-engineering-codex/)).

---

## The Three Pillars

Every harness engineering investment falls into one of three categories.

| Pillar | What it means | How the agent experiences it |
|--------|--------------|------------------------------|
| **Legibility** | The repo is its own documentation. The agent orients by reading the codebase, not by being told about it. | Clear directory naming, consistent file patterns, dependency layers visible in the import graph |
| **Mechanical enforcement** | Constraints are enforced by tools, not by instructions. Certain categories of mistake are impossible. | Linters that block cross-layer imports, pre-commit hooks that run formatters, CI gates that require test passage |
| **Constrained solution spaces** | The architecture limits the number of valid approaches. The agent does not need to choose the right pattern -- there is only one valid pattern. | A single ORM (no raw SQL allowed), a single test framework, a standard component template |

All three pillars contributed in OpenAI's approach: legibility told agents what to do, mechanical enforcement told them when they were wrong, and constrained solution spaces made the correct path the only available path ([Lavaee](https://alexlavaee.me/blog/openai-agent-first-codebase-learnings/)).

For the full taxonomy and worked example, see [Harness Engineering](../../agent-design/harness-engineering.md).

---

## Backpressure: Automated Feedback Loops

[Backpressure](../../agent-design/agent-backpressure.md) is the automated feedback signal that tells an agent when its output is wrong. The agent writes code, reads the error, fixes the issue, and runs again. No human review required in the loop.

Agent autonomy scales directly with backpressure quality in the codebase -- not with model capability.

### The backpressure spectrum

| Feedback source | Speed | Precision | Remediation quality |
|----------------|-------|-----------|-------------------|
| **Type system** | Immediate | Exact location + expected type | High -- the error message usually contains the fix |
| **Linter** | Immediate | Exact location + rule name | Variable -- depends on whether the rule includes remediation guidance |
| **Unit tests** | Fast (seconds) | Assertion-level (expected vs actual) | High -- the diff between expected and actual is the diagnosis |
| **Integration tests** | Moderate | System-level | Moderate -- shows what failed, but root cause may be indirect |
| **CI pipeline** | Slow (minutes) | Build/deploy level | Low -- "build failed" requires investigation |

A codebase with strict types, comprehensive tests, and enforced linting enables agents to iterate autonomously through a write-check-fix loop. A codebase with no types, no tests, and no linting means every agent output requires manual review -- you become the feedback loop.

These investments compound: they benefit both agents and human developers. Adding types, writing tests, and documenting decisions are not agent-specific investments ([Codebase Readiness](../../workflows/codebase-readiness.md)).

---

## Why Tools Beat Prompts

Prompt instructions are probabilistic. Under task pressure -- context window filling, attention diverted -- compliance degrades and the agent reverts to training defaults.

Hooks and linters are deterministic. A pre-commit hook runs outside the agent's context window; the model cannot overrule it.

The decision rule from [Hooks for Enforcement vs Prompts for Guidance](../../verification/hooks-vs-prompts.md):

- **Use hooks** when compliance is non-negotiable, the rule is binary, and the behavior has a strong opposing prior in training data.
- **Use prompts** when the guidance is contextual, requires model judgment, or depends on factors a hook cannot inspect.

Instructions tell the agent what to do. The harness ensures it cannot do otherwise.

### The enforcement stack

From softest to hardest:

1. **Instructions** -- guidance the agent interprets and may ignore
2. **Linter rules** -- flags violations with error messages the agent reads and self-corrects
3. **Type system** -- blocks invalid types; the agent must satisfy the compiler
4. **Pre-commit hooks** -- gates commits; code must pass checks to be committed
5. **CI pipeline** -- gates merge; PR must pass all checks
6. **Branch protection** -- gates deployment; requires approvals

Each layer catches what the layer above missed. Written conventions rely on agent compliance. Mechanical enforcement makes violation impossible -- or immediately visible ([Fowler/Bockeler](https://martinfowler.com/articles/exploring-gen-ai/harness-engineering.html)).

---

## Feedback Loop Quality

The quality of error messages determines whether the agent self-corrects or spirals. Linter error messages are just-in-time context: the failure output enters the agent's context at the exact moment it needs to make a different decision. Investing in feedback loop quality often outperforms upgrading the model — see [Feedback as Capability Equalizer](../../agent-design/feedback-capability-equalizer.md).

Write messages as actionable remediation, not violation flags ([Fowler/Bockeler](https://martinfowler.com/articles/exploring-gen-ai/harness-engineering.html)):

```
# Violation flag (low value)
ERROR: Service layer cannot import from UI layer.

# Remediation message (high value)
ERROR: Service layer cannot import from UI layer.
  Move shared logic to a Provider in src/providers/,
  or restructure to keep UI-specific code in src/ui/.
  See docs/architecture/layer-rules.md for the dependency diagram.
```

The remediation message provides three things the agent needs: what is wrong, what to do instead, and where to find more context. This is more effective than any instruction file entry because it appears at the moment of violation, not preloaded into context thousands of tokens earlier.

OpenAI's custom linters enforcing these constraints were themselves generated by coding agents, creating a self-reinforcing loop: agents build the guardrails that constrain future agent work ([Lavaee](https://alexlavaee.me/blog/openai-agent-first-codebase-learnings/)).

---

## Pre-Completion Checklists

Agents optimize for task completion, not task correctness. They stop as soon as output looks plausible -- not when it is verified correct.

A [pre-completion checklist](../../verification/pre-completion-checklists.md) intercepts the completion signal and forces the agent through a verification sequence before it is allowed to finish. The verification sequence covers four phases:

1. **Planning** -- did you understand the requirement before starting?
2. **Building** -- did you implement what was specified, not a simpler substitute?
3. **Verification** -- did you run end-to-end tests, check for regressions, confirm the output satisfies the stated requirement?
4. **Fixing** -- did you address every issue found in verification before declaring done?

Checklist items must be specific and verifiable. "Run the test suite and confirm all tests pass" works. "Check your work" does not.

Implementation options range from a mandatory final step in the system prompt to a lifecycle hook that intercepts completion signals and injects the checklist before allowing the agent to terminate. Hooks are more reliable because they intercept completion even when the agent forgets the instruction from earlier in the conversation [unverified].

---

## Convergence Detection

For code tasks, the stopping criterion is clear: tests pass. For prose, specifications, and design documents, no such machine-checkable gate exists.

[Convergence detection](../../agent-design/convergence-detection.md) fills that gap with three observable signals:

| Signal | Converging | Diverging |
|--------|-----------|-----------|
| **Change velocity** | Rate of modifications slows across passes | Rate stays high or accelerates |
| **Output size** | Size stabilizes or shrinks | Size grows (scope creep, not refinement) |
| **Content similarity** | Diff between consecutive passes shrinks toward zero | Diff stays large |

When all three signals converge simultaneously, further passes yield diminishing returns. When any signal diverges, issues remain unresolved.

Three failure patterns indicate a restart is needed rather than continued iteration: **oscillation** (output alternates between two versions), **expansion** (output grows each pass), and **low-quality plateau** (all signals converge but quality remains poor).

Always pair convergence detection with a hard max-round limit as a cost fallback.

---

## Rigor Relocation

When agents write the code, engineering discipline does not disappear -- it [relocates](../../human/rigor-relocation.md) from code style and abstractions to scaffolding, feedback loops, and constraint enforcement.

| Traditional discipline | Relocated discipline |
|----------------------|---------------------|
| Clean code, good abstractions | Clean harness, good tool design |
| Code review catches bugs | Automated verification catches bug classes |
| Style guides enforce consistency | Linters enforce constraints mechanically |
| Manual QA validates behavior | Feedback loops validate continuously |
| Architecture docs guide humans | Structured docs guide agents |

The engineer's role shifts from code reviewer to harness designer: set measurable verification targets, design constraint enforcement infrastructure, approve architectural decisions rather than line-by-line code, and build feedback loops that catch bug classes rather than individual bugs.

A linter rule catches a dependency violation every time, in every session, for every agent -- compounding across iterations rather than catching issues once in a single PR review.

---

## Multi-Session Scaffolding

Long sessions accumulate context and degrade output quality. Short, focused sessions that leave clean handoff artifacts produce more reliable results.

### Progress files

For work spanning multiple sessions, maintain a progress file the agent reads at session start. The file tracks what is completed (with commit references), what is in progress, and what remains. This replaces accumulated conversation context (which degrades) with a persistent, editable artifact (which stays accurate).

### Structured commits as handoffs

Commit messages serve as handoff notes for the next session: what was implemented, what tests pass, and what the next task is.

### Entropy reduction

Codebases drift -- documentation goes stale, boundaries erode, conventions accumulate exceptions. [Entropy reduction agents](../../workflows/entropy-reduction-agents.md) run on a schedule, scanning for decay that accumulates silently between commits. OpenAI's harness team calls this "garbage collection" of technical debt ([Fowler/Bockeler](https://martinfowler.com/articles/exploring-gen-ai/harness-engineering.html)). The harness is maintained infrastructure, not a bootstrap step.

---

## Key Takeaways

- **Environment design beats prompt tuning.** Investing in types, tests, and linters improves agent output quality more durably than tweaking instructions. Every harness improvement compounds across all future sessions.
- **Agent autonomy scales with backpressure quality**, not with model capability. A codebase with strict types and comprehensive tests enables autonomous agent iteration. A codebase without them requires manual review of every output.
- **Linter messages are just-in-time agent context.** They appear at the exact moment and location of a violation with a specific remediation. Write custom rules with actionable error messages, not violation flags.
- **Instructions provide context; the harness provides enforcement.** Use both, but do not rely on instructions for rules that must be followed mechanically. If the consequence of violation is real, enforce it with tooling, not text.
- **Engineering rigor relocates, it does not disappear.** The discipline shifts from writing clean code to designing clean environments. The leverage point is infrastructure, not intelligence.
- **Design for short, focused sessions** with clean handoff artifacts. Progress files, structured commits, and one-feature-per-session discipline prevent context degradation and make multi-session work reliable.
- **Know when to stop iterating.** Convergence detection (change velocity, output similarity, content similarity) prevents wasted cycles. Hard iteration limits prevent runaway sessions.

## Related

**Training**

- [Prompt Engineering](prompt-engineering.md) -- instructing agents effectively
- [Context Engineering](context-engineering.md) -- feeding agents the right information
- [Tool Engineering](tool-engineering.md) -- designing tools agents can use reliably
- [Eval Engineering](eval-engineering.md) -- measuring agent quality with feedback loops and automated verification
- [Autonomous Research Loops](autonomous-research-loops.md) -- convergence detection and iteration control in autonomous agents
- [How the Four Disciplines Compound](prompt-context-harness-capstone.md) -- how prompt, context, harness, and tool engineering reinforce each other
- [GitHub Copilot: Harness Engineering](../copilot/harness-engineering.md) -- Copilot-specific application of these principles

**Source Pages**

- [Harness Engineering](../../agent-design/harness-engineering.md) -- the full pattern page with three pillars, worked example, and evidence
- [Agent Backpressure](../../agent-design/agent-backpressure.md) -- automated feedback loops and the autonomy spectrum
- [Convergence Detection](../../agent-design/convergence-detection.md) -- three-signal model for knowing when to stop
- [Pre-Completion Checklists](../../verification/pre-completion-checklists.md) -- verification gates before task completion
- [Hooks for Enforcement vs Prompts for Guidance](../../verification/hooks-vs-prompts.md) -- deterministic enforcement over advisory instructions
- [Codebase Readiness](../../workflows/codebase-readiness.md) -- code-level qualities that make a codebase agent-friendly
- [Entropy Reduction Agents](../../workflows/entropy-reduction-agents.md) -- scheduled background agents for codebase hygiene
- [Rigor Relocation](../../human/rigor-relocation.md) -- engineering discipline relocates from code to scaffolding
- [Trajectory Logging via Progress Files and Git History](../../observability/trajectory-logging-progress-files.md) -- progress files and git commits as a filesystem-based audit trail
