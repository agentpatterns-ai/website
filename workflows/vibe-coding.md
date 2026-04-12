---
title: "Vibe Coding: Outcome-Oriented Agent-Assisted Development"
description: "Delegate implementation entirely to the agent and focus on evaluating outcomes — appropriate for low-risk work where the cost of wrong output is low"
tags:
  - workflows
  - human-factors
  - testing-verification
aliases:
  - "Outcome-Oriented Agent-Assisted Development"
  - "Anti-Pattern: Vibe Coding"
---

# Vibe Coding: Outcome-Oriented Agent-Assisted Development

> Delegate implementation entirely to the agent and focus on evaluating outcomes — appropriate for low-risk work where the cost of wrong output is low.

!!! info "Also known as"
    Anti-Pattern: Vibe Coding, Outcome-Oriented Agent-Assisted Development

## What Vibe Coding Is

Vibe coding is a development approach where the developer stops reading diffs, stops tracking implementation details, and focuses entirely on whether the output works and feels right. The term was [coined by Andrej Karpathy in February 2025](https://x.com/karpathy/status/1886192184808149383):

> "There's a new kind of coding I call 'vibe coding', where you fully give in to the vibes, embrace exponentials, and forget that the code even exists."

Karpathy described accepting all suggestions without reading diffs, copy-pasting error messages back to the agent without comment, and using voice input to minimize keyboard interaction. The developer's role shifts from implementation to outcome evaluation and course correction.

This is the inverse of the [plan-first loop](plan-first-loop.md). Where plan-first workflows invest in understanding before execution, vibe coding skips understanding entirely and relies on rapid iteration to converge on the desired result.

## When Vibe Coding Works

Vibe coding is appropriate when the cost of wrong output is low and iteration is cheap:

**Prototyping and throwaway tools.** Scripts, one-off data transformations, internal tools that will be replaced. If the output is wrong, you discard it and try again — no production impact.

**Bash scripts and automation.** Short scripts with tight feedback loops where the agent can write, execute, read errors, and fix within seconds. The [write-execute-debug cycle](../tool-engineering/cli-scripts-as-agent-tools.md) is naturally suited to vibe coding because each iteration is near-zero cost.

**Permutation-style work.** Generating variations of an established pattern — multiple API endpoints following the same structure, test cases from a template, configuration files across environments. The pattern is already proven; the agent is replicating it ([Source: ClaudeLog](https://claudelog.com/mechanics/vibe-coding)).

**Exploratory research.** Using agents to investigate libraries, APIs, or approaches where the goal is learning, not shipping code.

## When Vibe Coding Fails

Vibe coding produces [black box nodes](../anti-patterns/trust-without-verify.md) — parts of the system you do not understand. This is acceptable for throwaway code. It is dangerous for anything that persists:

**Production systems.** Code you do not understand is code you cannot debug, maintain, or extend. Vibe-coded production code creates technical debt that compounds with every change. As [Simon Willison states](https://simonwillison.net/2025/Mar/19/vibe-coding/): "I won't commit any code to my repository if I couldn't explain exactly what it does."

**Security-critical code.** Authentication, authorization, encryption, input validation — these require understanding, not vibes. A [Tenzai assessment](https://www.csoonline.com/article/4116923/output-from-vibe-coding-tools-prone-to-critical-security-flaws-study-finds.html) of five AI coding tools found 69 vulnerabilities across 15 test applications, concentrated in API authorization and business logic. [Kaspersky reports](https://www.kaspersky.com/blog/vibe-coding-2025-risks/54584/) that 20% of vibe-coded applications contain serious vulnerabilities or configuration errors, including hardcoded API keys and client-side authentication logic.

**Architecturally sensitive changes.** Changes that affect system structure, module boundaries, or data models require understanding of how components interact. Vibe coding optimizes for local correctness while potentially introducing structural drift.

**Novel functionality.** When the task requires discovering APIs, designing data structures, or solving problems the agent has not seen frequently in training data, vibe coding produces output that appears correct but may use wrong abstractions or deprecated patterns.

**Review at scale.** AI generates thousands of lines per session. [CodeRabbit found](https://www.coderabbit.ai/blog/code-review-best-practices-for-vibe-coding) that AI-generated code is "notoriously verbose" with pointless loops and imaginary functions, and large PRs defeat meaningful review. PRs of 10,000+ lines guarantee reviewers miss critical issues.

**Productivity expectations.** A [METR randomized controlled trial](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/) found experienced developers were 19% slower with AI tools despite predicting they would be 24% faster. Rejected AI generations still consume review time with no output to show for it.

**Safeguard removal.** When AI output triggers linters or tests, the path of least resistance is removing the safeguard rather than fixing the code. The guardrail correctly identified dangerous code; the response was to delete the guardrail.

**Maintainer burden.** [Open source projects report](https://www.infoq.com/news/2026/02/ai-floods-close-projects/) being flooded with AI-generated contributions — Daniel Stenberg shut down cURL's bug bounty after AI submissions reached 20% with only 5% validity. The cost of receiving contributions stays constant while the cost of creating them collapses.

## Required Safety Practices

If you choose to vibe code, these practices limit the blast radius of wrong output:

### Frequent Git Staging Outside the Session

Stage and commit at every working milestone from a separate terminal — not through the agent. Agents staging version control operations can introduce subtle problems: staging incomplete work, committing with misleading messages, or triggering automation that interferes with the current task ([Source: ClaudeLog](https://claudelog.com/mechanics/vibe-coding)).

```bash
# In a separate terminal, not through the agent
git add -p  # Review what you are staging
git commit -m "working: endpoint returns correct response format"
```

These commits are rollback points. When the agent takes the code in a wrong direction — which it will — you reset to the last known-good state and re-prompt.

### Incremental Verification

Run the output after each significant change. Do not let the agent make five changes before you check whether the first one works. Catching errors early prevents the agent from building on broken assumptions.

### Maintain Domain Knowledge

Vibe coding does not mean abandoning understanding of the problem domain. You still need enough knowledge to evaluate whether the output is correct and to steer the agent toward appropriate APIs and patterns. Without domain knowledge, you cannot distinguish output that works from output that appears to work.

### Set Scope Boundaries

Define what the agent should and should not touch. Vibe coding an entire application is an anti-pattern. Vibe coding a single utility function within a well-understood system is a reasonable time optimization.

## Vibe Coding vs. Structured Workflows

| Dimension | Vibe coding | Plan-first workflow |
|-----------|------------|-------------------|
| **Developer role** | Outcome evaluator | Co-designer |
| **Implementation understanding** | Minimal | Full |
| **Iteration cost** | Low (discard and retry) | Higher (plan revisions) |
| **Appropriate for** | Throwaway, low-risk, permutation work | Production, multi-file, architectural changes |
| **Risk model** | Accept wrong output, fix later | Prevent wrong output upfront |

Both approaches have a place. The mistake is using vibe coding's speed as justification for skipping planning on tasks that require it.

## Example

A developer needs a CLI tool to convert CSV files to JSON. This is throwaway tooling — the right context for vibe coding.

**Prompt to agent:**

```
Build a CLI tool that reads a CSV file and outputs JSON. Support --pretty for formatted output and --filter for column selection.
```

The agent produces `csv2json.py`. The developer does not read the implementation — they test it:

```bash
# Test with real data
python csv2json.py data/users.csv --pretty --filter name,email
```

Output looks correct. Next iteration:

```
Add --output to write to a file instead of stdout. Also handle missing columns gracefully.
```

The agent modifies the script. The developer tests again, stages the working version from a separate terminal:

```bash
# Separate terminal — not through the agent
git add csv2json.py
git commit -m "working: csv2json with filter and file output"
```

The developer then asks for stdin support. The agent breaks the existing file output. Because the previous version was committed, recovery is immediate:

```bash
git diff csv2json.py   # See what broke
git checkout csv2json.py  # Reset to last known-good
```

Re-prompt with a more constrained request: "Add stdin support without changing the existing --output flag behavior."

The entire session takes 10 minutes. The developer never read a diff. The tool works. If it breaks in six months, they will rewrite it from scratch in another 10-minute session — that is the expected lifecycle for vibe-coded output.

## Key Takeaways

- Vibe coding delegates implementation entirely to the agent; the developer evaluates outcomes without reading diffs or tracking implementation details
- Appropriate for prototyping, bash scripts, permutation tasks, and exploratory work where wrong output is cheap to discard
- Inappropriate for production systems, security-critical code, and architecturally sensitive changes where black-box code creates compounding risk
- Stage and commit from a separate terminal at every working milestone — do not delegate version control to the agent
- Verify incrementally and maintain enough domain knowledge to distinguish correct output from output that merely appears to work

## Related

- [The Plan-First Loop: Design Before Code](plan-first-loop.md)
- [Trust Without Verify](../anti-patterns/trust-without-verify.md)
- [CLI Scripts as Agent Tools](../tool-engineering/cli-scripts-as-agent-tools.md)
- [Escape Hatches: Unsticking Stuck Agents](escape-hatches.md)
- [Incremental Verification](../verification/incremental-verification.md)
- [Permutation Frameworks](permutation-frameworks.md)
- [Failure-Driven Iteration](failure-driven-iteration.md)
- [Human-in-the-Loop](human-in-the-loop.md)
- [Verification-Centric Development](verification-centric-development.md)
- [Eval-Driven Development](eval-driven-development.md)
- [The AI Development Maturity Model](ai-development-maturity-model.md)
