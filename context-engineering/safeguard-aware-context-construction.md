---
title: "Retrieve Project Safeguards for Security-Sensitive Code"
term: "Safeguard-Aware Context Construction"
description: "Functionality-oriented retrieval lifts correctness more than security. Put the project's own guards in context and check retrieved siblings for missing checks."
aliases:
  - security-aware context construction
  - safeguard retrieval for code generation
tags:
  - context-engineering
  - technique
  - security
  - arxiv
  - tool-agnostic
last_reviewed: 2026-11-09
maturity: emerging
---

# Retrieve Project Safeguards for Security-Sensitive Code

> Functionality-oriented retrieval lifts correctness more than security, so put the project's own safeguards in context and check retrieved siblings for missing guards.

This applies when an agent writes security-sensitive code whose safety depends on a project API or a repository-specific rule, such as an authorization check. It matters most when the repository also holds unfixed code with the same weakness. CASE-Bench contains 145 tasks built from real CVEs in 51 projects. Eleven functionality-oriented context methods changed the functional pass rate by up to 8.2 percentage points (pp) but the secure pass rate by at most 3.7 pp. None differed significantly from showing the model the target file alone ([A.S.E 2.0, arXiv:2611.06294v1](https://arxiv.org/abs/2611.06294v1)). Absolute numbers stay low: the best deployable method raised the secure pass rate from 12.6% to 18.1%, and a hand-annotated safeguard context reached 24.8%.

## How to apply it

1. Retrieve the safeguard on purpose. Before editing a sensitive operation, look for the code that enforces its policy: the access-control module, the project's validators, the safe API. In the study, removing one safeguard role from the hand-annotated context cost 3.9 to 8.1 pp of secure pass rate, and adding missing safeguards to the best method's context added 5.9 pp ([arXiv:2611.06294v1](https://arxiv.org/abs/2611.06294v1)).
2. Size the context by safeguard coverage. The repository truncated to 128K tokens raised the functional pass rate by 4.0 pp and lowered the secure pass rate by 0.5 pp. The paper's advice: "Context budgets should follow safeguard coverage rather than size, because larger contexts also expose more insecure exemplars." Placement matters in long contexts too: a safeguard in the middle cost 0.6 pp at 4K tokens and 5.9 pp at 64K ([arXiv:2611.06294v1](https://arxiv.org/abs/2611.06294v1)).
3. Check retrieved siblings before they become templates. On 74 tasks with an unguarded sibling, inserting one into the hand-annotated safeguard context raised correct-but-exploitable code by 6.3 pp "although the safeguard remains present". The authors suggest existing static analysis for this check, since an exemplar only needs flagging, not proof ([arXiv:2611.06294v1](https://arxiv.org/abs/2611.06294v1)).
4. After generation, confirm the guard sits on the attack path. With security-aware context, unused and misused safeguards rose from 10.7 to 21.3 per 100 generations ([arXiv:2611.06294v1](https://arxiv.org/abs/2611.06294v1)).

A generic security instruction does not substitute for any of this. It added 1.3 pp of secure pass rate "while lowering FuncPass@1 by 1.8 pp because some generations reject benign inputs" ([arXiv:2611.06294v1](https://arxiv.org/abs/2611.06294v1)).

## Coding agents share the gap

Agents read far more of the repository than a retriever and still miss the guard. SWE-agent and Claude Code read 16 to 26 times as many repository tokens as an 8K context, yet saw the relevant safeguard in only 27-36% of trajectories. On tasks that held an unguarded sibling, they saw one in 43-51% of trajectories. Of their search queries, 71% named functional entities and 9% named security concepts ([arXiv:2611.06294v1](https://arxiv.org/abs/2611.06294v1)).

Seeing the guard is not enough either. Trajectories that observed and used the safeguard reached 34.5% secure pass rate against 12.7% for those that never saw it. But 41% of trajectories that observed a safeguard did not use it. The authors say these results "motivate, but do not validate" two directions: agents that search for safeguards before editing, and post-generation checks that the guard covers the untrusted value. Treat step 1 for agents, and step 4 in general, as untested.

## Why it works

Functionality-oriented retrievers build their queries from the target code and the requirement, which say what the code does, and agent searches show the same bias. The rule that constrains it usually lives somewhere else. In the paper's words: "Safeguards, however, often live elsewhere in the repository (e.g., in a central access-control module), so they rarely resemble the target, whereas unfixed siblings resemble it closely" ([arXiv:2611.06294v1](https://arxiv.org/abs/2611.06294v1)). Similarity search therefore surfaces the sibling to copy and skips the policy.

Length explains little of the effect: irrelevant code of the same length at the same position raised correct-but-exploitable output by only 0.6 pp. Slicing from untrusted input to the sensitive operation and keeping the guards on that path raised the secure pass rate by 5.5 pp, the only method significant after correction. It beat external security knowledge most clearly on access control (9.3% against 3.1%), where security depends on project policy.

## When this backfires

- Generic checks: on tasks that built-in defenses can secure, the best functionality-oriented method gained 2.0 pp and the slicing method 1.8 pp. Safeguard retrieval adds little there ([arXiv:2611.06294v1](https://arxiv.org/abs/2611.06294v1)).
- A slice with only the vulnerable path can leave out the functional context the model needs. On RealSec-bench, a CodeQL dataflow retriever gave inconsistent results because "its narrow focus on vulnerability paths often omits broader functional contexts" needed to compile ([arXiv:2601.22706v1](https://arxiv.org/abs/2601.22706v1)). That study judged security with static analysis, which A.S.E 2.0 found ranks methods differently from exploits ([arXiv:2611.06294v1](https://arxiv.org/abs/2611.06294v1)).
- Static flagging misses some unguarded siblings. The paper's own queries "miss 17% of the vulnerable versions and flag 13% of the patched ones" ([arXiv:2611.06294v1](https://arxiv.org/abs/2611.06294v1)).
- Context cannot reveal every policy. In 8 of 145 tasks, the security property followed from neither the requirement and target file nor the annotated safeguards ([arXiv:2611.06294v1](https://arxiv.org/abs/2611.06294v1)).
- The evidence is one benchmark. The paper reproduces each method's context policy rather than running the original tool, and differences below about 5.6 pp may go undetected ([arXiv:2611.06294v1](https://arxiv.org/abs/2611.06294v1)).

## Example

OpenEMR CVE-2022-2732 let any authenticated user amend a patient record. The required permission appeared only in a widget guard in `demographics.php`, while the target file and its sibling pages had misleading or missing checks. The target file alone produced 0 of 18 secure generations. Functionality-oriented methods produced at most three, "because similarity retrieval favoured the unchecked siblings". Claude Code's retrieval found `demographics.php` but ranked it after the siblings (3 of 18). The slicing method followed the request from its form to the database write and retrieved the guard (6 of 18). The annotated safeguard context reached 12 of 18, four other generations checked the permission only after the request had run ([arXiv:2611.06294v1](https://arxiv.org/abs/2611.06294v1)).

## Key Takeaways

- Search for the guard of a sensitive operation by role (access policy, validator, safe API), not by similarity to the target.
- Measure context by whether it contains the safeguard; a bigger window brought more unguarded siblings and no security gain.
- Treat an unguarded sibling in context as a hazard: one raised exploitable output by 6.3 pp even with the safeguard present.
- Keep exploit tests and review downstream. The best deployable context still left over 80% of outputs insecure or broken.

## Related

- [Give the Model the Target's Contract, Not Similar Solutions](contract-context-over-example-retrieval.md) — the correctness-side case against retrieving similar solutions
- [Repository-Level Retrieval for Code Generation](repository-level-retrieval-code-generation.md) — the retriever families this study compared, viewed for correctness
- [Codebase-Derived Pattern Libraries as Agent Context](codebase-pattern-library-context.md) — serving your own code as examples, where unfixed siblings become templates
- [Lost in the Middle: The U-Shaped Attention Curve](lost-in-the-middle.md) — the position effect the study saw for safeguards in long contexts
- [Treating a Model Upgrade as a Security Improvement](../patterns/anti-patterns/model-upgrade-as-security-improvement.md) — why a newer model does not remove weaknesses that context leaves open
