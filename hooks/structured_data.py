"""
MkDocs hook: inject JSON-LD structured data into every page at build time.

Schemas emitted:
  - Organization  — all pages
  - WebSite       — homepage only
  - Article       — all non-index doc pages
  - BreadcrumbList — all pages with URL depth ≥ 1
  - FAQPage       — pages whose rendered HTML contains a recognised FAQ section
  - HowTo         — pattern/technique pages whose rendered HTML contains a numbered step list
  - DefinedTerm   — coined-concept pages (title=term, description=definition, aliases=alternateName)
  - DefinedTermSet — the /concepts glossary landing page (anchors every DefinedTerm)
"""

import html
import json
import logging
import re
import subprocess
from datetime import date
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin

log = logging.getLogger("mkdocs.hooks.structured_data")

# GEO-M2 answer band: FAQ answers should land in 40–80 words for citation lift.
FAQ_ANSWER_MIN_WORDS = 40
FAQ_ANSWER_MAX_WORDS = 80

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
        # Always emit a publisher Organization — E-E-A-T/attribution signal that
        # isPartOf (a WebSite) does not satisfy. Mirrors the on_config logo URL.
        "publisher": {
            "@type": "Organization",
            "name": site_name,
            "url": _site_url,
            "logo": f"{_site_url}/assets/logo.png",
        },
    }

    description = meta.get("description") or ""
    if description:
        article["description"] = _safe(description)

    # datePublished: explicit `date:` frontmatter wins; otherwise derive from
    # the first git commit (mirroring dateModified) so freshness/recency signals
    # are present without per-page frontmatter (0 of 1082 pages set `date:`).
    pub_date = meta.get("date") or ""
    if pub_date:
        article["datePublished"] = str(pub_date)
    else:
        created = _git_created(src_path)
        if created:
            article["datePublished"] = created

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
# Material's permalink plugin injects a headerlink anchor before every heading's
# closing tag (`<h2 id="faq">FAQ<a class="headerlink" ...>&para;</a></h2>`), so
# the heading never closes immediately after the text. The lazy tag-skipping
# group tolerates that anchor; it was previously matched by an exact
# `>FAQ</h2>` pattern that could never match real rendered output, which is why
# FAQPage had never once fired on this site (#9712).
_FAQ_HEADING_RE = re.compile(
    r'<h2[^>]*>\s*(?:FAQ|Frequently Asked Questions)\s*(?:<[^>]+>[^<]*)*?</h2>(.*?)(?=<h2|$)',
    re.IGNORECASE | re.DOTALL,
)
# `(.*?)` (not `[^<]+`) in both groups — a sourced answer routinely contains
# inline markup (a citation `<a>`, a `<code>` span, `<strong>`), and matching
# only up to the first `<` silently truncated the answer there, undercounting
# words and dropping everything after the first inline tag from the JSON-LD.
_QA_PAIR_RE = re.compile(
    r'<strong>(.*?)</strong>\s*</p>\s*<p[^>]*>(.*?)</p>',
    re.DOTALL,
)
_STRIP_TAGS_RE = re.compile(r'<[^>]+>')


def _detect_faq(rendered_html: str) -> Optional[dict]:
    m = _FAQ_HEADING_RE.search(rendered_html)
    if not m:
        return None
    block = m.group(1)
    pairs = _QA_PAIR_RE.findall(block)
    if len(pairs) < 2:
        return None
    entities = []
    for q, a in pairs:
        question = _STRIP_TAGS_RE.sub('', q).strip()
        answer = _STRIP_TAGS_RE.sub('', a).strip()
        # GEO-M2: warn (don't drop) when an answer falls outside the 40–80-word
        # band that carries FAQPage citation lift, so authors can tighten it.
        word_count = len(answer.split())
        if not FAQ_ANSWER_MIN_WORDS <= word_count <= FAQ_ANSWER_MAX_WORDS:
            log.warning(
                "FAQ answer is %d words (outside the %d–%d-word band): %r",
                word_count, FAQ_ANSWER_MIN_WORDS, FAQ_ANSWER_MAX_WORDS, question,
            )
        entities.append({
            "@type": "Question",
            "name": _safe(question),
            "acceptedAnswer": {"@type": "Answer", "text": _safe(answer)},
        })
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


def _src_posix(page) -> str:
    """Source path with forward slashes — src_path uses os.sep on Windows,
    which breaks the path-prefix gates below unless normalised."""
    return (page.file.src_path if page.file else "").replace("\\", "/")


