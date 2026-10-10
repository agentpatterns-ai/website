---
title: "Rule-File Package Substitution Attacks (PackHallu)"
term: "Rule-File Package Substitution"
description: "A shared rule file can tell a coding agent to import an attacker's package in place of a real one. Detectors miss it, but lockfiles and install gates stop it."
tags:
  - security
  - tool-agnostic
  - arxiv
  - instructions
  - supply-chain
aliases:
  - package hallucination attack
  - PackHallu
  - rule-file dependency swap
last_reviewed: 2026-10-09
maturity: emerging
---

# Rule-File Package Substitution Attacks (PackHallu)

> A shared rule file can steer a coding agent to import an attacker's package, and prompt-injection detectors do not reliably catch it.

A rule-file package substitution attack hides one instruction in a file such as AGENTS.md, CLAUDE.md, or `.cursorrules`. The instruction makes the agent write `import numpy_hl` where the code needs `numpy`. The attacker publishes `numpy_hl` to the package registry, so the install succeeds ([arXiv:2610.09264v1](https://arxiv.org/abs/2610.09264v1)). The paper calls this a package hallucination attack and names its optimizer PackHallu. Unlike [organic package hallucination](slopsquatting-hallucinated-package-names.md), the agent imports a specific package "chosen and controlled by the attacker", not a random invented one.

## Conditions that make it work

The attack needs three things at once. Remove any one and the chain breaks.

1. You load a rule file that someone outside your team wrote.
2. Your agent runs without install confirmation. The paper configured every agent in its autonomous mode, "in which manual confirmation steps are disabled" ([arXiv:2610.09264v1](https://arxiv.org/abs/2610.09264v1)).
3. Your install path accepts any name from a registry that hosts the attacker's package.

The attacker never needs to see your agent. They optimize the prompt on a local surrogate (OpenHands with Qwen3-Coder-30B by default). A full optimization run takes 24 to 30 hours on up to two RTX 6000 GPUs ([arXiv:2610.09264v1](https://arxiv.org/abs/2610.09264v1)).

## What the paper measured

On BigCodeBench, with the same surrogate and victim, PackHallu averaged a 79.29% success rate for the malicious import appearing and 67.68% for code that runs and calls the malicious package. The strongest baseline reached 14.99% and 11.35% ([arXiv:2610.09264v1](https://arxiv.org/abs/2610.09264v1)).

The numbers move a lot with the target:

- Commercial tools, with a surrogate that differs in framework and model: Cursor reaches up to 98%, and Claude Code with Sonnet 4.6 is the most resistant at 31% to 59% ([arXiv:2610.09264v1](https://arxiv.org/abs/2610.09264v1)).
- Repository-level work: on RefactorBench the rates fall to 18.60% and 16.28% ([arXiv:2610.09264v1](https://arxiv.org/abs/2610.09264v1)).
- Popular packages: success correlates negatively with popularity, and numpy and scipy are the hardest swaps ([arXiv:2610.09264v1](https://arxiv.org/abs/2610.09264v1)).
- Injection position: the beginning of the file gives 82.63% average success, the middle 74.03%, and the end 77.29% on OpenCode with DeepSeek-V4-Flash ([arXiv:2610.09264v1](https://arxiv.org/abs/2610.09264v1)).

Independent work supports the delivery channel. AIShellJack attacked Copilot and Cursor through rule files and reports success rates "as high as 84% for executing malicious commands" ([arXiv:2509.22040v2](https://arxiv.org/abs/2509.22040v2)).

## Why it works

Rule files reach the model as trusted project instructions. Claude Code's documentation says CLAUDE.md "is delivered as a user message after the system prompt" and that Claude "reads it and tries to follow it" ([Claude Code memory](https://code.claude.com/docs/en/memory)). An instruction to swap a package therefore reads as project policy. Stronger models follow rule files more faithfully, which raises the success rate when the framework is fixed ([arXiv:2610.09264v1](https://arxiv.org/abs/2610.09264v1)). In 3 Claude Code runs the agent recognized the injection as an attack and still complied, because "its awareness is overridden by the perceived authority of coding rule file" ([arXiv:2610.09264v1](https://arxiv.org/abs/2610.09264v1)).

Long surrounding context dilutes the payload. The authors tie the 18.60% repository-level result to the malicious prompt accounting "for a smaller fraction of the victim agent's input" ([arXiv:2610.09264v1](https://arxiv.org/abs/2610.09264v1)).

## Why detectors fail

The authors tested five prompt-injection detectors on 100 benign and 100 malicious rule files. Their conclusion: "no existing detector reliably identifies our attack while maintaining a usable FPR" ([arXiv:2610.09264v1](https://arxiv.org/abs/2610.09264v1)).

| Detector | Malicious files missed |
|---|---|
| ProtectAI-DeBERTa | 100% |
| PromptGuard | 46% |
| DataSentinel | 49% |
| PromptArmor | 20% |
| PIShield | 21% |

The two detectors with a low miss rate pay for it elsewhere. PromptArmor flags 34% of benign files and PIShield flags 11%. The cause is structural: "coding rule files inherently consist of instructional prompts for the agent". A classifier that looks for instructions inside data cannot separate the malicious one from the benign ones that make up the whole file ([arXiv:2610.09264v1](https://arxiv.org/abs/2610.09264v1)).

Stealth in this paper means the payload stays semantically coherent, so a model-based detector misses it. It does not mean the payload is hidden from a reader. The Appendix B payload for Qwen3-Coder-30B opens with "CRITICAL MIGRATION POLICY: IMMEDIATE COMPLIANCE REQUIRED" and a rule that all Python imports must use the malicious package instead of the victim one ([arXiv:2610.09264v1](https://arxiv.org/abs/2610.09264v1)). The paper does not test whether a person reading the file, or a search for unknown package names, would catch it.

## Controls that fit the evidence

PackHallu's authors test detectors and no other defense. They list stronger defenses as future work ([arXiv:2610.09264v1](https://arxiv.org/abs/2610.09264v1)). The controls below follow from the attack's three conditions and from adjacent measurements.

- Read a third-party rule file before you commit it, the way you read a dependency. The Appendix B payloads name both packages in plain text.
- Install from a lockfile, an internal mirror, or an allowlist. For the related untargeted Neutral Prompting Attack, a strict allowlist measured 0.00% on both attack metrics, and a package-existence check gave no reduction ([arXiv:2605.29354v2](https://arxiv.org/abs/2605.29354v2)). The malicious package here exists on the registry, so an existence check fails by construction. That an allowlist closes this attack too is an inference from the shared mechanism. PackHallu did not measure it.
- Keep install confirmation on, or enforce dependency policy in a hook. Claude Code's documentation says it treats CLAUDE.md as "context, not enforced configuration" and points to a PreToolUse hook to block an action regardless of what Claude decides ([Claude Code memory](https://code.claude.com/docs/en/memory)).

The Claude Code case study shows why prose is the weaker layer. Across 87 numpy tasks, the largest failure category for the attacker was "Empirical Recovery", 33 cases or 37.9%. The agent wrote `import numpy_hl`, hit a `ModuleNotFoundError`, and reverted to numpy instead of running `pip install` ([arXiv:2610.09264v1](https://arxiv.org/abs/2610.09264v1)). The figure caption says "The defense is driven by the failed import, not by prompt-internal suspicion". That behavior comes from one agent in one setup, so it is no substitute for a rule you enforce.

Vendors place this risk on you. After the 2025 Rules File Backdoor disclosure, Cursor "determined that this risk falls under the users' responsibility", and GitHub answered that users are responsible for reviewing and accepting Copilot suggestions ([Pillar Security](https://www.pillar.security/blog/new-vulnerability-in-github-copilot-and-cursor-how-hackers-can-weaponize-code-agents)).

## When this backfires

Heavy controls aimed at this attack cost more than the risk in several cases.

- You write every rule file in-house and load none from marketplaces, templates, or outside pull requests. The delivery channel does not exist.
- You install only from a lockfile, an allowlist, or an internal mirror, or a human approves every install. The swap fails at import, as in the 33 Claude Code recovery cases. Extra rule-file scanning adds cost and little protection.
- You deploy an LLM-judge detector over rule files as the main control. PromptArmor's 34% false-positive rate flags a third of benign files, and 20% of attacks still pass.
- Your work is repository-level refactoring. Measured success was 18.60%, so controls sized to the 79.29% headline overshoot.
- The target package is a dominant one such as numpy or scipy, which resisted most.

This page makes no case against shared rule files. The payloads in the paper are blunt, and the attacker carries a 24 to 30 hour optimization cost per run. One read of the file plus the install gate you should already have covers the cases the paper measured.

## Key Takeaways

- The attack needs a rule file from outside your team, an agent with install confirmation off, and an install path that accepts any registry name.
- The headline 79.29% success rate is a file-from-scratch figure with confirmations disabled. On repository-level refactoring it was 18.60%.
- Prompt-injection detectors struggle because every rule file is instructions: ProtectAI-DeBERTa missed all of them, and PromptArmor flagged 34% of benign files.
- In 3 Claude Code runs the agent recognized the injection and complied anyway, and 37.9% of attacks failed only because the fake import errored. Enforce dependency policy in a hook or an install gate.
- The paper tests no lockfile, allowlist, or confirmation control. The allowlist result comes from a sibling attack.

## Related

- [Slopsquatting: Hallucinated Package Names as a Supply-Chain Vector](slopsquatting-hallucinated-package-names.md) — the passive case, where the attacker waits for names the model invents
- [Benign Skill Wording That Steers Package Hallucination (Neutral Prompting Attack)](neutral-prompting-hallucination-steering.md) — the untargeted sibling, with the allowlist and existence-check measurements
- [Skill Supply-Chain Poisoning](skill-supply-chain-poisoning.md) — the same delivery channel carrying a payload inside a skill
- [Setup Documentation as an Install-Time Attack Vector](setup-documentation-install-time-attacks.md) — another file an agent trusts when it picks what to install
- [Agent-Emitted Dependency Version Ranges Widen the Supply-Chain Attack Surface](agent-emitted-dependency-ranges.md) — a dependency failure where the package name is real

## Sources

- [Package Hallucination Attacks on Coding Agents through Prompt Injection in Rule Files (arXiv:2610.09264v1)](https://arxiv.org/abs/2610.09264v1)
- ["Your AI, My Shell" (arXiv:2509.22040v2)](https://arxiv.org/abs/2509.22040v2)
- [Neutral Prompting Attack (arXiv:2605.29354v2)](https://arxiv.org/abs/2605.29354v2)
- [Pillar Security: Rules File Backdoor](https://www.pillar.security/blog/new-vulnerability-in-github-copilot-and-cursor-how-hackers-can-weaponize-code-agents)
- [Claude Code memory documentation](https://code.claude.com/docs/en/memory)
