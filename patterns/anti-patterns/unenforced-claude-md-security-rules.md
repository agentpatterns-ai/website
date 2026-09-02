---
title: "Assuming a CLAUDE.md Security Rule Is Enforced"
term: "Unenforced Security Rule"
description: "Under the strictest matching standard, 4.4% of security rules across 481 public CLAUDE.md files had a matching built-in Claude Code control. Sort each rule by what could enforce it."
tags:
  - anti-pattern
  - security
  - instructions
  - claude
  - arxiv
aliases:
  - unenforced security rule
  - CLAUDE.md security rule coverage gap
  - do not is not deny
last_reviewed: 2026-08-28
maturity: emerging
---

# Assuming a CLAUDE.md Security Rule Is Enforced

> A security rule in CLAUDE.md is an instruction the model interprets, and rarely one a built-in control enforces.

Write "never commit secrets" into CLAUDE.md and the file accepts it. Write `Read(./.env)` into the `permissions.deny` array and the runtime blocks the read. Both express one security goal, both sit in plain text in the same repository, and nothing reports which of the two you have. Ting Yan measured how often the second backs the first across 481 public CLAUDE.md files. Under the strictest standard, 4.4% of security rules had a matching built-in control, with a 95% confidence interval of 2.6 to 6.7% ([arXiv:2608.23550v1](https://arxiv.org/abs/2608.23550v1)).

Two conditions bound that number, and both cut against the alarming reading. Hooks sit outside the paper's control set by construction. A rule that does map to a deny entry is still not a boundary. Treat the finding as a prompt to sort your rules, not as a score on your file.

## What the measurement covers

Yan keyed a parser on rule words ("must", "never", "do not") to pull 4,661 candidate segments, of which 870 were security-related, and had Claude Sonnet 5 judge each against a frozen list of Claude Code controls. Two security practitioners relabeled a 180-segment sample blind, agreeing 96.5% of the time (kappa 0.89).

One limit rides on every figure below: the trigger-word extractor caught an estimated 66.3% of a file's security rules, so the rates describe only what it retrieved.

The headline moves with the matching standard rather than with sampling error:

| Standard | Coverage | 95% CI |
|---|---|---|
| Classifier over the full corpus | 16.6% | [12.5, 21.4%] |
| Human, partial matches counted | 14.3% | [7.6, 23.4%] |
| Adjudicated, control must cover the whole rule | 4.4% | [2.6, 6.7%] |

Coverage splits by what the rule protects: destructive commands 31.5%, network egress 26.5% — each names a command or a domain the matcher can see — against authorization at 6.9% and personal data at 5.6% ([arXiv:2608.23550v1](https://arxiv.org/abs/2608.23550v1)).

## Why it works (the rule has nothing to bind to)

A Claude Code permission rule binds to a tool name, the text of a Bash command, a `Read` or `Edit` file path in gitignore syntax, or a `WebFetch` domain ([Configure permissions](https://code.claude.com/docs/en/permissions)). That is the whole surface. Most written security rules name a property of file content or of runtime state instead, so there is no slot for them to bind to. The gap is structural rather than a sign that authors were careless.

Yan's classifier splits all 870 security rules by reason: 446 would need custom code (51.3%), 181 need open-ended model judgment (20.8%), and 99 turn on information the enforcement point cannot observe (11.4%). Read those as exploratory. No annotator validated them, and the paper says so: "we treat their percentages as exploratory and do not read the 'custom' share as the fraction of the gap that added code could close". Claude Code's documentation confirms the same boundary from the other side: it rejects `Bash(command:rm *)` outright, because a rule matching a tool's primary content field "would be bypassable by a compound command" ([Configure permissions](https://code.claude.com/docs/en/permissions)).

## Sort each rule into four buckets

Take each security rule you have written and decide what could enforce it.

| Bucket | The rule names | Where enforcement belongs |
|---|---|---|
| A built-in control covers it | a command, a path, or a domain | a `deny` or `ask` entry under `permissions` |
| A deterministic check covers it, but needs code | file content or a repository invariant | a [hook](../../instructions/hooks-vs-prompts.md), a pre-commit check, or CI |
| It needs judgment | something no fixed check can decide | prose, recorded as advisory |
| The information is not observable | state the enforcement point cannot see | change the rule or change the design |

The custom-code bucket is the largest of the three, and it is the one the paper's number hides. Yan excludes hooks from the control set because they require author-written executable logic, so a team that enforces its rules through hooks scores near zero on this metric while being well enforced. Keep the prose line in every case. It still shapes what the agent attempts.

## When this backfires

You convert six rules to deny entries and stop there. Claude Code's documentation warns that "Bash permission patterns that try to constrain command arguments are fragile", and lists five ways `Bash(curl http://github.com/ *)` misses: an option before the URL, a different protocol, a redirect, a shell variable, an extra space. Path deny rules have their own hole. They "don't apply to arbitrary subprocesses that read or write files indirectly, like a Python or Node script that opens files itself", and the documentation points at the OS sandbox for anything stronger ([Configure permissions](https://code.claude.com/docs/en/permissions)). A mapped rule you now trust is worse than an unmapped rule you still worry about.

You delete the rules that have no control. Rules files raise coding-agent task performance, and randomly generated rules help as much as expert-curated ones, both by 13.8 percentage points on a discriminative subset of SWE-bench Verified ([Zhang et al., 2026](https://arxiv.org/abs/2604.11088v2)). Rules appear to work partly by priming context rather than by being obeyed line by line, which [Guardrails Beat Guidance](../../instructions/guardrails-beat-guidance-coding-agents.md) covers in full. Yan never claims prose rules are worthless.

Your project has nothing to protect. The corpus skews small and new, with 93% of segments coming from repositories created in 2025 and 2026, and 58% of repositories carrying no stars ([arXiv:2608.23550v1](https://arxiv.org/abs/2608.23550v1)). A solo project with no secrets, no deploy, and no shared state gets ceremony from this audit and little else.

## Example

Four rules Yan quotes from the corpus, with the paper's match verdict and its own stated reason. The bucket column is this page's mapping onto the three reasons above, not the paper's — Table IV records a match decision and a reason, and never assigns its examples to Table VIII's categories ([arXiv:2608.23550v1](https://arxiv.org/abs/2608.23550v1)):

| Rule as written | Paper's reason (verbatim) | Bucket (ours) |
|---|---|---|
| "do not run rails credentials" | "deny on Bash command" | built-in control |
| "never store API keys in plaintext JSON in production" | "No control reads file content; production unobservable" | not observable |
| "never log passwords, tokens, IBAN, or location" | "No control inspects log content" | needs code |
| "delete the team only after all members shut down" | "Runtime state invisible" | not observable |

Four lines that look identical in the file, and only the first has a control behind it. `"Bash(rails credentials:*)"` under `permissions.deny` blocks that call before it runs. The logging rule needs code — a scrubber in the log path, because no control inspects log content. The other two turn on state the enforcement point cannot see: which environment is production, and whether every team member has shut down. Those stay in prose, marked advisory, so the next reader does not assume the runtime is watching.

## Key Takeaways

- Under the strictest matching standard 4.4% of security rules across 481 public CLAUDE.md files had a matching built-in control, rising to 16.6% when partial matches count ([arXiv:2608.23550v1](https://arxiv.org/abs/2608.23550v1)).
- The gap is structural. Permission rules bind to a tool name, a command string, a file path, or a domain, and most security rules name content or runtime state instead.
- Hooks sit outside the paper's control set, so rules a hook would enforce were coded as needing custom code rather than as unenforceable. That inflates the custom bucket by an amount the paper does not estimate.
- A rule that maps cleanly to a deny entry is still not a boundary. Claude Code documents that argument-constraining Bash patterns are fragile and that path deny rules miss subprocesses.
- Sort each rule by what could enforce it, then move the ones that need code out of prose and into a hook or CI. Keep the prose line either way.

## Related

- [Restraint Rules Need External Enforcement](../../instructions/restraint-rules-need-external-enforcement.md) — the compliance half of the same problem: refusal and handoff rules score 0% across four agents
- [Enforced Versus Advisory Controls in LLM-Native IDEs](../../security/enforced-versus-advisory-controls.md) — the taxonomy this measurement fills in, drawn from 446 user-reported incidents
- [Hooks for Enforcement vs Prompts for Guidance](../../instructions/hooks-vs-prompts.md) — where the second-bucket rules go once you have sorted them
- [Prompt-Only Tool Access Control](prompt-only-tool-access-control.md) — the same shape one layer down, at the tool-call boundary
- [bypassPermissions Silently Overrides allowedTools](bypass-permissions-overrides-allowlist.md) — the other way a permission configuration reads as restrictive and is not
- [Public Rules-File Corpora as Evidence](../../instructions/rules-file-corpus-evidence.md) — how to read a corpus study of rules files without over-claiming from it
