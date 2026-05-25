---
title: "Bootstrap URL Fetch Gate"
description: "Wrap WebFetch and equivalent URL-fetching tools with a public-web index check that lets crawler-observed URLs through automatically and surfaces user-specific or unknown URLs for explicit confirmation."
tags:
  - tool-agnostic
  - security
  - agent-design
aliases:
  - url fetch gate scaffold
  - common crawl url gate
  - public-index fetch gate
---

Packaged as: `.claude/skills/agent-readiness-bootstrap-url-fetch-gate/`

# Bootstrap URL Fetch Gate

> Wrap URL-fetching tools with a public-web index check; let crawler-observed URLs through automatically; surface unknown URLs for explicit confirmation.

!!! info "Harness assumption"
    The wrapper targets the agent's URL-fetching surface — `WebFetch` in Claude Code, the `fetch` MCP server elsewhere, or any custom tool that issues outbound HTTP. The index check is harness-agnostic: any wrapper that can intercept the URL before the request goes out can apply it. See [Assumptions](index.md#assumptions).

!!! info "Applicability"
    Apply when the agent has any URL-fetching capability **and** processes user input that could include URLs (issue bodies, PR comments, web search results). Skip for agents that fetch only from a hard-coded URL allowlist defined in repo config — those are already gated by static configuration.

The [Public-Web Index Gate](../security/url-fetch-public-index-gate.md) pattern shifts the safety question from "is this domain reputable?" to "has this URL been independently observed by a public crawler?" A URL absent from the index may encode session-specific data the crawler never saw. This runbook generates the wrapper, wires it into the harness, and validates the gate before declaring done.

## Step 1 — Detect Existing Fetch Surface

```bash
# Built-in fetch tools the harness exposes
grep -nE "WebFetch|web_fetch|fetch_url|http_get" \
  .claude/settings.json .claude/agents/*.md .claude/skills/*/SKILL.md 2>/dev/null

# MCP fetch servers
test -f .mcp.json && jq -r '.mcpServers | to_entries[] | select(.key | test("fetch|web|http")) | .key' .mcp.json

# Custom fetch implementations in scripts and tools
grep -rEn "httpx\.(get|post)|requests\.(get|post)|fetch\(" scripts/ tools/ src/ 2>/dev/null \
  | head -50
```

Capture every fetch site. The wrapper has to intercept all of them — a single un-wrapped `httpx.get` call is a bypass.

## Step 2 — Pick the Index Backend

Two production-grade public web indexes are available:

| Index | Endpoint | Latency | Coverage |
|-------|----------|--------:|---------|
| Common Crawl | `https://index.commoncrawl.org/CC-MAIN-<crawl>-index` | 200–800 ms | Monthly snapshot, ~3 B URLs |
| OpenAI's hosted gate (if available) | per [AI Agent Link Safety](https://openai.com/index/ai-agent-link-safety/) | sub-100 ms | Continuously updated |

Default to Common Crawl when no hosted gate is provisioned — it is the public reference implementation cited in [Public-Web Index Gate](../security/url-fetch-public-index-gate.md). Pin to a specific monthly crawl ID and document the pin in `AGENTS.md` so cache misses are explainable.

## Step 3 — Generate the Wrapper

Write `scripts/safe_fetch.py` (adapt to the project's language and harness):

```python
#!/usr/bin/env python3
"""Public-web index gate for URL fetching.

Wraps any HTTP fetch with a Common Crawl index check. URLs in the index
proceed automatically; unknown URLs surface to the user for confirmation
or are denied by default in non-interactive mode.

Source: docs/security/url-fetch-public-index-gate.md
"""
import os
import sys
import json
import httpx

CC_INDEX = os.environ.get(
    "CC_INDEX_URL",
    "https://index.commoncrawl.org/CC-MAIN-2026-05-index",
)
INTERACTIVE = sys.stdin.isatty() and os.environ.get("URL_GATE_NONINTERACTIVE") != "1"

def is_url_in_public_index(url: str) -> bool:
    try:
        r = httpx.get(
            CC_INDEX,
            params={"url": url, "output": "json", "limit": 1},
            timeout=5,
        )
    except httpx.RequestError:
        return False
    return r.status_code == 200 and r.text.strip() != ""

def safe_fetch(url: str) -> httpx.Response | None:
    # Resolve redirects before checking — the destination is what matters.
    head = httpx.head(url, follow_redirects=True, timeout=5)
    final_url = str(head.url)

    if is_url_in_public_index(final_url):
        return httpx.get(final_url, timeout=10)

    if not INTERACTIVE:
        print(json.dumps({
            "error": "url_not_in_public_index",
            "url": final_url,
            "remediation": "Re-run interactively or add to project URL allowlist.",
        }))
        return None

    print(f"URL not seen by public-web index: {final_url}")
    print("It may contain session- or user-specific data.")
    answer = input("Fetch anyway? [y/N]: ").strip().lower()
    return httpx.get(final_url, timeout=10) if answer == "y" else None

if __name__ == "__main__":
    resp = safe_fetch(sys.argv[1])
    sys.exit(0 if resp and resp.status_code < 400 else 1)
```

Three properties matter:

1. **Redirect resolution before check** — per [URL Fetch Public Index Gate §Limitations](../security/url-fetch-public-index-gate.md), checking only the initial URL misses redirect-based bypasses.
2. **Default-deny in non-interactive mode** — headless and CI agents cannot prompt. Failing closed prevents silent fetches.
3. **Embedded resources covered** — the wrapper has to be the only fetch path. Embedded images, iframes, and script src URLs go through the same gate.

## Step 4 — Wire the Wrapper

Three integration shapes:

### 4a. Replace direct fetch calls

Search/replace bare `httpx.get` and `requests.get` in agent-callable code paths with `safe_fetch`. Keep direct calls only in code that processes pre-validated URLs (e.g., a webhook receiver where the URL came from a signed source).

### 4b. PreToolUse hook (Claude Code)

Wire a hook that intercepts every `WebFetch` call:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "WebFetch",
        "hooks": [
          {
            "type": "command",
            "command": "python3 scripts/url_gate_check.py"
          }
        ]
      }
    ]
  }
}
```

Where `scripts/url_gate_check.py` reads the tool input from stdin, extracts the URL, calls `is_url_in_public_index`, and exits non-zero with a JSON body to deny per [Hooks Coverage](audit-hooks-coverage.md). Hook ordering rule: write and smoke-test the script before registering the hook (the write-before-wire rule from [`bootstrap-precompletion-hook`](bootstrap-precompletion-hook.md)).

### 4c. MCP server interposer

If the agent fetches through an MCP server, wrap the server's tool implementation rather than each agent. One enforcement point covers every client.

## Step 5 — Smoke Test

```bash
# Indexed URL — must succeed
python3 scripts/safe_fetch.py "https://docs.python.org/3/library/os.html"
echo "exit=$?"  # expect 0

