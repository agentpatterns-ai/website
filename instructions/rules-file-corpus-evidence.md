---
title: "Public Rules-File Corpora as Evidence"
term: "Rules-File Corpus Evidence"
description: "Corpus studies of .cursorrules files measure authorship, not efficacy: code quality fills 30.4% of coded content and security 4.2%, and 68.5% of the repositories have a single maintainer."
aliases:
  - cursorrules corpus studies
  - rules file corpus evidence
tags:
  - instructions
  - cursor
  - arxiv
last_reviewed: 2026-08-13
maturity: emerging
---

# Public Rules-File Corpora as Evidence

> Corpora of public `.cursorrules` files record what developers wrote and when, and carry no measure of whether any of it worked.

Two published corpora describe what project rules files contain. Both answer the question "what did developers write", and neither answers "did it help". Use them for two narrow purposes: auditing your own file against a measured baseline, and refusing the inference that a theme is rare because teams found it unnecessary.

## What the corpus measures

Sun et al. collected 12,110 unique `.cursorrules` files from 11,427 GitHub repositories, covering 15 April 2024 to 30 September 2025 ([arXiv:2608.10622v1](https://arxiv.org/abs/2608.10622v1)). They then coded a random sample of 65 prompt files into a 65-code codebook, 51 of them `.cursorrules` and 14 in the successor `.mdc` format. The dataset holds file content, commit history, and repository metadata. It holds no outcome variable, so it cannot support any claim about rule effectiveness.

Content is concentrated in three themes. Code quality and engineering practices take 30.4% of coded instances, project structure and configuration 18.3%, and maintainability and evolution 14.4%. Security takes 4.2% and access control 1.0%.

Some of the security-relevant content works against its author. About 1.5% of all coded instances are what the authors call security smells: information exposure, hard-coded sensitive parameters, internal resource exposure, and contradictory instructions.

Authorship is thinner than the file count suggests. Sun et al. report that 68.5% of the repositories are maintained by a single contributor, and only 3.4% involve more than ten. Activity is correspondingly low: 62.5% carry 50 or fewer commits, and 95.8% of the files were touched by one contributor. Their own summary: "most of these projects are small, unpopular, and are maintained by a single contributor".

None of this is confined to the deprecated format. Sun et al. report "a continuity of themes and topics between the now-legacy .cursorrules files and the current standard .mdc files", and their codebook stayed saturated when they extended it to `.mdc` samples ([arXiv:2608.10622v1](https://arxiv.org/abs/2608.10622v1)). The content findings carry over to the format teams use now.

## Why it works

The skew follows from when the file gets written. Sun et al. found that 40.7% of `.cursorrules` files appear within 24 hours of repository creation, and that 67.3% are never edited again ([arXiv:2608.10622v1](https://arxiv.org/abs/2608.10622v1)). A file authored at hour zero can only carry what its author already believed, which is stack conventions and formatting preferences. Security constraints arrive from incidents a day-old project has not had, so their absence says nothing about whether they belong.

That is also why prevalence says nothing about efficacy. The outcome measurement comes from separate work, covered in [Guardrails Beat Guidance](guardrails-beat-guidance-coding-agents.md). Zhang et al. ran rule sets against SWE-bench Verified and found that "random rules tie with curated rules at 63.8%" ([arXiv:2604.11088v2](https://arxiv.org/abs/2604.11088v2)). Mismatched, wrong-domain rules slightly outperformed matched ones. Rule topic was not the discriminating variable. Rule polarity was, and every distorting rule they identified was a positive directive.

Independent work reaches the same shape on content. Jiang and Nam analyzed 401 open-source repositories containing cursor rules and derived five themes: conventions, guidelines, project information, LLM directives, and examples ([arXiv:2512.18925v3](https://arxiv.org/abs/2512.18925v3)). Security does not appear among those five.

## When this backfires

Generalizing past the artifact is the most common misreading. The adoption profile describes legacy `.cursorrules` files in a 2024 to 2025 window. A deliberately popular-repo sample looks different: ActPlane's snapshot of 2026-05-23 holds "64 repositories with median 20K GitHub stars, 84 instruction files, and 2,116 extracted statements" ([arXiv:2606.25189v2](https://arxiv.org/abs/2606.25189v2)). Professional projects do maintain instruction files, and quoting the single-maintainer figure at AGENTS.md adoption misreads the sample.

Format churn is a competing explanation for the adoption profile, and the study does not rule it out. Cursor made `.cursorrules` legacy in February 2025 and pointed users at `.cursor/rules` and AGENTS.md ([arXiv:2608.10622v1](https://arxiv.org/abs/2608.10622v1)). Teams that kept pace migrated, so a corpus of files still carrying the old name over-samples repositories that stopped changing.

Over-correcting on the security gap wastes the finding. Raising security prose from 4.2% to a third of the file adds tokens and enforces nothing. Security written as "do X" directives is the shape Zhang et al. measured as distorting, so the fix belongs in CI or a hook, as covered in [Guardrails Beat Guidance](guardrails-beat-guidance-coding-agents.md).

Treating the codebook as a completeness checklist inflates the file for no gain. The authors call their 65-file sample "not a representative sample", so scoring your own file against all 65 codes manufactures bloat in an artifact whose cost is context budget.

## Example

Applying the method means asking, of any corpus claim, where the files came from. Doing that to the rule-file literature turns up a documented overlap. Zhang et al. built their study corpus as "679 files: 486 CLAUDE.md files from GitHub Code Search and 193 .cursorrules files from the awesome-cursorrules repository" ([arXiv:2604.11088v2](https://arxiv.org/abs/2604.11088v2)). The community library that practitioners copy starter files from is a component of the research corpus that describes practice. A finding drawn from that corpus cannot then validate the library, and a rules file copied from the library is not independent evidence of what teams converged on.

## Key Takeaways

- Corpus studies of rules files carry no outcome variable, so pair any content finding with an evaluation study before treating a theme as advice.
- The 4.2% security share is an authorship artifact of files written at scaffolding time, so absence is not evidence that security guidance is unwanted.
- Scope the single-maintainer profile to legacy `.cursorrules`; popular repositories carrying CLAUDE.md and AGENTS.md are a different population.
- Check your own file for the four documented security smells before adding anything: exposed paths, hard-coded secrets, internal URLs, and contradictory instructions.
- Community rule libraries feed the research corpora, so neither one corroborates the other.

## Related

- [Guardrails Beat Guidance: Rule Design for Coding Agents](guardrails-beat-guidance-coding-agents.md) — the outcome measurement this corpus lacks, and why positive directives underperform
- [Empirical Baseline: How Developers Configure Agentic AI Coding Tools](empirical-baseline-agentic-config.md) — which configuration mechanisms teams adopt, measured across 2,923 repositories
- [Stale AI Configuration Artifacts (Context Rot)](../patterns/anti-patterns/stale-ai-configuration-artifacts.md) — what happens to these files after the 67.3% stop being edited
- [Project Instruction File Ecosystem](instruction-file-ecosystem.md) — how `.cursorrules`, CLAUDE.md, and AGENTS.md relate
- [Encoding Values in AGENTS.md: Why Prose Without Verification Fails](encoding-values-in-agents-md.md) — the same gap for ethics and accessibility content, with the pairing rule
- [Documentation Read Counts Measure Retrievability, Not Value](documentation-read-counts.md) — the behavioral-trace version of the same trap, where read frequency stands in for efficacy
