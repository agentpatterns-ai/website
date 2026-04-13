---
title: "Persona-as-Code: Defining Agent Roles as Structured Docs"
description: "Encode each agent's domain, responsibilities, constraints, output artifacts, and scope exclusions in a Markdown file — explicit, auditable, and composable."
tags:
  - agent-design
  - workflow
  - tool-agnostic
  - instructions
---

# Persona-as-Code: Defining Agent Roles as Structured Documents

> Encode each agent's domain, responsibilities, constraints, output artifacts, and scope exclusions as a Markdown file so roles are explicit, auditable, and composable.

Persona-as-Code is a design practice where each agent's role is expressed as a structured Markdown file — domain, responsibilities, output artifacts, constraints, and scope exclusions — rather than buried inside a monolithic system prompt. The file is both the agent's operating specification and the contract governing handoffs to other agents.

## The Problem with Implicit Roles

When an agent's role is embedded in a single monolithic system prompt alongside tool definitions, workflow steps, and project context, the role boundary becomes invisible. Two things happen:

- Agents overstep — the "Developer" agent quietly makes architectural decisions that belong to the Architect
- Agents conflict — two agents legitimately claim the same change from different angles, and the merge step has no principle to resolve it

Role confusion is not a model failure. It is a specification failure. The role was never made explicit.

## What Persona-as-Code Means

A persona is a self-contained Markdown file that encodes one agent's identity. Each file answers four questions:

1. **Domain** — what area of expertise does this agent hold?
2. **Responsibilities** — what outputs does this agent produce?
3. **Constraints** — what is this agent not allowed to do?
4. **Scope exclusions** — which roles own adjacent decisions?

The file is the agent's system prompt. It is also the contract between agents. When a handoff happens, the receiving agent knows its scope from the file; the sending agent knows what it should not have touched.

## Anatomy of a Persona File

```markdown
# Product Manager

## Domain
Product definition and requirements. You own the problem statement, not the solution.

## Responsibilities
- Write and maintain the PRD (one-page maximum)
- Define acceptance criteria for each user story
- Prioritize features by user value and delivery risk

## Output Artifacts
- `docs/prd.md` — product requirements document
- `docs/stories/` — one Markdown file per user story

## Constraints
- Do not specify implementation details or technology choices
- Do not estimate effort — that belongs to the Developer persona

## Scope Exclusions
- Architecture decisions → Architect persona
- Sprint sequencing → Scrum Master persona
- Test criteria beyond acceptance criteria → QA persona
```

The scope exclusions are as important as the responsibilities. They prevent the PM from drifting into architecture decisions during a long session where context degrades and role boundaries blur.

## Artifact-Driven Handoffs

Persona-as-code works because agents hand off **artifacts**, not context. Each persona produces versioned Markdown files — PRDs, architecture briefs, user stories — that travel to the next agent in the pipeline. The receiving agent reads the file, not the chat history.

