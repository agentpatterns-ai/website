---
title: "Fixed-Width Credential Assumptions in Agent Pipelines"
term: "Fixed-Width Credential Assumption"
description: "Code that validates, stores, or redacts a token by its length breaks when the issuer reshapes it. GitHub installation tokens went from 40 to about 520 characters."
tags:
  - anti-pattern
  - security
  - tool-agnostic
aliases:
  - fixed-length token validation
  - token length assumptions
  - credential width assumptions
last_reviewed: 2026-10-05
maturity: emerging
---

# Fixed-Width Credential Assumptions in Agent Pipelines

> Your agent authenticates with a credential whose width the issuer never promised, and GitHub finished changing it on October 2, 2026.

A fixed-width credential assumption is any code that constrains a token by its length or its full shape: a 40-character equality check, a `VARCHAR(64)` column, a gateway that caps header size, a redaction regex written against the old format. The credential's meaning does not change when the issuer reshapes it, so none of these break in a way that names the cause.

The rule carries a condition, and inverting it is the expensive mistake. Treat a credential as opaque when you store, forward, or validate it. Detection is the exception. Scanners, log scrubbers, and pre-commit hooks exist to match credentials. GitHub added the `ghs_` prefix in 2021 for that job. With the prefix alone, it anticipated "the false positive rate for secret scanning will be down to 0.5%" ([GitHub Engineering, 2021](https://github.blog/engineering/platform-security/behind-githubs-new-authentication-token-formats/)). Match on the prefix with an open-ended body and ignore the width.

## What the rollout changed

GitHub finished moving installation tokens to a stateless format on October 2, 2026. "Installation tokens still start with the `ghs_` prefix, but they're now about 520 characters long instead of 40." Nothing else moved with the width: "Token permissions, repository scoping, the one-hour expiration, and the installation access token REST API endpoint are unchanged" ([GitHub Changelog, 2026-10-02](https://github.blog/changelog/2026-10-02-stateless-github-app-installation-tokens-rolled-out)). GitHub's REST docs say "Authenticating with invalid credentials will initially return a `401 Unauthorized` response" ([GitHub Docs](https://docs.github.com/en/rest/authentication/authenticating-to-the-rest-api)), so a truncated token surfaces as an ordinary auth failure.

The same changelog names four places to audit:

- "Validation that requires tokens to be exactly 40 characters or patterns written for the legacy format."
- "Database columns, secret stores, or environment variables with a fixed or small maximum length."
- "Proxies, gateways, or middleware that truncate or reject long `Authorization` headers."
- "Logging and secret redaction rules that only match the legacy token pattern."

The fourth writes a live credential into your agent's logs and keeps working.

The staged rollout "began on April 27, 2026", and the `X-GitHub-Stateless-S2S-Token` override header that let integrators force either format "will be deprecated on November 30, 2026" (same source).

## Why it works

The issuer holds a documented degree of freedom over the credential's shape, so an assumption built on the unwritten part of that shape rests on a coincidence. RFC 6749 names both forms the issuer may pick between: a token "may denote an identifier used to retrieve the authorization information or may self-contain the authorization information in a verifiable manner (i.e., a token string consisting of some data and a signature)" ([RFC 6749 §1.4](https://www.rfc-editor.org/rfc/rfc6749.txt)). GitHub switched from the first form to the second. A self-contained token carries its claims inside the string, so the width grew while the semantics held. The same document states what a consumer may assume: "The access token string size is left undefined by this specification. The client should avoid making assumptions about value sizes" (§4.2.2). That contract dates from 2012, so the consumer broke the terms. The issuer did not change them.

## When this backfires

- Detection tooling inverts the rule. Deleting a token pattern from a scanner removes the control. GitHub's guidance is a corrected regex, and even that changed after publication: "Editor's note (May 26th, 2026): Updated the regex format guidance" ([GitHub Changelog, 2026-05-15](https://github.blog/changelog/2026-05-15-github-app-installation-tokens-per-request-override-header/)).
- Caps you do not own stay broken. Dropping a length assertion from your code does nothing about a gateway that rejects a long header or a secret store with a hard field limit. The storage figure is a floor: columns should "accept at least 520 characters" (same source).
- GitHub Enterprise Server is out of scope. "GitHub Enterprise Server isn't impacted by this change" (same source), so the general rule holds there but this remediation buys nothing.
- Presence checks are not the anti-pattern. An empty or obviously truncated secret rejected at startup fails earlier than a 401 from the API. Opaque means do not assume the width. It does not mean skip the check.
- Revocation is unaddressed. Neither changelog mentions it, so a harness that revokes its token in a post-job step should test that path. The unchanged list does not cover it.

## Example

**Before — a redaction rule keyed to the legacy width:**

```python
TOKEN_RE = re.compile(r"ghs_[A-Za-z0-9]{36}")
```

**After — the published pattern, anchored on the prefix with no upper bound:**

```python
TOKEN_RE = re.compile(r"ghs_[A-Za-z0-9\.\-_]{36,}")
```

GitHub gives the second as its "recommended regex to match both new and current format tokens" ([GitHub Changelog, 2026-05-15](https://github.blog/changelog/2026-05-15-github-app-installation-tokens-per-request-override-header/)). The first still matches legacy tokens, so nothing in a test suite built on fixtures goes red when it stops matching the tokens in production.

## Key Takeaways

- The issuer reserved the right to change the token's width and has now used it. Your code holds the only copy of the assumption that it would not.
- Audit four sites: validation, storage, the proxies on the request path, and redaction. Only the last fails silently.
- Invalid credentials return 401 Unauthorized ([GitHub Docs](https://docs.github.com/en/rest/authentication/authenticating-to-the-rest-api)). Check the token's length early in diagnosis.
- The header that lets you test both formats stops being honored on November 30, 2026, so the testing window is finite.

## Related

- [Secrets Management for AI Agents: Credential Injection](../../security/secrets-management-for-agents.md) — how the credential reaches the agent in the first place.
- [Sandbox Credential Masking: Authenticate Without Seeing the Secret](../../security/sandbox-credential-masking.md) — keeping the real token out of agent context entirely.
- [Credential Hygiene for Agent Skill Authorship](../../security/credential-hygiene-agent-skills.md) — the authoring-time half of the same leak surface.
- [AI Agents in CI/CD with Elevated Permissions and Untrusted Content (GitInject)](ai-agents-in-ci-cd-with-elevated-permissions.md) — what a leaked pipeline token buys an attacker.
