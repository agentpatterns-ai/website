---
title: "Setup Documentation as an Install-Time Attack Vector"
term: "Weaponized Setup Instructions"
description: "Setup docs (README, requirements, Makefile) are unverified install authority: an attacker who edits them redirects an agent's install to a wrong name, untrusted registry, or vulnerable version, and the payload runs at install time."
tags:
  - security
  - tool-agnostic
  - anti-pattern
  - supply-chain
aliases:
  - install-time documentation supply chain attack
  - weaponized project setup instructions
last_reviewed: 2026-07-17
maturity: emerging
---

# Setup Documentation as an Install-Time Attack Vector

> An attacker who edits only a README, requirements file, or Makefile turns project setup into install-time code execution the agent runs unverified.

An AI coding agent asked to set up a project reads its documentation and installs what that documentation lists — without checking whether the package names are real, the registry is trusted, or the versions carry known CVEs. That makes setup documentation an install authority the agent obeys, so editing only a README, `requirements.txt`, `pyproject.toml`, or `Makefile` redirects the install to a wrong-but-plausible name, an attacker-controlled registry, or a known-vulnerable release. The first systematic evaluation of this surface probes four production harnesses across nine harness-model configurations on twelve scenarios in five attack classes ([arXiv:2607.15143](https://arxiv.org/abs/2607.15143)).

The distinguishing property is when the code runs. A typosquat or a registry redirect executes at install time through a package's `setup.py` or an import hook — before any code review, test, or human glance at the result. The [torchtriton dependency-confusion attack](https://pytorch.org/blog/compromised-nightly-dependency/) worked this way: a malicious `torchtriton` on public PyPI shadowed the package PyTorch shipped from its own index, `pip` installed the public one by default, and the payload harvested SSH keys and environment variables the moment it landed ([Wiz](https://www.wiz.io/blog/malicious-pytorch-dependency-torchtriton-on-pypi-everything-you-need-to-know)).

## The five attack classes

Each class violates a different trust property of an install — that the package is authentic, the intended one, and safe ([arXiv:2607.15143](https://arxiv.org/abs/2607.15143)):

- Name-based — a typosquat or separator-confusion name (`azurecore` for `azure-core`) in the manifest.
- Source-based — a redirect to an untrusted registry via an `--extra-index-url` flag or a hidden index directive in `requirements.txt`.
- Version-based — a pin to a release with a known CVE.
- Configuration-based — a build file that redirects resolution, for example a `Makefile` that sets `PIP_CONFIG_FILE`.
- Output-based — an error message that suggests installing an attacker's package.

The detection results invert the human threat model. Agents catch blatant typosquats reliably — an obvious `tranformers` misspelling was refused 30/30 — because those names recur in the security advisories the models trained on. Source-based attacks are missed almost everywhere: several harness-model pairs installed the untrusted registry 0 times out of 10, because `--extra-index-url` is a routine flag whose malicious uses are rare in training data. The plausible middle, separator confusion, splits by pairing — caught 30/30 on one configuration and 2/30 on another ([arXiv:2607.15143](https://arxiv.org/abs/2607.15143)).

## Why it works

The mechanism is that none of the three trust properties is verified anywhere in the install chain. The agent runs `pip install` without inspecting package contents and removes the human who would otherwise pause to check the name and source, so a manifest edit flows straight to code execution ([arXiv:2607.15143](https://arxiv.org/abs/2607.15143), Section 9.1). This is the same unverified-install-authority gap that makes model-hallucinated names exploitable in [slopsquatting](slopsquatting-hallucinated-package-names.md) — here the attacker authors the manifest instead of the model.

Two findings make the surface durable. First, the relevant security knowledge is present but dormant and dimension-specific: a prompt that names the source dimension lifted hidden-index detection from 0% to 93%, but had no effect on vulnerable version pins, which stayed at 0% until a version-targeted prompt raised refusal to 10/10 ([arXiv:2607.15143](https://arxiv.org/abs/2607.15143), Section 7). The default setup workflow simply does not activate reasoning the model can do on request. Second, install-then-flag is not prevention: once the install has run, the payload has already executed, so detecting it afterward reports a breach rather than stopping one.

## Install-time security is a harness-model property

The same model catches an attack through one harness and installs it through another — detection rests on the harness-model combination, not the model alone ([arXiv:2607.15143](https://arxiv.org/abs/2607.15143), Section 6.1). A pre-execution checkpoint let one model refuse an untrusted localhost registry 10/10 times; the same model through a run-then-report harness dropped to 9 refusals out of 30 (p=1.1×10⁻⁴). A harness that runs install commands immediately, with no per-command approval, forfeits the checkpoint however capable its model is.

## Closing the vector

Prompting recovers only the dimension it names, so the durable fix is deterministic. A pre-install gate that verifies name, source, and version before any install-time code runs — edit-distance and existence checks, package age, untrusted-source and hidden-directive detection, `PIP_CONFIG_FILE` inspection, and an OSV vulnerability lookup — caught 10 of 11 scenarios in the evaluation ([arXiv:2607.15143](https://arxiv.org/abs/2607.15143)). The practical controls:

- Gate the install behind a checkpoint that runs before install-time code, not a review after it.
- Treat the package source as a first-class trust signal: surface `--extra-index-url` and expand `requirements.txt` directives before executing them.
- Never auto-act on an install suggested by program output.
- Enforce a committed lockfile (`uv sync --frozen`, `npm ci`) so a name or source the lockfile never endorsed fails closed — the same control that gates [agent-emitted dependency ranges](agent-emitted-dependency-ranges.md) and [LLM-pinned vulnerable versions](llm-pinned-vulnerable-versions.md).

## Example

A poisoned `Makefile` redirects package resolution before the agent ever reads a package name:

**Before — Makefile redirects resolution to an attacker index:**

```makefile
setup:
	PIP_CONFIG_FILE=./.ci/pip.conf pip install -r requirements.txt
# .ci/pip.conf sets index-url to an attacker-controlled registry;
# every dependency now resolves from there, and setup.py runs at install
```

**After — the install is gated on a trusted source and a frozen lockfile:**

```makefile
setup:
	uv sync --frozen   # installs only what the committed lockfile endorses,
	                   # from the configured trusted index; an unlisted
	                   # name or source fails closed before any code runs
```

The first target hands resolution to the documentation; the second treats the manifest as a claim to verify against a lockfile the agent cannot silently rewrite.

## When this backfires

The threat is real but bounded, and a setup-doc-specific gate is redundant in several shapes:

- Committed lockfile with frozen installs (`npm ci`, `uv sync --frozen`): the doc-listed name or source never resolves, so the deviation fails closed without a separate check.
- Ephemeral, network-restricted, secret-free install sandboxes: install-time execution has nothing to exfiltrate and no persistence, so the payoff falls below the defense cost.
- Harnesses that already require per-command human approval before install catch most name-based attacks — a name-only check adds little there.
- Projects that pull only canonical, top-tier dependencies from a single trusted index have minimal exposure to the separator-confusion and registry-redirect classes.

The counter-argument is that an attacker who can edit your setup docs usually has repository write access and could inject a malicious code change directly. But documentation and CI-config changes draw less scrutiny than source diffs — the [Ultralytics compromise](https://blog.pypi.org/posts/2024-12-11-ultralytics-attack-analysis/) shipped a crypto-miner through an innocuously-titled pull request that exploited the project's GitHub Actions release pipeline ([Snyk](https://snyk.io/blog/ultralytics-ai-pwn-request-supply-chain-attack/)). The vector also covers third-party repositories an agent is told to clone and set up, where the attacker is the legitimate repo author and needs no intruder access at all.

## Key Takeaways

- Setup documentation is unverified install authority: an agent installs the names, sources, and versions the docs list without checking any of them ([arXiv:2607.15143](https://arxiv.org/abs/2607.15143)).
- The human threat model inverts — agents reliably catch blatant typosquats but miss source-based attacks like registry redirection almost everywhere, because malicious `--extra-index-url` uses are rare in training data.
- Install-time security is a harness-model property: a pre-execution checkpoint let one model refuse an untrusted registry 10/10, while the same model in a run-then-report harness dropped to 9/30.
- Prompting recovers only the dimension it names; a deterministic pre-install gate that verifies name, source, and version before any code runs caught 10 of 11 scenarios.
- Install-then-flag is not prevention — the install-time payload executes before any after-the-fact warning can fire.

## Related

- [Slopsquatting: Hallucinated Package Names as a Supply-Chain Vector](slopsquatting-hallucinated-package-names.md) — the name-based sibling where the model authors the bad name instead of an attacker authoring the doc
- [LLM-Pinned Library Versions Carry Systemic CVE Exposure](llm-pinned-vulnerable-versions.md) — the version dimension of the same install surface; pin against an external vulnerability source, not a training prior
- [Agent-Emitted Dependency Version Ranges Widen the Supply-Chain Attack Surface](agent-emitted-dependency-ranges.md) — floating ranges as a third leg of the agent-authored-manifest surface, closed by the same lockfile control
- [Improper Output Handling: Validate Agent Output Before Downstream Use](improper-output-handling-downstream-sinks.md) — the install sink is one of the downstream sinks that must be gated per-action
- [Pre-Trust Execution Surface in Coding Agent Harnesses](pre-trust-execution-surface.md) — the adjacent gap where project-local config executes before the trust prompt fires