def _detect_howto(page, rendered_html: str) -> Optional[dict]:
    src = _src_posix(page)
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
# DefinedTerm — coined-concept pages become machine-readable glossary entries
# ---------------------------------------------------------------------------
# Sections whose leaf pages name a coined concept (a term worth a glossary
# entry). Deliberately excludes articles/ (paper summaries), tools/ (vendor
# docs), training/ (pedagogical modules), standards/ (process docs), and the
# loose nav pages — those describe things, they don't coin terms.
_DEFINED_TERM_PATHS = (
    "patterns/", "anti-patterns/", "fallacies/", "frameworks/",
    "agent-design/", "context-engineering/", "instructions/", "multi-agent/",
    "tool-engineering/", "verification/", "security/", "workflows/",
    "geo/", "code-review/", "observability/", "emerging/",
)
# Curated exceptions: pages outside the concept sections that still name a
# canonical term worth a glossary entry (e.g. Prompt Engineering only has a
# training module today). Exact src paths, posix-separated.
_DEFINED_TERM_ALLOW = (
    "training/foundations/prompt-engineering.md",
)
# Canonical glossary that every DefinedTerm points back to via inDefinedTermSet.
_TERM_SET_SRC = "concepts.md"
_TERM_SET_ID = "/concepts/"


def _term_set_url() -> str:
    return f"{_site_url}{_TERM_SET_ID}"


def _build_defined_term(page, config) -> Optional[dict]:
    """A coined-concept leaf page → one DefinedTerm anchored to /concepts/."""
    src = _src_posix(page)
    if src.endswith("index.md"):
        return None
    in_section = any(src.startswith(p) for p in _DEFINED_TERM_PATHS)
    if not in_section and src not in _DEFINED_TERM_ALLOW:
        return None

    meta = page.meta or {}
    # `term:` is the clean canonical moniker; the page title is SEO-shaped, so
    # prefer the explicit term and let the full title stay in the headline only.
    name = _safe(meta.get("term") or meta.get("title") or page.title or "")
    description = _safe(meta.get("description") or "")
    # A term without a name or a definition is not a useful glossary entry.
    if not name or not description:
        return None

    term = {
        "@context": "https://schema.org",
        "@type": "DefinedTerm",
        "name": name,
        "description": description,
        "url": urljoin(_site_url + "/", page.url or ""),
        "inDefinedTermSet": _term_set_url(),
    }

    aliases = meta.get("aliases") or []
    alt = [_safe(str(a).strip()) for a in aliases if str(a).strip()]
    if alt:
        term["alternateName"] = alt

    return term


def _build_defined_term_set(config) -> dict:
    """Stub DefinedTermSet on /concepts/ so every term's reference resolves."""
    return {
        "@context": "https://schema.org",
        "@type": "DefinedTermSet",
        "@id": _term_set_url(),
        "name": f"{config.get('site_name') or 'Agent Patterns'} Glossary",
        "url": _term_set_url(),
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


def _git_created(src_path: str) -> Optional[str]:
    """Return YYYY-MM-DD of the first git commit that added src_path.

    Mirrors _git_lastmod but walks history in reverse so Article schema can
    carry a datePublished without per-page `date:` frontmatter. Returns None
    (rather than today) when history is unavailable, so the caller omits the
    field instead of asserting a misleading publish date.
    """
    if not _docs_dir or not src_path:
        return None

    abs_path = _docs_dir / src_path
    try:
        result = subprocess.run(
            ["git", "log", "--reverse", "--format=%cI", "--", str(abs_path)],
            capture_output=True, text=True, check=True, timeout=5,
        )
        for iso_ts in result.stdout.splitlines():
            iso_ts = iso_ts.strip()
            if iso_ts:
                return iso_ts[:10]
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None


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

        # DefinedTermSet — the glossary landing page anchors every term
        if src_path == _TERM_SET_SRC:
            schemas.append(_build_defined_term_set(config))

        # DefinedTerm — coined-concept leaf pages
        dt = _build_defined_term(page, config)
        if dt:
            schemas.append(dt)

    if not schemas:
        return output

    ld_block = _render_ld_json(schemas)

    # Inject before </head>; fall back to before <body> if </head> absent
    if "</head>" in output:
        return output.replace("</head>", f"{ld_block}\n</head>", 1)
    if "<body" in output:
        return re.sub(r'(<body[^>]*>)', rf'\1\n{ld_block}', output, count=1)
    return output + "\n" + ld_block
