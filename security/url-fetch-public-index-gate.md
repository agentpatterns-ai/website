---
title: "Use a Public-Web Index to Gate Automatic URL Fetching"
description: "Cross-reference URLs against a public-web crawl index before fetching — URLs absent from the index may encode user-specific data and require manual approval."
tags:
  - agent-design
  - instructions
---
# Use a Public-Web Index to Gate Automatic URL Fetching

> Rather than maintaining a domain allow-list, cross-reference URLs against an independent public-web crawl index before allowing automatic fetching — URLs not in the index may encode user-specific data.

## The Safety Property

The key insight: a URL that was independently discoverable by a public crawler — one that had no access to any user's session, conversation, or account data — cannot by definition contain user-specific secrets that the crawler never saw.

This shifts the safety question from "is this domain reputable?" (a domain-level check) to "has this specific URL been independently observed on the public web?" (a URL-level check). [Source: [AI Agent Link Safety](https://openai.com/index/ai-agent-link-safety/)]

## Why Domain Allow-Lists Fail

Domain allow-lists are insufficient because:

- The attacker-crafted URL can point to a trusted domain that immediately redirects to an attacker-controlled destination
- Query parameters on a trusted domain can still encode user-specific data
- The breadth of legitimate web content means any reasonably permissive allow-list causes alert fatigue

Strict allow-lists train users to approve everything; loose allow-lists provide little protection. Neither approach handles redirects. [Source: [AI Agent Link Safety](https://openai.com/index/ai-agent-link-safety/)]

## How the Index Gate Works

An independent crawler builds the URL index with no access to user conversations, accounts, or session data. The index contains URLs the crawler discovered through public links.

At fetch time, the agent's tool checks the requested URL against this index:

- **URL found in index**: fetch can proceed automatically — the URL was publicly observable before this user session existed
- **URL not found in index**: treat as unverified — block automatic fetch, or surface to the user with an explicit warning requesting manual approval

The same check applies to embedded resources (images, iframes, script tags) — not just top-level navigation links. [Source: [AI Agent Link Safety](https://openai.com/index/ai-agent-link-safety/), [Exploiting Web Search Tools of AI Agents for Data Exfiltration](https://arxiv.org/abs/2510.09093)]

## Handling False Negatives

New URLs are continuously created. A legitimate URL that was published after the last crawl will not appear in the index. The correct response to a missing URL is user confirmation, not rejection:

> "This URL hasn't been seen by the public web index. Would you like to fetch it anyway?"

This preserves utility for new content while maintaining the safety property as the default.

## Comparison to Domain Allow-Lists

| Property | Domain Allow-List | Public Index Gate |
|----------|-------------------|-------------------|
| Handles redirects | No | Partially (depends on resolution before check) |
| Scales with web breadth | No — maintenance burden | Yes — crawl handles discovery |
| Alert fatigue | High | Lower — only new/unknown URLs trigger review |
| Provides safety against user-data encoding | No | Yes, for indexed URLs |

## Limitations

- Requires access to a URL index at fetch time (infrastructure dependency)
- Does not protect against injections that use only indexed URLs creatively
- Newly published URLs always require manual confirmation until crawled
- Redirect chains: the final destination URL must be checked after resolution, not just the initial URL [Source: [AI Agent Link Safety](https://openai.com/index/ai-agent-link-safety/)]

## Example

The following shows a Python fetch tool that wraps HTTP requests with an index gate. URLs found in the Common Crawl index proceed automatically; unknown URLs require explicit user confirmation.

```python
import httpx

COMMON_CRAWL_INDEX_API = "https://index.commoncrawl.org/CC-MAIN-2024-51-index"

def is_url_in_public_index(url: str) -> bool:
    """Check whether a URL has been independently crawled by Common Crawl."""
    response = httpx.get(
        COMMON_CRAWL_INDEX_API,
        params={"url": url, "output": "json", "limit": 1},
        timeout=5,
    )
    # A 200 response with content means the URL was found in the index
    return response.status_code == 200 and response.text.strip() != ""

def safe_fetch(url: str, require_confirmation: callable) -> httpx.Response | None:
    """
    Fetch a URL only if it appears in the public web index,
    or if the user explicitly approves an unknown URL.
    """
    if is_url_in_public_index(url):
        return httpx.get(url, follow_redirects=True, timeout=10)

    # URL not in index — surface to the user before proceeding
    approved = require_confirmation(
        f"This URL has not been seen by the public web index: {url}\n"
        "It may contain session-specific or user-specific data. Fetch anyway?"
    )
    if approved:
        return httpx.get(url, follow_redirects=True, timeout=10)
    return None
```

Using this tool in an agent context:

```python
# In the agent's tool definition, replace bare httpx.get with safe_fetch:
result = safe_fetch(
    url="https://example.com/user?token=abc123session",
    require_confirmation=lambda msg: ask_user_yes_no(msg),
)
```

A URL like `https://docs.python.org/3/library/os.html` is in the Common Crawl index and fetches automatically. A URL like `https://app.example.com/export?user_id=42&session=xyz` is not — the agent surfaces it to the user before fetching, because query parameters could encode session-specific data the crawler never saw.

## Key Takeaways

- A URL independently observable by a crawler with no user data cannot encode user-specific data the crawler never saw
- The safety question is "has this specific URL been publicly observed?" not "is this domain trusted?"
- URLs not in the index are blocked from automatic fetching or surfaced for manual user approval
- The same check applies to embedded resources, not just top-level navigation
- The index approach tolerates the breadth of the internet better than allow-lists and causes less alert fatigue

## Related

- [Guarding Against URL-Based Data Exfiltration](url-exfiltration-guard.md)
- [Discovering Indirect Injection Vulnerabilities in Your Agent](indirect-injection-discovery.md)
- [Tool-Invocation Attack Surface in Coding Agents](tool-invocation-attack-surface.md)
- [Blast Radius Containment: Least Privilege for AI Agents](blast-radius-containment.md)
- [Design Human-in-the-Loop Confirmation Gates for Consequential Agent Actions](human-in-the-loop-confirmation-gates.md)
- [Prompt Injection: A First-Class Threat to Agentic Systems](prompt-injection-threat-model.md)
- [Lethal Trifecta Threat Model for AI Agent Development](lethal-trifecta-threat-model.md)
