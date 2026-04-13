---
title: "Engineering: Tools, Review, Verification, Security, and Observability"
description: "Engineering disciplines for production agent systems — tool design, code review, verification, security hardening, and observability."
tags:
  - engineering
  - tool-design
  - security
  - observability
  - verification
  - code-review
---

# Engineering

> The engineering disciplines that turn agent prototypes into production systems — tool design, code review, verification, security hardening, and observability.

The engineering disciplines that make agent systems production-ready — from tool design and code review to verification, security, and observability.

## [Tool Engineering](tool-engineering/index.md)

Design, implement, and optimize the tools agents use — MCP servers, CLI wrappers, [hook lifecycles](tool-engineering/hooks-lifecycle-events.md), skill authoring, and token-efficient tool interfaces.

## [Code Review](code-review/index.md)

Patterns for reviewing agent-generated code — tiered review strategies, diff-based approaches, committee patterns, and [balancing PR volume against value](code-review/agent-pr-volume-vs-value.md).

## [Verification](verification/index.md)

Testing and validation strategies for agent output — TDD workflows, pass@k metrics, deterministic guardrails, behavioral testing, and trajectory analysis.

## [Security](security/index.md)

Hardening agent systems against prompt injection, credential leakage, tool-invocation attacks, and other threats — defense-in-depth, sandboxing, and permission gating.

## [Observability](observability/index.md)

Monitoring and debugging agent behavior — OpenTelemetry integration, trajectory logging, circuit breakers, loop detection, and making observability legible to agents themselves.
