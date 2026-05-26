---
title: "Audit LLM-Pinned Vulnerable Dependency Versions"
description: "Enumerate dependency manifests authored by agents, query each pinned version against OSV and GitHub Advisories, and flag pins that are both CVE-vulnerable and cleanly patch-upgradable — the canonical signature of training-prior dependency selection."
tags:
  - tool-agnostic
  - security
  - dependencies
aliases:
  - LLM pinned vulnerable versions audit
  - agent dependency CVE audit
  - LLM-specified library version scan
last_reviewed: 2026-05-27
---

Packaged as: `.claude/skills/agent-readiness-audit-llm-pinned-versions/`

# Audit LLM-Pinned Vulnerable Dependency Versions

> Enumerate dependency manifests authored by agents, query each pinned version against OSV and GitHub Advisories, and flag pins that are both CVE-vulnerable and cleanly patch-upgradable — the canonical signature of training-prior dependency selection.

!!! info "Harness assumption"
    In-scope dependency manifests: Python (`requirements.txt`, `pyproject.toml`, `Pipfile`, `setup.py`), JavaScript (`package.json`, `package-lock.json`), Go (`go.mod`), Rust (`Cargo.toml`, `Cargo.lock`), Ruby (`Gemfile`), Java (`pom.xml`, `build.gradle`). The audit reads agent-authored commits identified by the same principal-detection pattern as [`audit-agent-pr-quality-metrics`](audit-agent-pr-quality-metrics.md) (bot author login, branch prefix `copilot/` `claude/` `cursor/`, or commit trailer). See [Assumptions](index.md#assumptions).

!!! info "Applicability"
    Skip when all dependency changes are human-curated and reviewed before merge, or when an existing tool (`pip-audit`, `npm audit`, Dependabot, Renovate, Artifactory/Nexus curated mirror) already blocks vulnerable installs as a hard CI gate. Run when agents author dependency files directly, when CI uses an advisory-only `npm audit` that does not block, or after enabling an agent class with dependency-write authority. The [`llm-pinned-vulnerable-versions`](../security/llm-pinned-vulnerable-versions.md) source page measures 36.7%–55.7% of LLM-specified versions as CVE-bearing across ten models, with 72.27%–91.37% of those CVEs disclosed before the model's training cutoff.

The LLM-pinned-vulnerable-versions class is a training-distribution artifact, not a per-model defect ([`llm-pinned-vulnerable-versions`](../security/llm-pinned-vulnerable-versions.md)). Models learn a co-occurrence prior over `(library, version-string)` pairs from Stack Overflow and tutorial blogs; the prior anchors on whichever version was popular when the most-upvoted answer was written, with no signal path from the CVE feed. All ten models in Wang et al. (May 2026) converge on the same risky releases ([arXiv:2605.06279](https://arxiv.org/abs/2605.06279)) — "use a better model" is not a remediation. The audit converts the externally-anchored remediations from that page into mechanical checks.

## Step 1 — Identify Agent-Authored Dependency-Manifest Commits

Use the principal-detection pattern from [`audit-agent-pr-quality-metrics`](audit-agent-pr-quality-metrics.md) (bot author, branch prefix, commit trailer). Then narrow to commits that touch a dependency manifest.

```bash
MANIFEST_PATHS='requirements.txt|pyproject.toml|Pipfile|setup.py|package.json|package-lock.json|go.mod|Cargo.toml|Cargo.lock|Gemfile|pom.xml|build.gradle'

# Agent-authored commits in the last 90 days that touch a manifest
git log --since="90 days ago" --format="%H|%ae|%s" --name-only \
  | awk -v RS='' -v p="$MANIFEST_PATHS" '
      NR==FNR { next }
      /\|/ { meta=$0; next }
      $0 ~ p { print meta "|" $0 }' \
  | grep -iE 'bot@|claude|copilot|cursor|aider|Agent-Session:' \
  > /tmp/agent-manifest-commits.tsv

# Or: GitHub PR-driven detection (more reliable when branches are pruned)
gh pr list --state merged --limit 500 \
  --json number,author,headRefName,files,mergedAt \
  --jq '.[] | select(
        (.author.login | test("bot|claude|copilot|cursor"; "i")) or
        (.headRefName | test("^(copilot|claude|cursor|aider)/"; "i"))
      ) | {pr: .number, files: [.files[].path | select(test("'"$MANIFEST_PATHS"'"))]}
    | select(.files | length > 0)' \
  > /tmp/agent-manifest-prs.json
```

Capture per-commit metadata: SHA, author, merge date, model identifier if available from the commit trailer (per [`bootstrap-agent-commit-attribution`](bootstrap-agent-commit-attribution.md)). Model ID is load-bearing for Step 5.

## Step 2 — Extract Pinned Versions per Manifest

The pin format varies by ecosystem. Treat exact pins (`==`, `=`, `~`, literal version) as in-scope; ignore unbounded ranges (`>=`, `^`, `~>`) which delegate to the resolver.

```bash
# Python: requirements.txt-style
extract_python_pins() {
  local f="$1"
  grep -E '^[A-Za-z0-9_.\-]+==[0-9]' "$f" \
    | sed -E 's/[[:space:]]*#.*//' \
    | awk -F'==' '{print "python|" FILENAME "|" $1 "|" $2}' FILENAME="$f"
}

# Python: pyproject.toml (PEP 621 / Poetry)
extract_pyproject_pins() {
  python3 -c '
import sys, tomllib
data = tomllib.load(open(sys.argv[1], "rb"))
deps = data.get("project", {}).get("dependencies", []) \
     + list(data.get("tool", {}).get("poetry", {}).get("dependencies", {}).items())
for d in deps:
    if isinstance(d, str) and "==" in d:
        name, ver = d.split("==", 1)
        print(f"python|{sys.argv[1]}|{name.strip()}|{ver.split(\";\")[0].strip()}")
    elif isinstance(d, tuple) and isinstance(d[1], str) and d[1].startswith("=="):
        print(f"python|{sys.argv[1]}|{d[0]}|{d[1][2:]}")
' "$1"
}

# JavaScript: package.json
extract_npm_pins() {
  jq -r --arg f "$1" '
    (.dependencies // {}) + (.devDependencies // {}) | to_entries[]
    | select(.value | test("^[0-9]"))
    | "npm|\($f)|\(.key)|\(.value)"' "$1"
}

# Go: go.mod
extract_go_pins() {
  awk -v f="$1" '
    /^require / && /v[0-9]/ { gsub(/[()"]/, ""); print "go|" f "|" $2 "|" $3 }
    /^\t[a-z]/ && /v[0-9]/ { print "go|" f "|" $1 "|" $2 }' "$1"
}

# Rust: Cargo.toml
extract_cargo_pins() {
  python3 -c '
import sys, tomllib
data = tomllib.load(open(sys.argv[1], "rb"))
for section in ("dependencies", "dev-dependencies", "build-dependencies"):
    for name, spec in data.get(section, {}).items():
        ver = spec if isinstance(spec, str) else spec.get("version", "")
        if ver and ver[0].isdigit():
            print(f"cargo|{sys.argv[1]}|{name}|{ver}")
' "$1"
}
```

Emit one normalized record per pin: `ecosystem|file|package|version`. Feed the next step.

## Step 3 — Query OSV for Known CVEs at Each Pin

[OSV.dev](https://osv.dev/) is the canonical aggregator — single schema across PyPI, npm, Go, crates.io, RubyGems, Maven. The free API ([api.osv.dev](https://google.github.io/osv.dev/api/)) has no auth and accepts batch queries.

```bash
# Map ecosystem to OSV ecosystem name
osv_ecosystem() {
  case "$1" in
    python) echo "PyPI" ;;
    npm) echo "npm" ;;
    go) echo "Go" ;;
    cargo) echo "crates.io" ;;
    gem) echo "RubyGems" ;;
    maven) echo "Maven" ;;
  esac
}

# Single-pin query
while IFS='|' read -r eco file pkg ver; do
  osv_eco=$(osv_ecosystem "$eco")
  result=$(curl -sS -X POST https://api.osv.dev/v1/query \
    -H "Content-Type: application/json" \
    -d "$(jq -n --arg p "$pkg" --arg v "$ver" --arg e "$osv_eco" \
      '{package: {name: $p, ecosystem: $e}, version: $v}')")
  vulns=$(echo "$result" | jq -r '.vulns // [] | length')
  if [[ "$vulns" -gt 0 ]]; then
    echo "$result" | jq -r --arg pkg "$pkg" --arg ver "$ver" --arg file "$file" '
      .vulns[] | "\($file)|\($pkg)|\($ver)|\(.id)|\(.summary // "no summary")|\(.database_specific.severity // .severity[0].score // "unknown")"'
  fi
done < /tmp/pins.tsv > /tmp/cve-hits.tsv
```

Cross-check critical-severity hits against the [GitHub Advisory Database](https://github.com/advisories) via `gh api`. OSV ingests GHSA but the GitHub-side severity classification (`CRITICAL`/`HIGH`/`MODERATE`/`LOW`) is more consistent than OSV's mixed CVSS-vector data:

```bash
gh api graphql -f query='
  query($ghsa: String!) {
    securityAdvisory(ghsaId: $ghsa) { severity, cvss { score } }
  }' -f ghsa="$GHSA_ID"
```

## Step 4 — Compute Clean Patch Upgrade per CVE Hit

A hit is actionable only when a non-major patch upgrade exists that clears the CVE. Major-version bumps fall outside the audit's remediation scope — they require migration work, not a pin change.

```bash
# For each CVE hit, find the smallest version >= pin that clears every CVE on that pin
while IFS='|' read -r file pkg ver ghsa summary sev; do
  current_major=$(echo "$ver" | awk -F. '{print $1}')

  # Fetch all versions and their CVE status for this package
  fixed_versions=$(curl -sS "https://api.osv.dev/v1/query" -X POST \
    -d "$(jq -n --arg p "$pkg" --arg e "PyPI" '{package: {name:$p, ecosystem:$e}}')" \
    | jq -r --arg id "$ghsa" '.vulns[] | select(.id == $id) | .affected[].ranges[].events[]
        | select(.fixed) | .fixed')

  for fix in $fixed_versions; do
    fix_major=$(echo "$fix" | awk -F. '{print $1}')
    if [[ "$fix_major" == "$current_major" ]]; then
      echo "high|$file|$pkg|$ver -> $fix|$ghsa|$sev|clean patch upgrade clears CVE"
      break
    fi
  done

  # No same-major fix exists
  if [[ -z "$fix_major" || "$fix_major" != "$current_major" ]]; then
    echo "medium|$file|$pkg|$ver|$ghsa|$sev|fix requires major-version bump — escalate to migration backlog"
  fi
done < /tmp/cve-hits.tsv
```

`pip index versions <pkg>`, `npm view <pkg> versions`, `go list -m -versions <module>`, and `cargo search <crate>` are local alternatives when offline. The OSV `affected.ranges[].events[].fixed` field is the authoritative source.

## Step 5 — Cross-Reference Model Knowledge-Cutoff

The [`llm-pinned-vulnerable-versions`](../security/llm-pinned-vulnerable-versions.md) finding most likely to apply is the **before-cutoff** pin: 72.27%–91.37% of agent-pinned CVE-bearing versions had their CVE disclosed before the model's training cutoff. A pin where the CVE predates the model's cutoff is stronger evidence of training-distribution bias than a generic CVE hit.

```bash
# Model-cutoff lookup table (extend per harness)
declare -A MODEL_CUTOFF=(
  ["claude-3-5-sonnet"]="2024-04-01"
  ["claude-3-7-sonnet"]="2024-11-01"
  ["claude-opus-4"]="2025-03-01"
  ["claude-opus-4-7"]="2026-01-01"
  ["gpt-4o"]="2023-10-01"
  ["gpt-4-turbo"]="2023-12-01"
  ["gpt-5"]="2024-09-01"
  ["gemini-1-5-pro"]="2024-05-01"
  ["gemini-2-0-flash"]="2024-08-01"
)

# CVE disclosure date via OSV (published field)
get_cve_disclosure() {
  curl -sS "https://api.osv.dev/v1/vulns/$1" | jq -r '.published'
}

# Promote severity when CVE disclosure predates model cutoff
while IFS='|' read -r sev file pkg upgrade ghsa cvss reason; do
  model=$(grep -oE 'Model: [a-z0-9.-]+' /tmp/agent-manifest-commits.tsv | sort -u | head -1 | cut -d' ' -f2)
  cutoff="${MODEL_CUTOFF[$model]}"
  disclosed=$(get_cve_disclosure "$ghsa")

  if [[ -n "$cutoff" && -n "$disclosed" && "$disclosed" < "$cutoff" ]]; then
    echo "high|$file|$pkg|$upgrade|$ghsa|$cvss|CVE disclosed $disclosed before model cutoff $cutoff — training-prior bias signal"
  else
    echo "$sev|$file|$pkg|$upgrade|$ghsa|$cvss|$reason"
  fi
done < /tmp/staged-findings.tsv
```

A finding without a model identifier is still actionable as a generic CVE — the cutoff cross-reference is signal-strength, not a gate.

## Step 6 — Findings Output

```markdown
| Severity | Manifest | Pin | Upgrade | CVE | CVSS | Reason |
|----------|----------|-----|---------|-----|------|--------|
```

Decision rule per [`llm-pinned-vulnerable-versions`](../security/llm-pinned-vulnerable-versions.md) and the issue spec:

- `high` — pin is CVE-vulnerable AND clean patch upgrade exists AND (model cutoff predates CVE disclosure OR no model attribution available with CVSS ≥ 7.0). Both legs of the decision rule fire.
- `medium` — pin is CVE-vulnerable but only a major-version bump clears it (migration backlog), or CVE disclosed after model cutoff (CVE is post-training; not training-prior bias)
- `low` — pin matches a CVE marked withdrawn or disputed, or the manifest is in a non-production path (`tests/`, `examples/`, `scripts/dev-*`)
- `info` — agent-authored manifest with no CVE-vulnerable pin; the fact that the project surfaces principal attribution at all is a positive signal

## Step 7 — Emit Report

```markdown
# Audit Report — LLM-Pinned Vulnerable Versions

> Window: last 90 days. Agent-authored manifest commits: <n>. Pins inspected: <n>.
> Findings: <high> high, <medium> medium, <low> low.

| Severity | Manifest | Package | Pin → Fix | CVE | Reason |
|----------|----------|---------|-----------|-----|--------|

## Top fix

Wire `pip-audit` / `npm audit --audit-level=high` / `govulncheck` / `cargo audit` as a
blocking CI gate on agent-authored PRs. Manifests become hints validated against
external CVE state, not source-of-truth. See [`llm-pinned-vulnerable-versions`](../security/llm-pinned-vulnerable-versions.md)
§What to Change.
```

## Idempotency

Read-only. The OSV API is unauthenticated and rate-limited at 1000 requests/minute per IP — batch via `POST /v1/querybatch` for large manifests ([OSV batch endpoint docs](https://google.github.io/osv.dev/post-v1-querybatch/)).

## Remediation

The remediations from [`llm-pinned-vulnerable-versions`](../security/llm-pinned-vulnerable-versions.md) §What to Change apply directly. None require the model to learn anything new about CVEs — every effective anchor routes around the model's prior:

- **CVE-aware install-time gate** — [`pip-audit`](https://pypi.org/project/pip-audit/), `npm audit --audit-level=high`, [`govulncheck`](https://pkg.go.dev/golang.org/x/vuln/cmd/govulncheck), [`cargo audit`](https://rustsec.org/) as a blocking CI step
- **Dependabot or Renovate** — auto-bump after merge so pins stay current with the CVE feed regardless of what the model picked at write time ([Dependabot security updates](https://docs.github.com/en/code-security/concepts/supply-chain-security/about-dependabot-security-updates))
- **Curated mirror** — Artifactory or Nexus filters block vulnerable versions at install time; the agent's pin is dead-on-arrival if it points at a blocked release
- **Lock-then-resolve workflow** — pipe the manifest through `pip-compile` / `uv lock` / `poetry lock` in a clean environment; the same workflow that closes the missing-dependency gap ([Dependency Gap Validation](../verification/dependency-gap-validation.md)) surfaces vulnerable transitive pulls

## Related

- [LLM-Pinned Library Versions Carry Systemic CVE Exposure](../security/llm-pinned-vulnerable-versions.md) — the source finding; measured CVE incidence and the training-prior mechanism
- [Audit Agent-Built Code Health](audit-agent-built-code-health.md) — sibling audit on structural quality of agent output; this audit covers the dependency surface
- [Audit Secrets in Context](audit-secrets-in-context.md) — sibling security audit on the credential surface; runs before this audit and halts on a high finding
- [Audit Agent PR Quality Metrics](audit-agent-pr-quality-metrics.md) — source of the agent-authored-commit detection pattern
- [Bootstrap Agent Commit Attribution](bootstrap-agent-commit-attribution.md) — wires the commit trailers (`Agent-Session`, `Model`, `Task-Reference`) that make Step 5's model-cutoff cross-reference reliable
- [Dependency Gap Validation for AI-Generated Code](../verification/dependency-gap-validation.md) — the missing-dependency complement; lock-then-resolve workflow surfaces transitive CVEs

## Sources

- [arXiv:2605.06279](https://arxiv.org/abs/2605.06279) — Wang et al. (May 2026): "Correct Code, Vulnerable Dependencies: A Large Scale Measurement Study of LLM-Specified Library Versions"
- [OSV.dev API documentation](https://google.github.io/osv.dev/api/) — schema and rate-limit details
- [GitHub Advisory Database](https://github.com/advisories) — GHSA-id severity classification
- [pip-audit](https://pypi.org/project/pip-audit/), [govulncheck](https://pkg.go.dev/golang.org/x/vuln/cmd/govulncheck), [cargo audit](https://rustsec.org/) — install-time CVE gates
