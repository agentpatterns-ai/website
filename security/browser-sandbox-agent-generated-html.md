---
title: "Browser Sandbox for Agent-Generated HTML (Sandboxed Iframe + Immutable CSP)"
term: "Browser Sandbox for Agent-Generated HTML"
description: "Run untrusted agent- or LLM-generated HTML in the browser by composing a sandboxed iframe, an immutable meta Content-Security-Policy, and a MessageChannel-scoped parent API."
tags:
  - security
  - tool-agnostic
aliases:
  - sandboxed iframe plus immutable CSP pattern
  - browser-native artifact sandbox
last_reviewed: 2026-06-23
maturity: emerging
---

# Browser Sandbox for Agent-Generated HTML (Sandboxed Iframe + Immutable CSP)

> Run untrusted agent- or LLM-generated HTML in the browser by composing a sandboxed iframe, an immutable meta CSP, and a MessageChannel-scoped parent API.

## When this pattern fits

The pattern fits when a coding agent emits a runnable HTML+JS artifact for execution inside an already-authenticated parent app, and all four hold:

- Blast radius bounded to the browser tab — no server-side state, file system, GPU, or background compute.
- Artifact delivered via `srcdoc` (or any path where you control the first bytes), so the `<meta>` CSP is parsed before any guest script runs.
- No need for `frame-ancestors`, the CSP `sandbox` directive, or `report-uri`/`report-to` — none of those work in a `<meta>` policy, per the CSP spec ([content-security-policy.com](https://content-security-policy.com/examples/meta/)).
- The parent never sets `sandbox="allow-scripts allow-same-origin"` — that combination lets the embedded document remove its own `sandbox` attribute ([MDN](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/iframe)).

If the parent stores significant private data and you can host artifacts on a separate origin, prefer the stronger Claude Artifacts shape (separate domain + HTTP-header CSP) discussed under 'When this backfires'.

## The three layers

Each layer closes a distinct browser primitive; pulling any one re-opens a known exfiltration path. The shape below mirrors the `datasette-apps` plugin Simon Willison launched in June 2026 ([Datasette Apps](https://simonwillison.net/2026/Jun/18/datasette-apps/), [launch post](https://datasette.io/blog/2026/datasette-apps/)).

### Layer 1: iframe sandbox attribute

```html
<iframe sandbox="allow-scripts allow-forms" srcdoc="..."></iframe>
```

`allow-scripts` permits JavaScript inside the frame; `allow-forms` permits in-frame form submission. Omitting `allow-same-origin` is load-bearing — without it, the embedded document is treated as a unique opaque origin that always fails the same-origin policy, so it cannot read DOM, cookies, or `localStorage` from the parent ([MDN: `<iframe>` sandbox](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/iframe)). What this does not stop: outbound `fetch()`, `<img>`, `<script src>`, or stylesheet loads to arbitrary external hosts — any of which can carry data in the URL ([Simon Willison: Datasette Apps](https://simonwillison.net/2026/Jun/18/datasette-apps/)).

### Layer 2: immutable meta CSP

```html
<meta http-equiv="Content-Security-Policy"
      content="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data: blob:;">
```

`default-src 'none'` collapses every fetch surface to "blocked." The two `'unsafe-inline'` exceptions re-enable inline scripts and styles the artifact ships with; `img-src data: blob:` permits in-page synthesized images without admitting any network origin. Once parsed, the policy is immutable: cross-browser testing on Chromium and Firefox confirms that JavaScript inside the iframe cannot remove, modify, or escape the `<meta>` tag, including via document replacement or `data:` URI navigation ([simonw/research: test-csp-iframe-escape](https://github.com/simonw/research/tree/main/test-csp-iframe-escape)).

### Layer 3: MessageChannel-scoped parent API

With layers 1–2 the iframe can do nothing useful. To open it back up safely, hand the child a single `MessagePort` at instantiation and expose only an allow-listed surface — for `datasette-apps`, that is read-only SQL plus admin-pre-registered stored-query writes ([Simon Willison: Datasette Apps](https://simonwillison.net/2026/Jun/18/datasette-apps/)). The parent verifies each request against its allow-list before executing it.

Prefer `MessageChannel` over raw `window.postMessage` for two reasons. First, the port reference is private — it never leaks to attacker-controlled code that ends up in the frame. Second, the channel auto-closes if the iframe navigates away, eliminating "child reloads to attacker code, channel still open" exploits ([MDN: MessageChannel](https://developer.mozilla.org/en-US/docs/Web/API/MessageChannel); [Simon Willison: Datasette Apps](https://simonwillison.net/2026/Jun/18/datasette-apps/)). If you must use raw `postMessage`, validate `event.source` and `event.origin` on every message ([MDN: postMessage security](https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage)).

## Why it works

The three layers are independent browser primitives that intersect on the threat. The sandbox attribute opaque-origins the frame, severing DOM and storage reach into the parent. The meta CSP is parsed at document-construction time, before any guest script runs; per the HTML spec and Simon's empirical cross-browser tests, the resulting policy is immutable for the lifetime of the document ([simonw/research: test-csp-iframe-escape](https://github.com/simonw/research/tree/main/test-csp-iframe-escape)). `default-src 'none'` then forces every fetch through the CSP allow-list, which is empty for external origins. The MessageChannel port is the only output surface left, and the parent only honors requests on a fixed allow-list. Pull any one layer and a known exfil channel opens — DOM read-back, network egress, or arbitrary parent-side commands — so the defense-in-depth holds only when all three are present and configured exactly as above.

## When this backfires

- Sensitive parents with separate-domain hosting available. Claude Artifacts hosts each artifact on `claudeusercontent.com` and delivers CSP via HTTP header ([Claude Artifacts overview](https://www.securityscientist.net/blog/12-questions-and-answers-about-claude-artifacts/)). That shape engages cross-site browser process isolation, enables the `frame-ancestors` / `report-to` / CSP `sandbox` directives that `<meta>` cannot carry ([content-security-policy.com](https://content-security-policy.com/examples/meta/)), and removes any parse-order concern. For sensitive auth-bearing parents the separate-origin variant is the right default; same-domain `srcdoc` is the fallback when separate hosting is impractical.
- Users can add arbitrary origins to the CSP allow-list. Any allow-listed origin is a data egress channel. Simon's Claude Fable security review caught a real attack: a less-privileged user with `create-app` permission allow-listed their own server, then social-engineered an admin into running the app — the app inherited the admin's query authority and exfiltrated to the allow-listed origin ([Simon Willison: Datasette Apps](https://simonwillison.net/2026/Jun/18/datasette-apps/)). Gate CSP allow-list mutation to trusted operators only.
- The message bridge accepts arbitrary parent commands. A bridge that proxies untyped commands re-creates the original threat at a different layer. Datasette Apps explicitly limits the bridge to read-only SQL plus pre-registered stored-query writes, with the parent verifying both the database and the query name before executing ([Simon Willison: Datasette Apps](https://simonwillison.net/2026/Jun/18/datasette-apps/)).
- You need server-side state, file system, GPU, or background compute. The browser sandbox bounds blast-radius but does not provide those capabilities. For those workloads run a server-side sandbox instead — see [In-Process WebAssembly Sandboxes for Agent-Generated Code](wasm-sandbox-agent-code-execution.md) for in-process execution, or the broader [Sandbox Runtime Comparison](sandbox-runtime-comparison.md) for containers, microVMs, and OS-level isolators.
- Any allow-listed origin re-hosts user-controlled content. CSP allow-lists are bypass-prone when an allow-listed host serves JSONP, hosts user uploads, or supports `data:` script sources ([Content Security Policy bypass survey, 2026](https://medium.com/@instatunnel/content-security-policy-bypass-1-000-ways-to-break-your-csp-%EF%B8%8F-ddbda5f96924)). Treat every allow-listed origin as data egress.

## Example

A minimal artifact host that runs an LLM-generated HTML document under all three layers:

```html
<iframe id="artifact"
        sandbox="allow-scripts allow-forms"
        srcdoc='<!DOCTYPE html>
<html>
<head>
  <meta http-equiv="Content-Security-Policy"
        content="default-src &apos;none&apos;;
                 script-src &apos;unsafe-inline&apos;;
                 style-src &apos;unsafe-inline&apos;;
                 img-src data: blob:;">
</head>
<body>
  <script>
    window.addEventListener("message", (e) => {
      if (e.data?.type === "init" && e.ports[0]) {
        const port = e.ports[0];
        port.postMessage({type: "query", sql: "select count(*) from items"});
        port.onmessage = (m) => document.body.textContent = JSON.stringify(m.data);
      }
    });
  </script>
</body>
</html>'></iframe>
<script>
  const iframe = document.getElementById("artifact");
  iframe.addEventListener("load", () => {
    const channel = new MessageChannel();
    channel.port1.onmessage = async (m) => {
      // Allow-list check: this parent only accepts {type: "query", sql: string}
      // and only against pre-registered safe queries.
      if (m.data?.type !== "query" || !isAllowedQuery(m.data.sql)) return;
      const result = await runReadOnlySql(m.data.sql);
      channel.port1.postMessage(result);
    };
    iframe.contentWindow.postMessage({type: "init"}, "*", [channel.port2]);
  });
</script>
```

## Key Takeaways

- The pattern is the composition of three browser primitives — sandbox attribute, immutable meta CSP, MessageChannel — each closing a distinct exfiltration path
- Omit `allow-same-origin` from the sandbox token list; together with `allow-scripts` it lets the embedded document remove its own sandbox
- Meta CSP cannot carry `frame-ancestors`, the CSP `sandbox` directive, or violation reporting — use an HTTP-header CSP on a separate origin when you need them
- Prefer `MessageChannel` over raw `postMessage`; the port reference is private and the channel dies on iframe navigation
- Gate CSP origin allow-list mutation to trusted operators — any user-allow-listed origin is a data egress channel
- Use this when blast-radius can be bounded to the browser tab; reach for server-side sandboxes when the workload needs filesystem, network, or sustained compute

## Related

- [In-Process WebAssembly Sandboxes for Agent-Generated Code](wasm-sandbox-agent-code-execution.md)
- [Dual-Boundary Sandboxing: Filesystem and Network Isolation](dual-boundary-sandboxing.md)
- [Sandboxed Coding Environments: Containers vs MicroVMs vs OS-Level Isolators](sandbox-runtime-comparison.md)
- [Agent-Authored Messages as a Deferred Exfiltration Channel](agent-authored-message-rendered-image-exfiltration.md)
- [Guarding Against URL-Based Data Exfiltration in Agentic Workflows](url-exfiltration-guard.md)
- [Defense-in-Depth Agent Safety](defense-in-depth-agent-safety.md)
