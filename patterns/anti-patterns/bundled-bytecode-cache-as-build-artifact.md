---
title: "Treating a Bundled Bytecode Cache as a Build Artifact"
term: "Inspection-Execution Gap"
description: "Seven skill scanners failed to flag 94 to 100% of packages whose concealed behavior sat in a shipped bytecode cache, and no finding named that cache body."
aliases:
  - inspection-execution gap
  - PyCache Trap
  - source-cache mismatch
tags:
  - anti-pattern
  - security
  - skills
  - tool-agnostic
  - arxiv
last_reviewed: 2026-10-11
maturity: emerging
---

# Treating a Bundled Bytecode Cache as a Build Artifact

> Python's acceptance check establishes that a bundled bytecode cache may load, not that it was compiled from the source a scanner read.

Three conditions have to hold together. The skill comes from a third party and ships Python, it arrives with a `__pycache__` you did not compile, and your review reads the source. Where they do, the file you approved and the file Python runs are two different artifacts, and nothing in the import machinery relates them.

## Why it works

CPython validates a cache for eligibility, never for derivation. The default mode stores the source's last-modified timestamp and size. The hash-based modes store a hash of the source contents instead, and one of the two skips the comparison. The reference manual states that case plainly: "For unchecked hash-based `.pyc` files, Python simply assumes the cache file is valid if it exists" ([Python import reference](https://docs.python.org/3/reference/import.html#cached-bytecode-invalidation)). PEP 552 puts the bit that selects that behavior inside the file, written by whoever compiled it ([PEP 552](https://peps.python.org/pep-0552/)).

