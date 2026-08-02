---
title: "Internal Hostname Disclosure in Agent-Readable Context"
term: "Internal Hostname Disclosure"
description: "Internal hostnames, staging URLs, and private subdomains left in agent-readable instruction files hand an attacker a map of your infrastructure, not just a secret to steal."
tags:
  - security
  - agent-design
  - tool-agnostic
aliases:
  - internal hostname leakage
  - staging URL disclosure in agent files
  - private subdomain exposure
last_reviewed: 2026-07-13
maturity: adopted
---

# Internal Hostname Disclosure in Agent-Readable Context

> An internal hostname or staging URL left in a CLAUDE.md or MCP config is reconnaissance data — it names a target with no credential required.

Internal hostname disclosure is the exposure of a system's internal naming — hostnames, staging subdomains, or private-network identifiers such as `.local`, `.internal`, `.corp`, `staging-*`, `dev-*`, or a bastion/jump-host name — to a party not authorized to see them. CWE-200 groups "network status and configuration" among the categories of information this weakness covers ([CWE-200: Exposure of Sensitive Information to an Unauthorized Actor](https://cwe.mitre.org/data/definitions/200.html)). A hostname alone grants no access. It names where to look next, and naming the target is most of what reconnaissance is.

## Why this differs from a credential leak

A leaked API key is usable the moment it is found. A leaked hostname is not — it needs a further exploit, a further leaked credential, or a further misconfiguration before it yields anything. That is exactly why it survives casual review: nobody rotates a hostname the way they rotate a key, so once named it stays a target indefinitely. Security testing methodology treats this as the deliberate first phase of an assessment, not an afterthought: OWASP's Web Security Testing Guide places host and infrastructure fingerprinting in its Information Gathering category, the foundational step before any deeper test begins ([OWASP WSTG — Fingerprint Web Server](https://owasp.org/www-project-web-security-testing-guide/stable/4-Web_Application_Security_Testing/01-Information_Gathering/02-Fingerprint_Web_Server)). Attackers follow the same order: map the estate, then attack it.

## The naming patterns already targeted

Naming conventions that mark an environment as internal or pre-production are not obscure. They are common enough to ship as literal wordlist entries in mainstream reconnaissance tooling. SecLists, the security tester's standard wordlist collection, includes `staging`, `dev`, `internal`, and `bastion` among its top subdomain-enumeration tokens ([SecLists — subdomains-top1million-110000.txt](https://github.com/danielmiessler/SecLists/blob/master/Discovery/DNS/subdomains-top1million-110000.txt)), meaning automated recon already tries these tokens against a target's DNS before a human ever reads a leaked file. A `jumpbox` is the same category of asset as a listed bastion host, the two terms being used interchangeably for a hop server into a private network, and a pre-production label (`staging-*`, `dev-*`, `uat-*`) additionally signals an environment statistically more likely to run with weaker hardening than production.

Exposed source and configuration repositories confirm the pattern in practice. Coverage of git-exposure incidents groups what attackers pull from a leaked repo into three buckets: credentials, business logic, and "infrastructure intel — details about internal systems such as hostnames, IPs, ports, or architectural diagrams" ([The Hacker News — The Unusual Suspect: Git Repos, 2025](https://thehackernews.com/2025/07/the-unusual-suspect-git-repos.html)). Infrastructure intel is its own line item precisely because it has reconnaissance value independent of whether any credential leaked alongside it.

## Why agent-readable files are a live instance of an old problem

Text committed into a shared or published surface leaks at scale even when authors know better: GitHub's own scanning found more than 39 million secrets exposed across the platform in 2024 alone, the large majority slipping past push protection before being caught ([GitHub — the next evolution of GitHub Advanced Security](https://github.blog/security/application-security/next-evolution-github-advanced-security/)). Agent instruction files (`CLAUDE.md`, `AGENTS.md`, skill files, `.mcp.json`) are populated with real environment detail during setup so the agent can actually reach it, then travel the same three paths this corpus already documents for credentials in skill files: publication to a shared or community corpus, persistence in git history after a later edit removes the literal string, and verbatim reproduction when the agent echoes the file's contents into generated output ([Credential Hygiene for Agent Skill Authorship](credential-hygiene-agent-skills.md)). A staging hostname pasted into a setup instruction propagates through every one of those paths exactly like a credential would, except that it is not a credential, so credential-only scanning misses it.

## What to check and fix

- Extend the same regex sweep already run for credential-format strings to internal-naming patterns: `\.local\b|\.internal\b|\.corp\b|staging-[a-z]+\.|dev-[a-z]+\.|jumpbox|bastion` across `CLAUDE.md`, `AGENTS.md`, `.claude/agents/`, `.claude/skills/`, and `.mcp.json`.
- Replace a real internal hostname in a committed instruction file with a placeholder (`$STAGING_HOST`) and inject the real value at runtime — the same environment-injection pattern already used for credentials ([Secrets Management for Agent Workflows](secrets-management-for-agents.md)).
- Treat a hit as a low-severity, informational finding relative to a live credential — it maps the estate rather than granting access — but do not drop it: the same finding shortens the path for whoever later obtains or brute-forces a working credential against the now-named host.

## When this backfires

Not every internal-looking name is sensitive. Some teams intentionally publish a staging endpoint for external QA tooling, and a `.corp` string in a public style guide about naming conventions is not a leak. Flag by pattern, then confirm the flagged host is not already public and intentionally so before treating it as a finding — this is a judgment call at the edge, not a deterministic verdict on every match.

## Key Takeaways

- Internal hostname disclosure names a target; it grants no access on its own, which is why it survives review far longer than a credential does.
- The naming patterns that mark an environment as internal (`.local`, `.internal`, `.corp`, `staging-*`, `dev-*`, bastion or jumpbox names) are literal entries in mainstream reconnaissance wordlists — automated recon already tries them.
- Exposed source and configuration repositories are documented to leak "infrastructure intel" — hostnames, IPs, ports, architecture — as a category distinct from credentials.
- Agent-readable instruction files propagate a leaked hostname through the same three paths already documented for credentials in skill files: publication, git history, and verbatim agent reproduction.
- Treat a match as a low-severity informational note, not a High finding — but do not ignore it, and confirm a flagged host is not already intentionally public before reporting it.

## Related

- [Credential Hygiene for Agent Skill Authorship](credential-hygiene-agent-skills.md) — the credential-specific version of the same three propagation paths
- [Secrets Management for Agent Workflows](secrets-management-for-agents.md) — the environment-injection pattern this page reuses for hostnames
- [Protecting Sensitive Files from Agent Context](protecting-sensitive-files.md) — mechanical enforcement for keeping sensitive paths out of agent reads
- [OWASP LLM Top 10 (2025): Agent Security Crosswalk](owasp-llm-top-10-2025-agent-crosswalk.md) — LLM02:2025 Sensitive Information Disclosure, the framework category this risk sits under