# Unindexed user-specific URL — must fail in non-interactive
URL_GATE_NONINTERACTIVE=1 python3 scripts/safe_fetch.py \
  "https://app.example.com/export?user_id=42&session=xyz"
echo "exit=$?"  # expect 1

# Redirect to unindexed destination — must fail (final URL checked, not initial)
URL_GATE_NONINTERACTIVE=1 python3 scripts/safe_fetch.py \
  "https://httpbin.org/redirect-to?url=https://app.example.com/secret"
echo "exit=$?"  # expect 1
```

If any of the three cases produces the wrong exit code, the gate is broken — do not register the hook until they pass.

## Step 6 — Document the Bypass Path

The gate has a documented bypass: a user-approved fetch of an unindexed URL. Record this in `AGENTS.md` so reviewers know the gate is not absolute:

```markdown
## URL Fetch Gate

WebFetch is gated by `scripts/safe_fetch.py` (Common Crawl index, pinned to
CC-MAIN-2026-05). Unindexed URLs require interactive confirmation. For
legitimate URLs known to be missing (newly published, internal, embargoed),
add to `config/url-allowlist.txt` rather than disabling the gate.
```

The allowlist is read by `safe_fetch.py` before falling through to the index check. Keep it short — every entry is a permanent exception.

## Step 7 — Pair with Trifecta and Exfiltration Audits

The gate closes one leg of the [Lethal Trifecta](../security/lethal-trifecta-threat-model.md) — egress under untrusted input. Pair it with:

- [`audit-lethal-trifecta`](audit-lethal-trifecta.md) — re-run after the gate is wired; the egress leg should change from "unrestricted" to "indexed-or-confirmed".
- [`audit-mcp-control-plane-bypass`](audit-mcp-control-plane-bypass.md) — confirm no MCP server or subprocess bypasses the gate.
- The exfiltration patterns in [URL Exfiltration Guard](../security/url-exfiltration-guard.md) — the gate handles inbound URL fetching; exfiltration via outbound URL construction needs the complementary check.

## Idempotency

Re-running on an already-gated repo: the detection step finds the wrapper, the smoke test passes, no diff. Re-running after a regression (someone added a direct fetch call): Step 1 surfaces the new bypass site for re-wrapping.

## Output Schema

```markdown
# URL Fetch Gate — <repo>

| Component | State |
|-----------|-------|
| Wrapper script (`scripts/safe_fetch.py`) | present / generated |
| Index backend | <Common Crawl pin or hosted gate> |
| Hook registration | wired / pending |
| Smoke test | 3/3 passed |
| AGENTS.md note | present |
| Allowlist entries | <n> |

Bypass paths discovered: <count> (see Step 1 inventory)
```

## Related

- [Public-Web Index Gate for URL Fetching](../security/url-fetch-public-index-gate.md)
- [URL Exfiltration Guard](../security/url-exfiltration-guard.md)
- [Audit Lethal Trifecta](audit-lethal-trifecta.md)
- [Audit MCP Control-Plane Bypass](audit-mcp-control-plane-bypass.md)
- [Bootstrap Egress Policy](bootstrap-egress-policy.md)
- [Bootstrap Precompletion Hook](bootstrap-precompletion-hook.md)