A skill publisher controls the documentation, source, scripts and bundled caches, and so controls both the header the loader inspects and the body it executes. The attack needs "neither a hash collision nor a modified interpreter" ([arXiv:2610.10612v1](https://arxiv.org/abs/2610.10612v1)).

## What the findings cannot tell you

Across 100 attacked skills, seven scanners failed to flag 94 to 100% of them, and semantic recognition was zero for all seven ([arXiv:2610.10612v1](https://arxiv.org/abs/2610.10612v1)). The rubric was strict. A positive label needed a finding identifying the substituted cache, its concealed behavior, or the file carrying it. "Merely mentioning a cache, bytecode, or suspicious invocation wording does not qualify." So the usual corrective of reading what fired has nothing to work on, and the source a reviewer would read is benign by construction.

Those figures measure non-detection. The paper collected runtime confirmation for only four of the seven scanners. For those four, "Admission plus a runtime-signature match occurs in 76–83 of 100 victims", in isolated research sandboxes against assigned behaviors ([arXiv:2610.10612v1](https://arxiv.org/abs/2610.10612v1)).

## What to check instead

Compare a trusted recompile of the inspected source against the shipped cache, on the code objects. The paper measures that against the alternatives over the same 100 substitutions and 100 legitimate caches, under Python 3.11 ([arXiv:2610.10612v1](https://arxiv.org/abs/2610.10612v1)):

| Check | Substitutions caught | False positives on legitimate caches |
|---|---|---|
| Reject any package carrying a cache | 100 of 100 | 100 of 100 |
| Header consistency, what the loader already does | 0 of 100 | 14 of 100 |
| Read the bytecode's semantics directly | 100 of 100 | 17 of 100 |
| Recompile the source and compare | 100 of 100 | 0 of the 86 pairs it can check |

The recompile costs 2.15 ms at median latency. On the 14 fixtures that ship a cache with no source it abstains rather than clears ([arXiv:2610.10612v1](https://arxiv.org/abs/2610.10612v1)). Treat an abstention as a refusal: nothing to reproduce means nothing to approve. A flagged package is usually repairable, since rebuilding from inspected source "removes the substituted bytes in all 99 code-bearing packages in the repair evaluation" ([arXiv:2610.10612v1](https://arxiv.org/abs/2610.10612v1)).

Two interpreter settings look like they do this job and do not. `PYTHONDONTWRITEBYTECODE` and `-B` stop Python writing caches on import, which says nothing about one the publisher shipped ([Python command line](https://docs.python.org/3/using/cmdline.html#envvar-PYTHONDONTWRITEBYTECODE)). `--check-hash-based-pycs=always` makes the loader hash the source and compare it with the hash stored in the cache, "whether checked or unchecked" ([Python command line](https://docs.python.org/3/using/cmdline.html#cmdoption-check-hash-based-pycs)). The publisher writes that stored hash, so the flag changes which header field the loader checks and does not show that the body derives from the source. It also leaves timestamp-based files unaffected. Only deletion and recompile-and-compare cover both modes.

## When this backfires

- The study that hunted for it found nothing. The paper that calls itself "the first to investigate Python cache poisoning" reports: "While we did not identify any malware leveraging this attack vector, we demonstrate that several widespread package managers are vulnerable to such attacks" ([Ohm et al., SICHERHEIT 2026](https://doi.org/10.18420/sicherheit2026_13)). Rank it below the instruction surface, where the attacks you can point to live.
- Shipping a cache is ordinary. That study finds "about 12,500 packages are distributed with cache files" on PyPI ([Ohm et al., SICHERHEIT 2026](https://doi.org/10.18420/sicherheit2026_13)). The base rate is what makes the cheap rule expensive: rejecting on cache presence rejected all 100 legitimate fixtures ([arXiv:2610.10612v1](https://arxiv.org/abs/2610.10612v1)).
- The skill ships no Python, so there is nothing to compare. The paper's corpus was built "without requiring existing Python files", and its attack "adds the source/cache module and task-relevant invocation" to every skill ([arXiv:2610.10612v1](https://arxiv.org/abs/2610.10612v1)).
- Your fleet spans interpreter versions. The comparison needs an interpreter-matched compile, and the paper holds unsupported pairings and compilation failures as "unresolved rather than evidence of derivation" ([arXiv:2610.10612v1](https://arxiv.org/abs/2610.10612v1)).
- A custom import hook loads a standalone cache. Reproduction abstained on all 50 sourceless custom-hook fixtures, "whose loaded artifacts remain unresolved in the graph" ([arXiv:2610.10612v1](https://arxiv.org/abs/2610.10612v1)).

## Example

**Before** — a skill ships `SKILL.md`, a short `main.py`, and `__pycache__/helpers.cpython-311.pyc`. The source is unremarkable, the scan returns clean or a generic note that a compiled file is present, and the skill installs. The closest published case ran this way. ReversingLabs found a PyPI package whose two source files "appeared benign" and whose behavior lived in a third, a `.pyc`. Its payload method "isn't found (in readable form) anywhere inside the original *fshec2* package" ([ReversingLabs, 2023](https://www.reversinglabs.com/blog/when-python-bytecode-bites-back-who-checks-the-contents-of-compiled-python-files)). That package loaded its cache through a loader script rather than substituting one, a different mechanism in the same artifact class.

**After** — installation deletes any `__pycache__` the publisher shipped and lets the interpreter regenerate it, which ends the question for the common case. Where a cache has to be kept, compile the inspected source with a matching interpreter and compare the code objects. A cache with no source beside it is unreviewed code.

## Key Takeaways

- Delete a publisher-supplied `__pycache__` at install and let the interpreter rebuild it. That covers both invalidation modes. `--check-hash-based-pycs=always` and `PYTHONDONTWRITEBYTECODE` cover neither against a substituted cache.
- Where a cache has to survive install, run recompile-and-compare on code objects. Of the standalone checks in the paper's table, it was the only one that caught all 100 substitutions with no false positives on checkable pairs. It needs the source and a matching interpreter.
- Log an abstention as unreviewed, never as a pass. The sourceless cache is both the case the check cannot resolve and the case an attacker has the most room in.
- Regenerate rather than reject. Rejection discards the skill along with the cache, while rebuilding from inspected source keeps it and removed the substituted bytes in all 99 code-bearing packages.
- Put this below text-surface attacks in a review backlog. The evidence here is a laboratory demonstration, and the one prior study found no malware using the vector.

## Related

- [Trusting a Skill Scanner's Verdict as a Security Judgment (Green-Check Fallacy)](skill-scanner-verdict-not-security-judgment.md) — the general case, where the corrective is to read the findings; here there are no findings to read, so the artifact under review has to change instead.
- [Treating a Clean Static Scan as Security Evidence](static-clean-as-security-evidence.md) — the same gap over application source, where the scanner reads the right file and misses a runtime property.
- [Skill Supply-Chain Poisoning](../../security/skill-supply-chain-poisoning.md) — the text-surface attack on the same distribution channel, and the one with observed incidents.
- [Vetting Tool Definitions for Exfiltration Signatures](../../security/vetting-tool-definitions-before-install.md) — what manual review of a declaration can and cannot establish before install.
- [Credential Hygiene for Agent Skills](../../security/credential-hygiene-agent-skills.md) — what a skill reaches once admission has let it run.
