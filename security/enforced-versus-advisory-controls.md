---
title: "Enforced Versus Advisory Controls in LLM-Native IDEs"
term: "Enforced Versus Advisory Controls"
description: "Sort agent safeguards by where they are evaluated: the runtime enforces permissions and sandboxes, while ignore files and rules files are resolved inside the model's context and lose to the task."
aliases:
  - advisory controls
  - enforced controls
  - LLM-native IDE security issues
tags:
  - security
  - agent-design
  - human-factors
  - tool-agnostic
  - arxiv
last_reviewed: 2026-08-28
maturity: emerging
---

# Enforced Versus Advisory Controls in LLM-Native IDEs

> A control the runtime evaluates bounds an LLM-native IDE. A control stated inside the model's context does not.

Sort every safeguard around a coding agent by where it gets evaluated. Filesystem permissions, container boundaries, and scoped credentials are checked outside the model, so the agent cannot argue with them. Ignore files, rules files, and prompt-level prohibitions are resolved by the model alongside the task, and they lose to it often enough to dominate the categories developers report.

## What developers actually report

A study collected 1.1M posts from 29 subreddits between January 2023 and March 2026 and narrowed them to 446 posts describing security or privacy failures in Cursor, Copilot, Codex, and Cline ([Akhond et al., 2026](https://arxiv.org/abs/2607.26390v3)). Where those reports land:

| Security category (297 posts) | Share |
|---|---|
| Unauthorized file operations | 43.1% |
| Operational safety, including production and system-level actions | 23.9% |
| Unsafe code generation | 18.2% |
| Violations of constraints the user set | 16.5% |
| Third-party tool integration | 4.7% |

| Privacy category (194 posts) | Share |
|---|---|
| Lack of transparency | 45.9% |
| Unauthorized data access, with secrets access at 14.4% | 23.7% |
| Privacy leakage, including exposed secrets | 15.5% |
| Unauthorized transmission and collection | 11.9% |
| Context integrity failures | 8.8% |

The authors summarize the split as "7 out of 10 security and privacy issues were system-level issues, and 2 were LLM-level issues" ([Akhond et al., 2026](https://arxiv.org/abs/2607.26390v3)). The failures trace to design choices about file access and autonomy, not to model reasoning.

## Sorting the safeguards

The same study coded 1,318 comments into 13 mitigation strategies ([Akhond et al., 2026](https://arxiv.org/abs/2607.26390v3)). Split them by where each is evaluated.

Enforced outside the model: sandboxed execution (105 comments), version control for rollback (232), local model hosting (94), session and memory isolation (56), and the permission half of secure IDE configuration.

Advisory, resolved inside the model's context: ignore files and rules files, which make up the other half of secure IDE configuration. Configuration is the most-adopted category of the 13 at 501 comments, and it mixes the two kinds together.

Four independent records show the advisory half failing. The study's opening case has a developer block a `.env` file in Copilot, after which Copilot "read and attempted to modify the `.env` file, ignoring the configured access restrictions" ([Akhond et al., 2026](https://arxiv.org/abs/2607.26390v3)). Cursor documents the same ceiling as designed behavior: "The terminal and MCP server tools used by Agent cannot block access to code governed by `.cursorignore`" ([Cursor Docs](https://cursor.com/docs/reference/ignore-file)). A published advisory shows an attacker can invalidate an existing ignore configuration by writing a new cursorignore file ([GHSA-vhc2-fjv4-wqch](https://github.com/cursor/cursor/security/advisories/GHSA-vhc2-fjv4-wqch)). A fourth record checks CLAUDE.md files directly. The paper extracted security rules from 481 public files. Only 4.4% had a matching built-in Claude Code control under the strictest standard (95% CI 2.6-6.7%), and 4-16% under looser matching. Two practitioners checked a sample independently and confirmed the count (["When 'Do Not' Is Not Deny," 2026](https://arxiv.org/abs/2608.23550)).

## Why it works

An instruction to the agent enters the same context window as the task, so it is resolved probabilistically against the goal rather than bounding it. A filesystem permission or a container boundary is checked by code the model never sees. The field data follows that split, concentrating where enforcement was delegated to the model ([Akhond et al., 2026](https://arxiv.org/abs/2607.26390v3)). Controlled measurement shows the same effect on a single failure class. Overeager-action rates run 5.4% to 27.7% on permissive-default harnesses. An ask-to-continue harness, which puts a consent event between proposal and execution, holds them to 0.2% to 4.5% ([Qu et al., 2026](https://arxiv.org/abs/2605.18583v1)).

## When this backfires

- Outbound risk. Lack of transparency and unauthorized transmission alone sum to 57.8% of the privacy reports, and nothing you contain locally changes what leaves the machine ([Akhond et al., 2026](https://arxiv.org/abs/2607.26390v3)).
- Rollback outside the working tree. Version control restores tracked files. It does not restore a production database, which is what Replit's agent deleted for one user ([The Register, 2025](https://www.theregister.com/2025/07/21/replit_saastr_vibe_coding_incident/)).
- Production-shaped work. Migrations and infrastructure tasks need real credentials, so the sandbox either blocks the task or holds the thing you meant to contain.
- Review capacity. Manual verification is the most-cited governance strategy at 239 comments, and it degrades to rubber-stamping once agent output exceeds what anyone reads carefully ([Akhond et al., 2026](https://arxiv.org/abs/2607.26390v3)).
- Report frequency is not incidence. The authors state that counts reflect discussion patterns rather than vulnerability rates, and that enterprise use and developers who do not publicly report issues are absent. The study's LLM pre-filter also reported 0.21 precision on its validation set, so these shares rank complaints rather than risk ([Akhond et al., 2026](https://arxiv.org/abs/2607.26390v3)).
- Supply chain above the IDE. Local enforcement did not stop malicious code, committed with an inappropriately scoped GitHub token, from shipping in version 1.84.0 of the Amazon Q extension for VS Code ([AWS Security Bulletin AWS-2025-015](https://aws.amazon.com/security/security-bulletins/AWS-2025-015/)).

## Example

The advisory form of a secrets control asks the agent not to look:

```
# .cursorignore
.env
.env.*
secrets/
```

Cursor states what that buys you: "While Cursor blocks ignored files, complete protection isn't guaranteed due to LLM unpredictability" ([Cursor Docs](https://cursor.com/docs/reference/ignore-file)).

The enforced form puts the secret somewhere the agent's file tools do not reach:

```bash
# secret lives outside the working tree; the agent reads only the process env
export API_KEY="$(cat ~/.config/app/api-key)"
npm start
```

Nothing here depends on the agent honoring a rule; the file is not in the repository.

## Key Takeaways

- Classify each safeguard by where it is evaluated: outside the model (permissions, sandboxes, scoped credentials, version control) or inside its context (ignore files, rules files, prompt prohibitions).
- Field reports put 43.1% of security complaints in unauthorized file operations and 14.4% of privacy complaints in agents reading secrets ([Akhond et al., 2026](https://arxiv.org/abs/2607.26390v3)).
- Use ignore files for noise reduction and never as a secret boundary; Cursor states its terminal and MCP tool paths cannot honor them ([Cursor Docs](https://cursor.com/docs/reference/ignore-file)).
- Local containment does not touch the vendor-side privacy categories, and transparency plus unauthorized transmission alone are 57.8% of privacy reports ([Akhond et al., 2026](https://arxiv.org/abs/2607.26390v3)).
- Commit often so tracked files are recoverable, and keep production credentials out of the agent's reach, because version control cannot undo a database deletion.

## Related

- [Permission Framework Choice Outweighs Model Choice for Limiting Overeager Actions](permission-framework-over-model.md) — controlled benchmark of the same enforcement effect on one failure class
- [Protecting Sensitive Files from Agent Context Access](protecting-sensitive-files.md) — the prescriptive control whose limits this page tests against field reports
- [Secrets Management for Agent Workflows](secrets-management-for-agents.md) — environment-variable injection as the enforced alternative to ignore files
- [Blast Radius Containment: Least Privilege for AI Agents](blast-radius-containment.md) — scoping the permissions that carry the enforced half
- [Four-Layer Taxonomy of Agent Security Risks](four-layer-agent-security-taxonomy.md) — design-side taxonomy to place these field-reported categories against
- [Delegating Dependabot Pull Request Triage to an Agent](../workflows/dependabot-pr-triage-delegation.md) — a vendor stating that its own approval panel is advisory, not enforced
- [Permission Gates That Deny the Agent's Own Cleanup (Denied Remediation Path)](../patterns/anti-patterns/denied-remediation-path.md) — a best-effort gate that stays advisory in one direction and enforcing in the other
- [Reading a Coding-Agent Vendor's Security Certificate](../verification/vendor-security-certification-scope.md) — how to check which of a vendor's named safeguards an outside auditor actually exercised
