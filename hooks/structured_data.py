"""
MkDocs hook: inject JSON-LD structured data into every page at build time.

Schemas emitted:
  - Organization  — all pages
  - WebSite       — homepage only
  - Article       — all non-index doc pages
  - BreadcrumbList — all pages with URL depth ≥ 1
  - FAQPage       — pages whose rendered HTML contains a recognised FAQ section
  - HowTo         — pattern/technique pages whose rendered HTML contains a numbered step list
"""

import html
import json
import re
import subprocess
from datetime import date
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin

# ---------------------------------------------------------------------------
# Module-level singletons built once at on_config
# ---------------------------------------------------------------------------
_organization: Optional[dict] = None
_website: Optional[dict] = None
_site_url: str = ""
_docs_dir: Optional[Path] = None


# ---------------------------------------------------------------------------
# on_config — build shared schemas once
# ---------------------------------------------------------------------------
def on_config(config):
    global _organization, _website, _site_url, _docs_dir

    _site_url = (config.get("site_url") or "").rstrip("/")
    _docs_dir = Path(config.get("docs_dir") or "docs")
    site_name = config.get("site_name") or ""
    logo_url = f"{_site_url}/assets/logo.png"
    extra = config.get("extra") or {}
    social_profiles = extra.get("social_profiles") or []

    _organization = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": site_name,
        "url": _site_url,
        "logo": logo_url,
    }
    if social_profiles:
        _organization["sameAs"] = social_profiles

    _website = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": site_name,
        "url": _site_url,
        "potentialAction": {
            "@type": "SearchAction",
            "target": {
                "@type": "EntryPoint",
                "urlTemplate": f"{_site_url}/search/?q={{search_term_string}}",
            },
            "query-input": "required name=search_term_string",
        },
    }

    return config


# ---------------------------------------------------------------------------
# Schema builders
# ---------------------------------------------------------------------------

def _build_article(page, config) -> dict:
    meta = page.meta or {}
    site_name = config.get("site_name") or ""
    page_url = urljoin(_site_url + "/", page.url or "")
    src_path = page.file.src_path if page.file else ""

    article = {
        "@context": "https://schema.org",
        "@type": "TechArticle",
        "headline": _safe(meta.get("title") or page.title or ""),
        "url": page_url,
        "isPartOf": {
            "@type": "WebSite",
            "name": site_name,
            "url": _site_url,
        },
    }

    description = meta.get("description") or ""
    if description:
        article["description"] = _safe(description)

    pub_date = meta.get("date") or ""
    if pub_date:
        article["datePublished"] = str(pub_date)

    # dateModified from git history — critical for freshness signals
    lastmod = _git_lastmod(src_path)
    if lastmod:
        article["dateModified"] = lastmod

    author = meta.get("author") or ""
    if author:
        article["author"] = {"@type": "Person", "name": _safe(author)}

    tags = meta.get("tags") or []
    if tags:
        article["keywords"] = ", ".join(tags)

    return article


def _build_breadcrumbs(page) -> Optional[dict]:
    url = (page.url or "").strip("/")
    if not url:
        return None
    segments = [s for s in url.split("/") if s]
    if not segments:
        return None

    items = []
    accumulated = ""
    for i, segment in enumerate(segments):
        accumulated = f"{accumulated}/{segment}"
        # Strip trailing /index or .html suffixes for display
        label = segment.replace("-", " ").replace("_", " ").title()
        label = re.sub(r"\.html?$", "", label)
        if label.lower() == "index":
            continue
        items.append({
            "@type": "ListItem",
            "position": len(items) + 1,
            "name": label,
            "item": _site_url + accumulated,
        })

    if not items:
        return None

    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": items,
    }


# ---------------------------------------------------------------------------
# FAQ detection
# ---------------------------------------------------------------------------
_FAQ_HEADING_RE = re.compile(
    r'<h2[^>]*>(?:FAQ|Frequently Asked Questions)</h2>(.*?)(?=<h2|$)',
    re.IGNORECASE | re.DOTALL,
)
_QA_PAIR_RE = re.compile(
    r'<strong>([^<]+)</strong>\s*</p>\s*<p[^>]*>([^<]+)',
    re.DOTALL,
)