Context evaporates between sessions in multi-agent systems; [artifact-based handoffs prevent this](https://github.com/bmad-code-org/BMAD-METHOD). A chat-based handoff loses fidelity. A file-based handoff is exact.

Git-versioning the artifacts adds auditability. Every human and AI contribution is tracked. Pull requests become the review mechanism for AI-generated specs before they reach implementation.

## Role Boundaries and Conflict Resolution

When two personas could legitimately touch the same artifact, the persona files define priority. Without explicit rules, two agents modifying the same artifact create a merge conflict with no principled resolution; with explicit priority, the spec resolves it. A survey of multi-agent collaboration mechanisms identifies interdependency between role-scoped agents as the primary source of cascade failures in LLM systems — explicit scope exclusions directly address this ([Tran et al., 2025](https://arxiv.org/abs/2501.06322)).

This mirrors the principle behind [Specialized Agent Roles](specialized-agent-roles.md): mutually exclusive scopes prevent redundant overlap. Persona-as-code makes that exclusivity durable across sessions.

## Relationship to Task-Specific Design

Persona-as-code and [task-specific agents](task-specific-vs-role-based-agents.md) address different problems:

| Dimension | Persona-as-Code | Task-Specific Agents |
|-----------|-----------------|----------------------|
| Unit of definition | Role (domain expertise) | Task (bounded operation) |
| Scope | Wide — all tasks within a domain | Narrow — one task, one success criterion |
| Best fit | Long-running project workflows | Discrete automations, CI operations |
| Handoff mechanism | Versioned artifact files | JSON output or tool results |

Personas suit multi-phase project work. Task-specific agents suit discrete automations where success is unambiguous. The patterns compose: a Scrum Master persona can invoke a task-specific story-validator without encoding that in the persona file.

## Example

The [BMAD Method](https://github.com/bmad-code-org/BMAD-METHOD) packages this pattern at scale: 12+ agent personas — PM, Architect, Developer, UX, Scrum Master, QA — each defined as a structured Markdown file with explicit scope exclusions.

A minimal two-persona [content pipeline](../workflows/content-pipeline.md) illustrates the structure:

```markdown
# Researcher persona

## Domain
Source gathering and validity assessment. You produce findings, not content.

## Output Artifacts
- `docs/research/<slug>.md` — structured research notes with sourced claims

## Constraints
- Do not write publishable content
- Do not make editorial decisions about framing

## Scope Exclusions
- Content angle and framing → Author persona
```

```markdown
# Author persona

## Domain
Content drafting from research. You translate findings into publishable pages.

## Input Artifacts
- `docs/research/<slug>.md` — read before writing

## Output Artifacts
- `docs/<category>/<slug>.md` — final page

## Constraints
- Do not gather new sources — treat research notes as the complete input

## Scope Exclusions
- Source validity → Researcher persona
```

Each persona operates within its file. The boundary is enforced by the spec, not by the model.

## When This Backfires

Persona-as-code adds coordination surface area. Three conditions where it is worse than a unified prompt:

1. **Scope boundaries are ambiguous.** If the line between two personas is unclear — both can reasonably claim a decision — explicit exclusions do not resolve the conflict; they just relocate it to a boundary dispute. Role-based systems can show rigidity when task requirements deviate from predefined scope, resulting in disputes or functional deficiencies ([Tran et al., arXiv 2501.06322](https://arxiv.org/abs/2501.06322)).
2. **Single-agent or short-session workflows.** Maintaining separate persona files and artifact handoff conventions adds overhead with no benefit when a single agent handles a bounded task end-to-end. A well-structured system prompt is simpler.
3. **Rapidly changing requirements.** Persona files encode stable role definitions. When the domain or team structure is still evolving, keeping multiple files consistent costs more than the clarity they provide.

## Key Takeaways

- Role confusion is a specification failure, not a model failure — make roles explicit in persona files
- Each persona file defines domain, responsibilities, output artifacts, constraints, and scope exclusions
- Scope exclusions are as important as responsibilities — they prevent drift during long sessions
- Artifact-driven handoffs preserve fidelity across agents and sessions; chat-based handoffs do not
- Git-versioning artifacts creates auditability and enables human review before implementation
- Persona-as-code suits multi-phase project workflows; task-specific agents suit discrete automations

## Related

- [Specialized Agent Roles](specialized-agent-roles.md)
- [Task-Specific vs Role-Based Agents](task-specific-vs-role-based-agents.md)
- [Separation of Knowledge and Execution](separation-of-knowledge-and-execution.md)
- [Agents vs Commands](agents-vs-commands.md)
- [Cognitive Reasoning and Execution Separation](cognitive-reasoning-execution-separation.md)
- [Agent Composition: Chains, Fan-Out, Pipelines, Supervisors](agent-composition-patterns.md)
- [Agent-First Software Design for AI Agent Development](agent-first-software-design.md)
- [Agent Harness: Initializer and Coding Agent](agent-harness.md)
- [Agent Memory Patterns: Learning Across Conversations](agent-memory-patterns.md)
- [GoF Patterns and SOLID as Agent Design Vocabulary Bridge](classical-se-patterns-agent-analogues.md)
- [Event-Driven Agent Routing](event-driven-agent-routing.md)
- [Delegation Decision](delegation-decision.md)
- [Session Initialization Ritual](session-initialization-ritual.md)
- [Sprint Contracts](sprint-contracts.md)
