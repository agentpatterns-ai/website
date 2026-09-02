---
title: "Reading a Coding-Agent Vendor's Security Certificate"
term: "Vendor Certificate Scope Reading"
description: "An agent-security certificate attests organizational controls, product behavior, or both. Read the scope statement to learn which verification work it removes."
tags:
  - testing-verification
  - security
  - human-factors
  - tool-agnostic
  - arxiv
aliases:
  - agent vendor certification review
  - AIUC-1 certificate scope
  - reading an agent security audit
last_reviewed: 2026-08-27
maturity: emerging
---

# Reading a Coding-Agent Vendor's Security Certificate

> A certificate's scope statement says which halves of a vendor's security story an outsider checked. Nothing outside it was looked at.

A coding-agent security certificate is worth reading for its scope statement and little else. The scope names two things you can act on: whether an auditor inspected the vendor's organizational controls, attacked the running product, or did both, and which product surfaces that attack covered. Cursor's AIUC-1 certificate, published 13 August 2026, states both, and describes the standard as one that "combines an audit of organizational controls with adversarial testing of the product itself" ([Cursor, 2026-08-13](https://cursor.com/blog/aiuc-1)).

## What each half attests

A controls audit reads documents, policies, and process evidence. It establishes that a control is written down and operating. It tells you nothing about what the agent does in your terminal. Schellman, "the world's first ANAB-accredited ISO 42001 certification body and the first authorized auditor for AIUC-1", performed that half for Cursor ([Cursor, 2026-08-13](https://cursor.com/blog/aiuc-1)).

Adversarial product testing queries the deployed product and grades what it does. Cursor's testing covered "our key agent surfaces, including the IDE and cloud agents, using a representative enterprise configuration" across two rounds and several thousand scenarios ([Cursor, 2026-08-13](https://cursor.com/blog/aiuc-1)). Read that sentence twice. An IDE-only pass would carry nothing about a cloud agent, and a representative enterprise configuration is not yours.

## Five questions to put to a certificate

| Question | What the answer changes | Cursor's AIUC-1 answer |
|---|---|---|
| Which half? | Controls-only leaves runtime behavior untested. | Both halves |
| Which surfaces? | Every unlisted surface is unmeasured. | IDE and cloud agents |
| Which configuration? | Your wiring decides your exposure. | A representative enterprise configuration |
| How recently? | A single pass ages as the product ships. | "at least quarterly, with a full audit each year" |
| Which controls? | An untraceable claim is one you cannot check. | Rules, hooks, Auto-review, model-level safeguards |

Every answer in the third column comes from one vendor post ([Cursor, 2026-08-13](https://cursor.com/blog/aiuc-1)). If a vendor cannot answer the five in writing, treat what you have as a claim.

## Why it works

Audit strength is a function of the access the auditor held, and the two halves grant different access. Casper et al. separate three levels. Black-box access means querying the system and observing its outputs. White-box adds weights, activations, and gradients; outside-the-box adds training methodology, code, and deployment details. They conclude that transparency about the access and methods an auditor used is "necessary to properly interpret audit results" ([Casper et al., 2024](https://arxiv.org/abs/2401.14446v3)). A controls audit is documentary. Adversarial product testing is black-box. Neither reaches model internals, so the scope statement is the only part of the certificate that tells you which inference you are entitled to draw.

## When this backfires

- No procurement gate exists. A two-person team adopting the tool regardless gets no decision from the reading.
- Your threat model is not the one that set the bar. AIUC-1 "was developed with input from more than 100 Fortune 500 CISOs and risk leaders", and for coding agents its requirements "extend to areas such as secrets protection, secure code generation, MCP security, and agent identity and permissions" ([Cursor, 2026-08-13](https://cursor.com/blog/aiuc-1)). That is a bar set by enterprise buyers for the risks they carry. A project whose real exposure is its dependency supply chain gets a careful answer to a different question, and treating the pass as your answer swaps their threat model in for yours.
- A pass gets read as exploit absence. Xie et al. red-teamed six coding assistants through tool invocation and obtained remote code execution on every tested agent-model pair. Their attack succeeded on 19 of 25 agent-LLM pairs, "achieving leakage on every agent using Claude and Grok backends" ([Xie et al., 2026](https://arxiv.org/abs/2509.05755v6)). Red teaming has also narrowed toward model-level flaws and away from the system around them ([Majumdar et al., 2025](https://arxiv.org/abs/2507.05538v2)).
- Your wiring differs from the tested wiring. Across 3,250 attack scenarios, function calling recorded 73.5% attack success against 62.59% for MCP ([Gasmi et al., 2025](https://arxiv.org/abs/2507.06323v1)). Architecture moves the number, so a result under one configuration does not transfer to another.

The behavioral half carries a ceiling of its own. Seth and Sankarapu call the divergence between required and achievable verification access the audit gap, and call a safety claim whose evidential structure does not support it fragile assurance ([Seth & Sankarapu, 2026](https://arxiv.org/abs/2605.15164v1)). So read a certificate as a floor on process quality. Your own testing still decides what you know about your repository.

## Key Takeaways

- Read the scope statement before anything else. It bounds what you may infer from the rest of the artifact.
- A controls audit and adversarial product testing are separate purchases. Ask which one you got.
- Cadence decides staleness. AIUC-1 requires quarterly testing with a full annual audit ([Cursor, 2026-08-13](https://cursor.com/blog/aiuc-1)).
- Trace each named safeguard to a control you can configure yourself, then verify it in your own repository.
- A certificate raises the floor on process. It does not establish that exploits are absent.

## Related

- [Enforced Versus Advisory Controls in LLM-Native IDEs](../security/enforced-versus-advisory-controls.md) — sort the safeguards a certificate names by where they get evaluated
- [Task Completion as Tool Certification (Silent Tool Rot)](../patterns/anti-patterns/task-completion-as-tool-certification.md) — the same inference error one level down, at the tool a session builds
- [Benchmark-Driven Tool Selection for Code Generation](benchmark-driven-tool-selection.md) — what to measure yourself once the certificate is read
- [Policy-Graded Evaluation of Coding Agents](policy-graded-agent-evaluation.md) — score an agent at each enforced security tier instead of once
- [Lethal Trifecta Threat Model](../security/lethal-trifecta-threat-model.md) — the exposure a coding agent brings before any vendor control applies
