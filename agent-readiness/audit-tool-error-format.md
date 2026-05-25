---
title: "Audit Tool Error Format"
description: "Probe every agent-facing tool and HTTP endpoint, validate error responses against RFC 9457 application/problem+json with retryable, retry_after, and error_category extension fields, emit per-tool findings."
tags:
  - tool-agnostic
  - tool-engineering
  - cost-performance
aliases:
  - RFC 9457 audit
  - machine-readable error audit
  - problem+json audit
---

Packaged as: `.claude/skills/agent-readiness-audit-tool-error-format/`

# Audit Tool Error Format

> Probe every agent-facing tool and HTTP endpoint, validate error responses against RFC 9457 with operational extension fields, emit per-tool findings on token cost and recovery surface.

!!! info "Harness assumption"
    Applies to two surfaces: (1) HTTP APIs the agent calls outbound (third-party services, internal microservices), and (2) tools the project itself exposes to agents (MCP servers, REST endpoints documented in `AGENTS.md`). See [`rfc9457-machine-readable-errors`](../tool-engineering/rfc9457-machine-readable-errors.md).

!!! info "Applicability"
    Skip for projects whose only agent-facing surface is local filesystem and shell — there are no HTTP errors to format. Apply when the agent calls or exposes HTTP endpoints.

When an agent receives an HTML error page instead of a structured response, it must pattern-match through markup to extract status and guess retry behavior. A Cloudflare 1015 rate-limit page is ~14,252 tokens as HTML; the same information as RFC 9457 JSON is ~256 tokens — a 55× reduction. At scale, HTML errors burn context and produce unreliable recovery logic. Rules from [`rfc9457-machine-readable-errors`](../tool-engineering/rfc9457-machine-readable-errors.md).

## Step 1 — Enumerate Endpoints

```bash
# MCP servers and tools the project exposes
test -f .mcp.json && jq '.servers // .mcpServers | to_entries[] | {name:.key, command:.value.command}' .mcp.json

# Endpoints documented in AGENTS.md or tools docs
grep -rE "^[A-Z]+\s+/.*$|https?://" AGENTS.md docs/ 2>/dev/null | grep -vE "https?://github|https?://example" | sort -u

# Outbound HTTP calls the agent makes (best-effort)
grep -rE "WebFetch|httpx|requests\.(get|post)|fetch\(" .claude/skills/ scripts/ 2>/dev/null | head -20
```

Capture each as `{name, kind, base_url}`. If no endpoints are found, skip to the report — nothing to audit.

## Step 2 — Probe Each Endpoint for Error Responses

For each endpoint, induce a deterministic error and capture the response. Three reproducible error classes:

| Error | How to induce | Expected RFC 9457 fields |
|-------|---------------|---------------------------|
| 4xx auth | omit auth header | `status:401`, `error_category:access_denied`, `owner_action_required:true` |
| 4xx not found | request invalid resource id | `status:404`, `error_category:not_found`, `retryable:false` |
| 4xx rate limit | exceed published rate limit | `status:429`, `error_category:rate_limit`, `retryable:true`, `retry_after:<int>` |

```bash
probe() {
  local url="$1" method="$2" headers="$3"
  curl -sS -w '\n%{http_code}\n%{content_type}\n' -X "$method" $headers "$url" 2>&1
}

# Auth probe — omit header that would normally be required
probe "$BASE/protected" GET ""

# Always include the Accept header to request structured errors
probe "$BASE/anything" GET "-H 'Accept: application/problem+json'"
```

Capture response body, status code, and content type for each probe.

## Step 3 — Validate the Response Body

For each captured response with status ≥ 400, validate:

```bash
validate_problem_json() {
  local body="$1" content_type="$2"
  local findings=()

  # Content type
  echo "$content_type" | grep -q 'application/problem+json' \
    || findings+=("medium|content-type is '$content_type', not application/problem+json|set Content-Type: application/problem+json")

  # Body parses as JSON
  echo "$body" | jq -e . >/dev/null 2>&1 \
    || { findings+=("high|response body is not JSON|emit RFC 9457 problem+json instead of HTML"); printf '%s\n' "${findings[@]}"; return; }

  # Required base fields
  for field in type status title; do
    [[ "$(echo "$body" | jq -r ".$field // empty")" ]] \
      || findings+=("medium|missing required RFC 9457 field: $field|add $field")
  done

  # Operational extension fields
  for field in retryable error_category; do
    [[ "$(echo "$body" | jq -r ".$field // empty")" ]] \
      || findings+=("medium|missing operational field: $field|add $field for agent control flow")
  done

  # Rate-limit-specific
  status=$(echo "$body" | jq -r '.status // 0')
  if [[ "$status" == "429" ]]; then
    [[ "$(echo "$body" | jq -r '.retry_after // empty')" ]] \
      || findings+=("high|429 response missing retry_after|agent cannot back off without explicit interval")
  fi

  printf '%s\n' "${findings[@]}"
}
```

