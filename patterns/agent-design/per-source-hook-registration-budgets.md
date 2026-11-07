---
title: "Per-Source Hook Registration Budgets"
term: "Per-Source Hook Registration Budget"
description: "Claude Code caps skill hook registrations by source. Count hooks and matcher characters separately, and diagnose skills whose hooks exceed the session limits."
tags:
  - pattern
  - agent-design
  - hooks
  - skills
  - claude
aliases:
  - per-source hook budget
  - skill hook registration limit
  - per-source registration allowance
applies_to: "claude-code@2.x"
last_reviewed: 2026-11-06
maturity: emerging
status: current
---

# Per-Source Hook Registration Budgets

> Per-source hook registration budgets limit each source separately; Claude Code counts both skill hooks and their matcher characters within each session.

A per-source budget assigns each extension source its own registration limit. Claude Code 2.1.304 introduced ceilings of 1,024 skill hooks and 16,384 matcher characters per source per session ([changelog](https://code.claude.com/docs/en/changelog#2-1-304)).

The project, personal skills folder, and each plugin are separate sources. Skills within one source share its allowance. Each hook charges its matcher text separately, including hooks under the same matcher ([hook limits](https://code.claude.com/docs/en/hooks#limits-on-skill-hooks)).

## What the partition controls

One source's registrations do not consume another source's documented allowance. This separates registration accounting; it does not establish a total session limit or a bound on hook execution time. That distinction follows from the per-source limits ([changelog](https://code.claude.com/docs/en/changelog#2-1-304)).

AWS describes per-tenant caps on concurrent inference calls as a comparable isolation design ([tenant-aware performance isolation](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentperf07-bp02.html)). This comparison makes no claim about how Claude Code schedules hook execution.

## When hooks disappear

A skill past its source's limit runs without its frontmatter hooks. Check `/hooks`, then reproduce the invocation order with `claude --debug`. Search for `registers none of its hooks`. Plugin-only policy and invalid frontmatter are alternative causes to investigate ([diagnosis procedure](https://code.claude.com/docs/en/hooks#limits-on-skill-hooks)).

Skill hooks normally persist across later turns. `once: true` removes a hook after its first successful run. The documentation does not promise that removal refunds registration allowance ([hook lifetime](https://code.claude.com/docs/en/hooks#hooks-in-skills-and-agents)). Keep that distinction when estimating a session's budget.

A security check that never registers cannot gate a call. Verify registration before relying on a skill's hook, and reduce hooks or matcher length when the limit is reached ([hook limits](https://code.claude.com/docs/en/hooks#limits-on-skill-hooks)).

## Example

The documented `secure-operations` skill uses a `Bash` matcher with one command hook ([skill hook example](https://code.claude.com/docs/en/hooks#hooks-in-skills-and-agents)). Its matcher contributes 4 characters to the accounting. The two ceilings cross at an average of 16 characters per registered hook:

```text
16,384 matcher characters / 1,024 hooks = 16 characters per hook
```

This is arithmetic from the published limits, not a measured performance threshold. Longer average matchers reach the character ceiling before the hook-count ceiling ([release limits](https://code.claude.com/docs/en/changelog#2-1-304)).

## Key Takeaways

- Count matcher text once per hook when estimating source usage.
- Preserve invocation order when reproducing a missing hook; the session totals build up across skills.
- Verify that a required check registered before treating skill invocation as protected work.

## Related

- [Per-Surface Hook Matchers for Shell-Starting Tools](shell-surface-hook-matcher-coverage.md) — the other way a matcher string decides coverage
- [Refilling Tool Budgets: Rationing by Rate, Not Session Cap](refilling-tool-budgets.md) — the alternative to a hard per-session ceiling, and the visibility bill a refill rate creates
- [Designing Agent Plugins to Survive Co-Installation](plugin-co-installation-safety.md) — contention between installed plugins over a different shared resource, the exported capability name
- [Three Skill Disclosure Decisions to Move Off the Model](skill-disclosure-controller.md) — why model-chosen skill invocation order is a design input rather than an accident
- [Claude Code Hooks: Deterministic Lifecycle Automation](../../tools/claude/hooks-lifecycle.md) — the matcher and frontmatter syntax these budgets are charged against
