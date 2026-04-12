---
title: "Task-Specific vs Role-Based Agents: Narrowing Agent Scope"
description: "Build agents for specific tasks rather than generic roles — narrow scope produces more precise output and reduces context confusion."
tags:
  - agent-design
  - tool-agnostic
aliases:
  - Narrow Agent Scope Over Broad Role
  - Specialized Agent Roles (sequential context)
---

# Task-Specific Agents vs Role-Based Agents

> Build agents for specific tasks — "canary upgrade", "PR review" — rather than generic roles — "kubernetes admin", "senior engineer" — because narrow scope produces more precise output.

!!! info "Also known as"

    Narrow Agent Scope Over Broad Role, Specialized Agent Roles (sequential context)

    Scope: **sequential task decomposition** — individual agents for discrete, bounded tasks that run one at a time. For **parallel specialization** — distinct roles for concurrent agents on the same codebase — see [Specialized Agent Roles](specialized-agent-roles.md).

## The Failure Mode of Role-Based Agents

Role-based agents mirror org charts: "DevOps engineer", "frontend developer", "QA analyst". This feels natural because it mirrors how teams are described. But a role is not a task. A "kubernetes admin" handles cluster upgrades, canary deployments, secret rotation, ingress configuration, and incident response — entirely different tasks with different steps, checks, and success criteria.

Combining all of that into one agent produces an agent that is mediocre at many tasks rather than effective at specific ones. The scope is too wide for precise instructions, the context carries irrelevant expertise for any given job, and success criteria are ambiguous.

## Task-Specific Agents

A task-specific agent has a single, bounded job:

- `canary-upgrade`: promotes a canary deployment, runs health checks, rolls back if error rate exceeds threshold
- `pr-reviewer`: reviews diffs for specific categories: type safety, test coverage, security anti-patterns
- `import-blog-post`: fetches a URL, extracts content, creates an issue with source attribution

Each agent knows exactly what it is doing. The steps are explicit. The success criteria are unambiguous. The context contains only what is relevant to this task.

## The Trade-Off

Task-specific design means more agents — one per task rather than one per role. This trade-off suits teams that value precision and independent maintainability:

| Dimension | Role-Based | Task-Specific |
|-----------|------------|---------------|
| Agent count | Low | High |
| Agent size | Large | Small |
| Scope clarity | Vague | Precise |
| Context relevance | Mixed | High |
| Success criteria | Fuzzy | Explicit |
| Reusability | Low (too broad) | High ([skills](separation-of-knowledge-and-execution.md) composable) |
| Maintenance | Touches everything | Touches one task |

Smaller agents are easier to test, easier to update, and easier to replace. A broken `canary-upgrade` agent does not affect `pr-reviewer`. A new deployment strategy requires updating one agent, not refactoring a monolithic role.

## Shared Knowledge Through Skills

The concern with task-specific design is duplication: each agent needs some of the same knowledge (git conventions, coding standards, project context). Shared skills address this.

Common knowledge lives in shared skills that any agent can load. Each task-specific agent loads the skills it needs — only those. The agent definition remains small; the skill carries the shared knowledge.

This is task-specific design at the agent level with shared reuse at the skill level. See [Separation of Knowledge and Execution](separation-of-knowledge-and-execution.md) for the three-layer model.

## Identifying the Right Task Boundary

The right task boundary is where the success criteria are natural and atomic. A task is at the right granularity when you can answer without ambiguity: "did this agent succeed or fail?"

- "Did the canary deploy and pass health checks?" — clear
- "Did the kubernetes admin do a good job?" — unclear

When success is ambiguous, the task boundary is wrong. Split or narrow until success is unambiguous.

## Example

The contrast below shows the same deployment work modelled first as a role-based agent and then split into task-specific agents. The task-specific version has explicit steps and unambiguous success criteria for each unit.

**Role-based (avoid):**

```yaml
# .claude/agents/kubernetes-admin.md
name: kubernetes-admin
description: "Handle all Kubernetes cluster operations: upgrades, canary deployments, secret rotation, ingress changes, and incident response."
tools:
  - kubectl
  - helm
  - gh
  - slack

You are a senior Kubernetes administrator. Handle all cluster operations including
upgrades, canary deployments, secret rotation, ingress changes, and incident response.
```

**Task-specific (prefer):**

```yaml
# .claude/agents/canary-promote.md
name: canary-promote
description: "Promote a canary deployment, run health checks, and roll back automatically if error rate or latency exceeds threshold."
tools:
  - kubectl

Steps:
1. Run `kubectl get canary <name> -n <namespace>` and confirm weight is at target %
2. Check error rate: `kubectl top pods -l app=<name>` — abort if p99 latency > 500ms or error rate > 1%
3. Run `kubectl patch canary <name> -n <namespace> --type merge -p '{"spec":{"weight":100}}'`
4. Wait 60s, re-check error rate
5. If error rate exceeded: `kubectl patch canary <name> -n <namespace> --type merge -p '{"spec":{"weight":0}}'` and report failure

Success: canary weight is 100 and error rate is within threshold for 60s
Failure: any step returns a non-zero exit code, or error rate threshold is breached
```

The `canary-promote` agent knows exactly what it does, what tools it needs, and what success and failure look like. A separate `rotate-secrets` agent handles secret rotation without carrying canary deployment context.

## Key Takeaways

- Scope agents to tasks, not roles — narrow scope produces clearer steps and unambiguous success criteria
- More agents, each smaller and independently maintainable, is a reasonable trade-off for precision
- Test the boundary: if success criteria are ambiguous, the task is too broad

## Related

- [Specialized Agent Roles](specialized-agent-roles.md) — parallel counterpart: assigning distinct specializations to concurrent agents
- [VS Code Agents App: Agent-Native Parallel Task Execution](vscode-agents-parallel-tasks.md) — running multiple task-specific agents simultaneously in a dedicated execution surface
- [Agents vs Commands: Separation of Role and Workflow](agents-vs-commands.md)
- [Progressive Disclosure for Agent Definitions](progressive-disclosure-agents.md)
- [Separation of Knowledge and Execution](separation-of-knowledge-and-execution.md)
- [Cognitive Reasoning vs Execution: A Two-Layer Agent Architecture](cognitive-reasoning-execution-separation.md)
- [Cost-Aware Agent Design](cost-aware-agent-design.md) — applies task-specific framing to balance capability against inference cost
- [Memory Synthesis from Execution Logs](memory-synthesis-execution-logs.md) — task-scoped agents produce cleaner execution logs for memory synthesis
- [The Delegation Decision](delegation-decision.md) — deciding what to delegate complements deciding how to scope the agent
- [Agent Composition Patterns](agent-composition-patterns.md) — structural patterns for combining task-specific agents into workflows
- [Treat Task Scope as a Security Boundary](../security/task-scope-security-boundary.md) — narrow scope reduces prompt injection attack surface, not just context noise