## Step 4 — Token-Cost Sample

Compare error-response token cost. The audit fails if any error response exceeds 1000 tokens — the threshold above which the response itself crowds the agent's recovery context.

```bash
TOKENS=$(echo "$body" | python3 -c "import sys, tiktoken; enc=tiktoken.get_encoding('cl100k_base'); print(len(enc.encode(sys.stdin.read())))")
[[ $TOKENS -gt 1000 ]] && echo "high|$endpoint|error response is $TOKENS tokens|exceed 1000-token recovery budget; switch to RFC 9457 JSON"
[[ $TOKENS -gt 250 && $TOKENS -le 1000 ]] && echo "low|$endpoint|error response is $TOKENS tokens|reasonable but consider trimming detail field"
```

## Step 5 — Verify Accept-Header Honored

Some endpoints emit HTML even when the client requests JSON. Probe each endpoint twice — once with `Accept: application/problem+json`, once without — and flag any endpoint that ignores the negotiation:

```bash
WITH=$(probe "$BASE/auth-fail" GET "-H 'Accept: application/problem+json'")
WITHOUT=$(probe "$BASE/auth-fail" GET "")
echo "$WITH" | grep -q '^Content-Type: application/problem+json' \
  || echo "high|$endpoint|ignores Accept: application/problem+json|honor the negotiation header"
```

## Step 6 — Per-Endpoint Scorecard

```markdown
# Audit Report — Tool Error Format

## Per-endpoint scorecard

| Endpoint | Content-type | Base fields | retryable | error_category | retry_after (429) | Tokens | Top issue |
|----------|:------------:|:-----------:|:---------:|:--------------:|:-----------------:|------:|-----------|
| /v1/foo | ✅ | ✅ | ⚠️ | ❌ | n/a | 312 | <one-line> |

## Findings

| Severity | Endpoint | Finding | Suggested fix |
|----------|----------|---------|---------------|
| high | /v1/bar | error response is 14,000 tokens HTML | switch to RFC 9457 JSON |
```

## Idempotency

Read-only with respect to the project under audit. Probes generate API requests against the target endpoints — rate-limit and auth-failure probes hit real endpoints; coordinate with the operator before running against production.

## Output Schema

```markdown
# Audit Tool Error Format — <repo>

| Endpoints | Pass | Warn | Fail | HTML errors |
|----------:|-----:|-----:|-----:|-----------:|
| <n> | <n> | <n> | <n> | <n> |

Top fix: <one-liner — usually missing operational fields>
```

## Remediation

For each endpoint emitting HTML or missing fields, file an issue with the suggested fix and the captured response sample. The fix is a server-side change — out of scope for an in-repo bootstrap. If the project owns the endpoint, the fix template is:

```python
# Example: FastAPI middleware emitting RFC 9457 problem+json
@app.exception_handler(RateLimitError)
async def rate_limit_handler(request, exc):
    return JSONResponse(
        status_code=429,
        media_type="application/problem+json",
        content={
            "type": "https://errors.example.com/rate-limit",
            "status": 429,
            "title": "Rate Limit Exceeded",
            "detail": str(exc),
            "instance": str(request.url),
            "retryable": True,
            "retry_after": exc.retry_after,
            "error_category": "rate_limit",
        },
    )
```

## Related

- [Machine-Readable Error Responses (RFC 9457)](../tool-engineering/rfc9457-machine-readable-errors.md)
- [Token-Efficient Tool Design](../tool-engineering/token-efficient-tool-design.md)
- [Tool Description Quality](../tool-engineering/tool-description-quality.md)
- [Audit Tool Descriptions](audit-tool-descriptions.md)
- [Self-Healing Tool Routing](../tool-engineering/self-healing-tool-routing.md)
