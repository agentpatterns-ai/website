---
title: "Check Context-File Dependency Rules Against the Code"
term: "Aspirational Dependency Rule"
description: "In a 3,346-project study, 18% of checkable dependency rules in AGENTS.md-style files were broken the day they were written. Check each rule then; mark goals."
tags:
  - instructions
  - tool-agnostic
  - arxiv
  - testing-verification
aliases:
  - aspirational architecture rules
  - target-architecture rules in context files
  - day-one broken dependency rules
last_reviewed: 2026-11-24
maturity: emerging
---

# Check Context-File Dependency Rules Against the Code

> Existing code often breaks context-file dependency rules on the day they are written, so check each rule then and mark target rules.

An aspirational dependency rule is a context-file rule about what may import what that the code already breaks when the rule is written. In a study of 184 checkable rules from 3,346 open-source projects, "33 of 184 (18%) were confirmed broken on the day they were written, usually by older code, and nearly all stayed broken" ([Ghimire and Damian, 2026](https://arxiv.org/abs/2611.29916v1)). Run each rule against the code when you write it. If it fails, fix the code or rewrite the rule as a target with its exceptions.

## When this applies

The advice holds under two conditions.

- The rule can be checked. It names folders, packages, or libraries an import checker can resolve. About half the rule sentences in the study could not be checked, "for example because they name parts that cannot be mapped to folders" ([§6](https://arxiv.org/abs/2611.29916v1)).
- No linter already carries the rule with its own exception list. If `no-restricted-imports` or an import linter enforces it in CI, the linter is the source of truth and the prose is a pointer to it.

The evidence for the problem is strong. The evidence for the remedy is weaker: marking target rules and checking at write time are the authors' recommendations, and the paper leaves testing what agents do when a rule is already broken to future work ([§7](https://arxiv.org/abs/2611.29916v1)).

## Path claims and dependency rules fail differently

The study also checked path claims, which name folders and files ([Ghimire and Damian, 2026](https://arxiv.org/abs/2611.29916v1)).

| Claim type | Count | Error finding |
|---|---|---|
| Path claims | 41,090 | About 5% point to missing paths; an estimated 2.2% are real errors, against 3.5% for READMEs |
| Dependency rules | 184 | 18% confirmed broken on the day written; of the 51 rules the checker flagged as broken when written, 50 were still broken at the snapshot |

Path claims mostly keep up with the code. "In 61% of fixes, the claim changed at the same time as the code, which in practice means in the same commit" ([§4.2](https://arxiv.org/abs/2611.29916v1)). Dependency rules rarely decay. Only 4 rules held when written and broke later ([§4.3](https://arxiv.org/abs/2611.29916v1)). The problem is the rule's starting state.

The breaking code was usually there first: "In 26 of the 33 confirmed cases, every rule-breaking import was already in the code before the project’s first context file existed" ([§4.3](https://arxiv.org/abs/2611.29916v1)). Library rules broke from the start more often than rules between internal modules: 14 of 58 (24%) against 19 of 126 (15%), counting confirmed cases ([§4.3](https://arxiv.org/abs/2611.29916v1)).

The 18% figure is a floor. The authors call it "likely a lower bound", because in a sample of 40 rules their checker passed, 5 had a break it missed ([§4.3](https://arxiv.org/abs/2611.29916v1)).

## What to do

1. Run each new dependency rule against the code before you commit the context file. An import grep works for one rule. For many, use an import linter, or a tool like [ContextCov](https://arxiv.org/abs/2603.00822v2), which the authors name as one that fits this need ([§5.6](https://arxiv.org/abs/2611.29916v1)).
2. If the rule holds, keep it as a fact. If it matters, enforce it with a linter. The study found projects that already write "enforced by ESLint no-restricted-imports" beside the rule ([§5.6](https://arxiv.org/abs/2611.29916v1)).
3. If the rule fails, decide which side is wrong. Fix the code, or rewrite the rule as a target. The authors suggest a target rule should "state the target, the current exceptions, and the direction of change" ([§5.2](https://arxiv.org/abs/2611.29916v1)).
4. Name exceptions by scope, not by import. One Go rule in the study had 107 breaking imports ([Table 8](https://arxiv.org/abs/2611.29916v1)). A folder scope costs one line. One file in the study marks `pkg/og/` as "legacy code being phased out" ([§4.3](https://arxiv.org/abs/2611.29916v1)).
5. Re-run the check whenever the context file changes. The authors say a rule checker "should also run whenever a context file changes" and "must support known exceptions and migration states" ([§5.6](https://arxiv.org/abs/2611.29916v1)).

## Example

The study reports a rule from a TypeScript project, shortened in its Table 8: "Do not import MUI; we are actively removing it". The code had 132 MUI imports when the rule was written and 74 at the snapshot ([Ghimire and Damian, 2026](https://arxiv.org/abs/2611.29916v1)). A version of the rule that applies step 3 reads:

```markdown
## Dependency rules
- Target: no new imports of MUI (`@mui/*`). New UI code uses the in-house components in `src/ui/`.
- Current exceptions: existing screens under `src/legacy/` still import MUI.
- Direction: we remove MUI screen by screen. Do not copy MUI imports from legacy screens.
```

The folder names in this version are placeholders for your own layout, not the study project's.

## Why it works

The agent re-reads the context file every session and is built to treat it as true ([§1](https://arxiv.org/abs/2611.29916v1)). It also learns from the code it reads. For a rule the code breaks, the authors put it this way: "An agent sees two conflicting signals: the rule in its instructions, and many counter-examples in the code it reads" ([§5.1](https://arxiv.org/abs/2611.29916v1)). They suggest one reason the rules stay broken: rules are rarely checked, "so nothing flags a rule that is broken on the day it is written" ([§5.1](https://arxiv.org/abs/2611.29916v1)). The paper frames this with the architecture distinction between what should be (prescriptive) and what is (descriptive), and notes that "Context files mix both in one list" ([§5.2](https://arxiv.org/abs/2611.29916v1)). A write-time check exposes the gap while the author still knows the intent. A marked target rule tells the agent which signal describes new code.

## When this backfires

- New breaks were already rare. Agent-assisted commits broke rules at 0.29% against 0.16% for other commits, from 14 confirmed breaks, which the authors call "an early signal, not evidence of a difference or of its absence" ([Ghimire and Damian, 2026](https://arxiv.org/abs/2611.29916v1)). An unmarked target rule may already steer new code well enough.
- A linter already encodes the exceptions. Copying them into prose duplicates config, and the two copies can drift.
- Exception lists bloat always-loaded context. Enumerating 107 imports costs tokens every session. Keep exceptions at folder scope, or leave them in the linter config.
- A blanket instruction to follow existing code undoes the target. [Code precedence over stale instruction files](code-precedence-over-instruction-files.md) tells the agent to copy the code when docs and code disagree, which for a target rule means copying the breaking imports. Scope that instruction, or use a [written priority rule](written-priority-rules-for-migrations.md) for the migration.
- The sample is open source over a short window, a median of 67 days per file ([§6](https://arxiv.org/abs/2611.29916v1)). The authors say results may differ for industrial code, and more claims may go stale over longer periods.

## Key Takeaways

- Spend checking effort on dependency rules first. About 98% of path claims pointed to real code; 18% of rules were broken on day one.
- The breaking code usually predates the rule, so a write-time check finds it.
- A failed check means fix the code or mark the rule as a target with scoped exceptions and a direction.
- The harm to agents and the benefit of marking are untested. Weigh the cost of the exception text.

## Related

- [Stale AI Configuration Artifacts (Context Rot)](../patterns/anti-patterns/stale-ai-configuration-artifacts.md) — path and code-element drift, the failure that path claims show
- [Corroborated Compliance Checks for Agent Context Files](corroborated-compliance-checks-from-context-files.md) — generating one executable check per context-file rule
- [Written Priority Rules for Coding-Agent Migrations](written-priority-rules-for-migrations.md) — telling the agent a target convention overrides existing code
- [Code Precedence Over Stale Instruction Files](code-precedence-over-instruction-files.md) — the opposite instruction, and the case where it conflicts with a target rule
- [Enforce the Rules Your Code Cannot Show](per-rule-enforcement-budget.md) — budgeting enforcement by whether the diff shows compliance