def _detect_faq(rendered_html: str) -> Optional[dict]:
    m = _FAQ_HEADING_RE.search(rendered_html)
    if not m:
        return None
    block = m.group(1)
    pairs = _QA_PAIR_RE.findall(block)
    if len(pairs) < 2:
        return None
    entities = [
        {
            "@type": "Question",
            "name": _safe(q.strip()),
            "acceptedAnswer": {"@type": "Answer", "text": _safe(a.strip())},
        }
        for q, a in pairs
    ]
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": entities,
    }


# ---------------------------------------------------------------------------
# HowTo detection
# ---------------------------------------------------------------------------
_ORDERED_LIST_RE = re.compile(r'<ol[^>]*>(.*?)</ol>', re.DOTALL | re.IGNORECASE)
_LIST_ITEM_RE = re.compile(r'<li[^>]*>(.*?)</li>', re.DOTALL | re.IGNORECASE)
_HOWTO_PATHS = (
    "patterns/", "techniques/", "agent-design/", "geo/",
    "workflows/", "context-engineering/", "tool-engineering/",
    "multi-agent/", "instructions/", "verification/",
)


def _detect_howto(page, rendered_html: str) -> Optional[dict]:
    src = page.file.src_path if page.file else ""
    if not any(src.startswith(p) for p in _HOWTO_PATHS):
        return None

    m = _ORDERED_LIST_RE.search(rendered_html)
    if not m:
        return None
    items_html = _LIST_ITEM_RE.findall(m.group(1))
    if len(items_html) < 3:
        return None

    steps = []
    for i, item_html in enumerate(items_html, 1):
        text = re.sub(r'<[^>]+>', '', item_html).strip()
        if not text:
            continue
        steps.append({
            "@type": "HowToStep",
            "position": i,
            "text": _safe(text),
        })

    if len(steps) < 3:
        return None

    meta = page.meta or {}
    return {
        "@context": "https://schema.org",
        "@type": "HowTo",
        "name": _safe(meta.get("title") or page.title or ""),
        "step": steps,
    }


# ---------------------------------------------------------------------------
# Injection helper
# ---------------------------------------------------------------------------

def _git_lastmod(src_path: str) -> str:
    """Return YYYY-MM-DD of the last git commit touching src_path."""
    if not _docs_dir or not src_path:
        return date.today().isoformat()

    abs_path = _docs_dir / src_path
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%cI", "--", str(abs_path)],
            capture_output=True, text=True, check=True, timeout=5,
        )
        iso_ts = result.stdout.strip()
        if iso_ts:
            return iso_ts[:10]
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return date.today().isoformat()


def _safe(value: str) -> str:
    """Escape HTML special chars so they are safe inside a <script> block."""
    return html.unescape(value)


def _render_ld_json(schemas: list) -> str:
    parts = []
    for schema in schemas:
        payload = json.dumps(schema, ensure_ascii=False, indent=None)
        # Escape </script> sequences to prevent injection
        payload = payload.replace("</", "<\\/")
        parts.append(f'<script type="application/ld+json">{payload}</script>')
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# MkDocs events
# ---------------------------------------------------------------------------

def on_post_page(output: str, *, page, config, **kwargs) -> str:
    """Inject JSON-LD blocks into every rendered page."""
    schemas = []

    # Organization — always
    if _organization:
        schemas.append(_organization)

    # WebSite — homepage only
    src_path = page.file.src_path if page.file else ""
    is_home = src_path == "index.md" or (page.url or "").strip("/") == ""
    if is_home and _website:
        schemas.append(_website)

    # Skip rich schema for noindex pages (stubs/consolidated)
    meta = page.meta or {}
    is_noindex = meta.get("noindex", False)

    # Article — non-index, non-noindex pages
    is_index = src_path.endswith("index.md")
    if not is_index and not is_noindex:
        schemas.append(_build_article(page, config))

    # BreadcrumbList
    bc = _build_breadcrumbs(page)
    if bc:
        schemas.append(bc)

    if not is_noindex:
        # FAQPage
        faq = _detect_faq(output)
        if faq:
            schemas.append(faq)

        # HowTo
        howto = _detect_howto(page, output)
        if howto:
            schemas.append(howto)

    if not schemas:
        return output

    ld_block = _render_ld_json(schemas)

    # Inject before </head>; fall back to before <body> if </head> absent
    if "</head>" in output:
        return output.replace("</head>", f"{ld_block}\n</head>", 1)
    if "<body" in output:
        return re.sub(r'(<body[^>]*>)', rf'\1\n{ld_block}', output, count=1)
    return output + "\n" + ld_block
