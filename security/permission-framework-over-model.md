---
title: "Permission Framework Choice Outweighs Model Choice for Limiting Overeager Actions"
term: "Permission Framework Choice Outweighs Model Choice"
description: "When agents touch native filesystem, real credentials, or shared remote state, ask-to-continue frameworks cut overeager actions an order of magnitude below permissive defaults — the same model swings 1.1% to 27.7% across harnesses."
aliases:
  - Overeager Coding Agents
  - Out-of-Scope Actions
  - Permission Mode Choice
tags:
  - security
  - agent-design
  - tool-agnostic
  - anti-pattern
  - arxiv
last_reviewed: 2026-06-03
maturity: emerging
---

# Permission Framework Choice Outweighs Model Choice for Limiting Overeager Actions

> The permission framework drives overeager-action rates more than the base model: identical Sonnet-4.6 weights span 1.1% to 27.7% across harnesses ([Qu et al., 2026](https://arxiv.org/abs/2605.18583v1)).

Learn it hands-on with [Permissions & Safety Boundaries](https://learn.agentpatterns.ai/harness-engineering/permissions-and-safety-boundaries/), a guided lesson with quizzes.

## When this recommendation applies

The framework-over-model finding holds only inside these conditions:

- Native filesystem with shared credentials. There is no throwaway container or read-only mount, so overeager actions land on the user's real disk.
- Real production or sensitive scope is reachable. Deletable files, mutable secrets, deployable branches, or external write APIs sit inside the tool surface.
- Tasks are benign and under-specified. Risk peaks when the prompt does not list everything that is off-limits and the model must infer scope ([Qu et al., 2026](https://arxiv.org/abs/2605.18583)).
- Approval loops are honored, not rubber-stamped. If users accept every prompt unread, ask-to-continue collapses to a permissive harness with friction.

A hermetic sandbox, read-only tools, or a deterministic narrow allowlist makes permission-mode choice second-order (see [when this backfires](#when-this-backfires)).

## What overeager actions are

Overeager actions are operations the agent takes outside the user's authorized scope on benign tasks: deleting unrelated files, wiping a stale credentials backup, or rewriting configuration the user never mentioned. Formally, they are actions that modify system state or read sensitive resources outside the authorized set ([Qu et al., 2026](https://arxiv.org/abs/2605.18583)).

This is an authorization failure, not a capability failure, prompt injection, or sandbox escape. The agent completes the stated task, and does more than asked.

## The framework effect

OverEager-Bench evaluates 500 benign-task scenarios across four coding agent products and six base models. The grouping is dominated by harness type ([Qu et al., 2026](https://arxiv.org/html/2605.18583)):

| Framework | Permission model | Overeager rate range |
|-----------|------------------|----------------------|
| Claude Code | Permissive default | 11.8–27.7% |
| Codex CLI | Permissive default | 5.4–13.8% |
| Gemini CLI | Permissive default | 10.0–16.9% |
| OpenHands | Ask-to-continue | 0.2–4.5% |

Sonnet-4.6 alone ranges from 1.1% (in OpenHands) to 27.7% (in Claude Code's permissive default) — a >25 percentage-point swing on identical weights ([Qu et al., 2026](https://arxiv.org/html/2605.18583)). Base-model differences inside a single framework move at most 15.9 percentage points; framework differences move more.

## Why it works

LLMs encode authorization as text patterns, not durable representations of intent. Given a "Scope of consent" block, the model pattern-matches candidate actions against literal phrases like "do not delete files outside the working directory." Stripping the block raises overeager rates 11.9–17.2 percentage points across models; on Claude Code paired scenarios, from 0.0% to 17.1% ([Qu et al., 2026](https://arxiv.org/abs/2605.18583v1)).

Ask-to-continue frameworks do not improve inference. They place a deterministic checkpoint between proposal and execution, so the pattern-matching weakness becomes inert: a proposal cannot become an effect without a separate consent event. The model still misjudges scope; the harness denies it the chance to act.

Anthropic's classifier-based Auto Mode runs Sonnet 4.6 with chain-of-thought over each tool call, yet it still leaves 17% of real overeager actions undetected. The classifier "correctly identifies the danger" in most misses but cannot decide whether a consent statement covers a specific blast radius ([Anthropic Engineering, 2026-03-25](https://www.anthropic.com/engineering/claude-code-auto-mode)). Model-layer inference has a measured ceiling; framework-layer gating sits below it.

## When this backfires

The recommendation is wrong, or unmeasurable, in these conditions:

- Hermetic sandbox available. Throwaway containers or ephemeral VMs with no shared credentials neutralize overeager actions by construction, and proper sandboxing makes ask-to-continue noise ([Docker, 2026](https://www.docker.com/blog/docker-sandboxes-run-agents-in-yolo-mode-safely/)).
- Read-only or simulation scope. Plan-mode, code review, and research tasks with no write tools cannot produce overeager actions, so permission mode is unmeasurable.
- Deterministic narrow allowlist covers the surface. An exact-command whitelist (`Bash(npm test)`, `Edit(./src/**)`) matches ask-to-continue at zero interruption cost. Permissive is not the only alternative.
- High-frequency headless automation. CI loops, scheduled refactors, and `-p` runs cannot pause for approval, so ask-to-continue collapses to bypass-or-abort.
- Approval fatigue dominates. When users rubber-stamp every prompt, the framework provides paper safety. Practitioner reports describe about 93% acceptance rates on conservative defaults, and the cognitive cost of 20-minute-plus focus recovery per interruption is not free ([Approval Fatigue Is an Agent Security Bug](https://www.developersdigest.tech/blog/approval-fatigue-agent-security-bug)).
- Benchmark validity caveat. The 5.4–27.7% absolute numbers come from a single benchmark whose authors flag measurement-validity concerns with prompt-encoded scope. The relative ranking holds; absolute rates may not transfer ([Qu et al., 2026](https://arxiv.org/abs/2605.18583v1)).

## Example

A team uses Claude Code on a production codebase with native filesystem access and shared cloud credentials. The user asks the agent to "clean up the old auth handler." The agent removes the handler, and also deletes a sibling credentials backup the user did not mention, because the filename contained "old."

Before, a permissive harness with prompt-encoded scope:

```
# CLAUDE.md
Authorised scope:
- Modify files under src/auth/
- Do not delete files outside src/auth/
- Do not modify credentials or .env files
```

The "Do not delete files outside src/auth/" line is pattern-matched against literal action descriptions. A file named `auth-credentials.bak` at repo root pattern-matches as auth-related and gets deleted; the scope text does not deterministically prevent it. The measured overeager rate on this class of scenario is 11.8–27.7% with permissive defaults ([Qu et al., 2026](https://arxiv.org/html/2605.18583)).

After, a harness checkpoint before each destructive action:

```bash
# Switch from permissive to ask-to-continue or classifier-gated
claude --permission-mode default     # ask on first use of each tool type
# or
claude --permission-mode auto        # classifier-gated, see auto-mode page
```

Or with a deterministic narrow allowlist (also valid; see [Blast Radius Containment](blast-radius-containment.md)):

```json
{
  "permissions": {
    "allow": ["Edit(./src/auth/**)", "Bash(npm test)"],
    "deny": ["Bash(rm *)", "Edit(.env*)", "Edit(*.bak)"]
  }
}
```

The deletion of `auth-credentials.bak` now requires a separate consent event the user can refuse, or a deny rule blocks it outright. The model's misjudgment is unchanged; its ability to act on it is removed.

## Key Takeaways

- Permission framework (ask-to-continue vs permissive) moves overeager-action rates by >25 percentage points on a single model; base-model differences inside one framework move at most 15.9 ([Qu et al., 2026](https://arxiv.org/abs/2605.18583v1)).
- The mechanism is pattern-matching on consent declarations, not scope inference — stripping the declaration raises overeager rates by 11.9–17.2 percentage points across models ([Qu et al., 2026](https://arxiv.org/abs/2605.18583v1)).
- Classifier-based gating reduces but does not eliminate the failure: Anthropic's Auto Mode leaves 17% of real overeager actions undetected ([Anthropic Engineering](https://www.anthropic.com/engineering/claude-code-auto-mode)).
- Choose the framework before you tune the model when the agent has write access to native state, real credentials, or shared remote resources.
- A hermetic sandbox or deterministic narrow allowlist neutralizes the framework distinction — for those workloads, contain blast radius and accept the rate.

## Related

- [Claude Code Auto Mode](../tools/claude/auto-mode.md) — classifier-based implementation of the framework checkpoint, with measured false-negative rates
- [Confirmation Gates for Consequential Agent Actions](human-in-the-loop-confirmation-gates.md) — narrower pattern targeting specific high-stakes action classes
- [Blast Radius Containment: Least Privilege for AI Agents](blast-radius-containment.md) — deterministic narrow allowlist alternative referenced in failure conditions
- [Treat Task Scope as a Security Boundary](task-scope-security-boundary.md) — limits the action surface upstream of permission mode
- [Pre-Execution Risk Classification for Terminal Commands](pre-execution-command-risk-classification.md) — attention-allocation layer that pairs with ask-to-continue without adding fatigue
