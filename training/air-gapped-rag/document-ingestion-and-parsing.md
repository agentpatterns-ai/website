---
title: "Air-Gapped RAG: Document Ingestion and Parsing"
description: "Compare open-source PDF parsers and OCR engines for offline RAG pipelines — extract structure, tables, and metadata without cloud dependencies."
tags:
  - training
  - workflows
  - tool-agnostic
---

# Air-Gapped RAG: Document Ingestion and Parsing

> Parsing is where most RAG systems silently fail — text extraction that drops tables, headings, and figure captions degrades retrieval before any query runs.

This module covers document ingestion for air-gapped RAG: choosing a parser, handling scanned documents with OCR, preserving structural metadata, and extracting tables in a retrieval-friendly form. The runnable examples wire parsers into a [Haystack](https://github.com/deepset-ai/haystack) indexing pipeline; the comparison tables stay framework-agnostic so you can substitute parsers without rebuilding the pipeline graph.

---

## Why Parsing Quality Determines Retrieval Quality

Most RAG failures trace back to the ingestion stage. A document that enters the pipeline as a flat string — headings flattened, tables converted to chaotic text fragments, figure captions lost — cannot be retrieved accurately regardless of embedding model quality or retriever sophistication.

Structural signals matter for retrieval: a chunk that retains its section heading gives the embedder semantic context that "Table 3 shows the following values:" alone does not. Page numbers and section hierarchy let citations point to specific locations rather than vague document references.

The five properties to optimize for in an air-gapped pipeline:

- **No cloud dependencies** — all inference runs locally; no API calls to external services
- **Table fidelity** — tables preserved as structure, not converted to whitespace-separated text
- **Reading order** — text extracted in the order a human would read it, not PDF draw order
- **OCR integration** — scanned PDFs handled without a separate preprocessing step
- **Metadata preservation** — headings, page numbers, section hierarchy carried through

---

## Parser Comparison

Five open-source parsers cover the main trade-off axes. All run fully offline. The Haystack Component column names the integration each parser ships through; where no Haystack wrapper exists you wrap the parser in a [custom Component](https://docs.haystack.deepset.ai/docs/custom-components) in about 15 lines.

| Parser | Table fidelity | Structure | OCR | Haystack component | Best for |
|--------|---------------|-----------|-----|---------------------|----------|
| [docling](https://github.com/DS4SD/docling) | High — detects structure, not just geometry | Layout + reading order | Built-in (EasyOCR/Tesseract) | `DoclingConverter` via [`docling-haystack`](https://github.com/DS4SD/docling-haystack) | Research papers, complex layouts |
| [PyMuPDF](https://github.com/pymupdf/PyMuPDF) | Medium — TableFinder API, geometry-based | Good for native PDFs | None natively | `PyPDFToDocument` (Haystack's built-in converter uses `pypdf`; wrap PyMuPDF as a custom component for TableFinder access) | Fast extraction of digital PDFs |
| [pdfplumber](https://github.com/jsvine/pdfplumber) | Medium — spatial analysis, character-level | Character positions, bounding boxes | None | Custom component wrapper | Machine-generated PDFs with clear geometry |
| [unstructured](https://github.com/Unstructured-IO/unstructured) | Medium | Document elements with type labels | Via Tesseract/Poppler | `UnstructuredFileConverter` via [`unstructured-fileconverter-haystack`](https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/unstructured) | Multi-format ETL pipelines |
| [marker](https://github.com/VikParuchuri/marker) | High — DL-based, handles multi-page tables | Markdown headings, layout-aware | Built-in via Surya | Custom component wrapper | Highest-fidelity Markdown output |

**docling** ([DS4SD/docling](https://github.com/DS4SD/docling)) is IBM's open-source document parser. It detects layout, reading order, table cell structure, code blocks, and formulas — not just raw character positions. Output formats include lossless JSON (preserving the full document hierarchy), Markdown, and HTML. It explicitly supports air-gapped execution for sensitive environments.

**PyMuPDF** ([pymupdf/PyMuPDF](https://github.com/pymupdf/PyMuPDF)) has no mandatory external dependencies and processes native PDFs at high speed. Its `TableFinder` API locates tables geometrically. For digital PDFs where speed matters more than accuracy on complex layouts, it is the lowest-overhead choice.

**pdfplumber** ([jsvine/pdfplumber](https://github.com/jsvine/pdfplumber)) operates at character level — each character carries its bounding box, font, and size. This enables precise table extraction via spatial clustering on well-structured PDFs. On scanned documents or irregular layouts it degrades significantly.

**unstructured** ([Unstructured-IO/unstructured](https://github.com/Unstructured-IO/unstructured)) wraps Tesseract and [Poppler](https://poppler.freedesktop.org/) for PDF processing and auto-detects file types. It outputs typed elements (`Title`, `NarrativeText`, `Table`) that map naturally to chunking by content type. Can be deployed fully offline via Docker.

**marker** ([VikParuchuri/marker](https://github.com/VikParuchuri/marker)) uses deep learning ([Surya](https://github.com/VikParuchuri/surya) for OCR, layout models for structure) to produce high-fidelity Markdown. It handles headers/footers removal, equation formatting, and multi-page tables. Runs on CPU, GPU, or Apple Silicon — but requires PyTorch and is the slowest of the five on CPU-only hardware [unverified — no neutral benchmark found].

---

## OCR for Scanned PDFs

Native PDFs embed text as character data. Scanned PDFs embed images — OCR is required to extract any text. The choice of OCR engine affects accuracy on non-standard layouts, throughput, and language support.

| Engine | Architecture | Language support | Strengths | Deployment |
|--------|-------------|-----------------|-----------|------------|
| [Tesseract](https://github.com/tesseract-ocr/tesseract) | LSTM + pattern | 100+ | Mature, Apache 2.0, simple integration | Any platform, no GPU |
| [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) | Deep learning (PP-OCRv5) | 100+ | 94.5% accuracy on OmniDocBench; handles skewed, warped, low-contrast | GPU recommended; CPU supported |
| [RapidOCR](https://github.com/rapidai/RapidOCR) | ONNX-ported PaddleOCR models | 80+ (default: Chinese + English) | Lighter than full PaddlePaddle; ONNX Runtime/TensorRT/OpenVINO backends | Multi-platform, no full PaddlePaddle stack |

**Selection guidance:**

- Straightforward English text, minimal layout complexity → **Tesseract** via `pytesseract`. Minimal dependencies, widely supported, sufficient for most office documents.
- Complex layouts, non-Latin scripts, tables within scans, or low-quality scans → **PaddleOCR** (PP-OCRv5). Significantly higher accuracy on difficult inputs. GPU speeds throughput but CPU works for batch processing.
- Need PaddleOCR accuracy without the full PaddlePaddle installation → **RapidOCR**. Uses the same models via ONNX; multi-platform and cross-language.

Image preprocessing before OCR raises accuracy for all engines: deskewing (rotate to horizontal baseline), denoising, binarization (grayscale → black/white), and scaling to 300 DPI minimum. [OpenCV](https://github.com/opencv/opencv) handles all of these without cloud dependencies.

---

## Air-Gap Considerations

All five parsers and all three OCR engines run entirely offline — but several require model weights or auxiliary files that must be pre-fetched before the host is air-gapped.

**Pre-download model weights on the network side:**

- **docling**: loads layout and table structure models on first call. Pre-fetch via `docling-tools models download` (or run the converter once on the network side), then pass `artifacts_path="/opt/models/docling"` to `DocumentConverter` inside the air-gap. Alternatively, set the Hugging Face cache via `HF_HOME=/opt/hf-cache` before the first run.
- **marker**: downloads Surya OCR, layout, and OCR error detection models from Hugging Face on first use. Mirror them into `HF_HOME` before air-gapping.
- **PaddleOCR**: downloads detection, recognition, and classification models on first call. Pre-download via `paddleocr --lang en` on the network host, then transfer `~/.paddleocr/` to the air-gapped host.
- **Tesseract**: traineddata files (e.g., `eng.traineddata`) must be present in `/usr/share/tesseract-ocr/4.00/tessdata/` or a path set via `TESSDATA_PREFIX`.

**Disable outbound fetches at runtime:**

Set `HF_HUB_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1` in the environment of any process that uses Hugging Face models. These cause the library to raise immediately on any outbound fetch attempt rather than failing silently at query time. Haystack converters that wrap HuggingFace models (`DoclingConverter`, the marker wrapper) pick up these environment variables automatically because they defer to the underlying library.

Set `HAYSTACK_TELEMETRY_ENABLED=False` defensively for Haystack 1.x compatibility wrappers — 2.x drops the telemetry module entirely, but if any transitive integration still imports it, the environment variable is a belt-and-braces guarantee.

**Avoid `trust_remote_code=True` on unverified parsers:**

Some Hugging Face models carry custom Python code that is fetched and executed at load time. This bypasses the normal weight-only download. For air-gapped environments, either pin the model revision, vendor the code into your image, or avoid models that require this flag.

---

## Table Extraction Strategies

Tables present four output format options, each with downstream trade-offs:

| Format | Example | Best for |
|--------|---------|---------|
| Plain text | Concatenated cell values | Simple text embedding; loses structure |
| Markdown table | `\| Col1 \| Col2 \|` | Readable in LLM context; structure-aware chunking |
| HTML table | `<table><tr><td>...</td></tr></table>` | Highest fidelity; larger token footprint |
| Structured object | Dict/dataframe per row | Programmatic access; requires separate serialization for embedding |

For RAG retrieval, Markdown tables are the practical default: they preserve cell relationships, render in most UIs, and occupy moderate token space. Extract each table as a separate chunk with the surrounding section heading attached — the heading provides context that the table alone lacks.

For tables spanning multiple pages, only docling and marker reliably reconstruct the full table as a single object. PyMuPDF and pdfplumber detect per-page table fragments that require post-processing to join.

---

## Preserving Structural Metadata

Flat text chunks lose the document's organizational signal. Preserve at minimum:

- **Source file path and filename** — for citation display
- **Page number** — for pointing users to the source location
- **Section heading** — the nearest `h1`/`h2` ancestor of the chunk
- **Element type** — `title`, `body`, `table`, `figure_caption`, `code_block`

docling's lossless JSON output carries all of these natively. For other parsers, reconstruct heading context by tracking the last heading seen as you iterate through document elements.

Figure captions deserve explicit handling: skip the figure itself (unless you have a local vision model), but preserve the caption text as a chunk. Captions often contain the most specific factual claim associated with a diagram — retrieval of the caption text frequently surfaces the relevant section.

---

## Example

A minimal Haystack indexing pipeline that parses PDFs with docling and writes them to a Qdrant collection. This is the first half of the full indexing pipeline from [Module 2](architecture-fundamentals.md#assembling-the-pipeline-in-haystack) — chunking and embedding stages follow in Modules 4 and 5.

```python
from haystack import Pipeline
from haystack_integrations.components.converters.docling import DoclingConverter
from haystack.components.preprocessors import DocumentCleaner

converter = DoclingConverter(
    # Pass pre-downloaded model weights for fully air-gapped environments.
    # On the network-connected build host: run docling once to populate the cache,
    # then copy the cache directory into the air-gapped host.
    convert_kwargs={"artifacts_path": "/opt/models/docling"},
)

indexing = Pipeline()
indexing.add_component("converter", converter)
indexing.add_component("cleaner", DocumentCleaner(
    remove_empty_lines=True,
    remove_extra_whitespaces=True,
    remove_repeated_substrings=False,
))
indexing.connect("converter.documents", "cleaner.documents")

result = indexing.run({
    "converter": {"sources": ["corpus/attention_is_all_you_need.pdf"]},
})

for doc in result["cleaner"]["documents"]:
    print(f"[{doc.meta.get('page', '?')}] {doc.content[:120]}")
```

`DoclingConverter` runs layout detection, table structure recognition, and reading-order reconstruction locally. The resulting `Document` objects carry page numbers, bounding boxes, and element types in the `meta` dict — metadata that survives all downstream stages (chunk, embed, retrieve) when you configure the `DocumentSplitter` to preserve it.

**Swapping parsers inside this pipeline is a one-line change.** The parser class determines which source formats the pipeline accepts and the richness of `meta`; everything downstream stays the same:

```python
# Fast path for digital PDFs — no ML inference
from haystack.components.converters import PyPDFToDocument
indexing.add_component("converter", PyPDFToDocument())

# Multi-format ETL with auto-detection
from haystack_integrations.components.converters.unstructured import UnstructuredFileConverter
indexing.add_component("converter", UnstructuredFileConverter())

# Mixed corpus — route by extension with a FileTypeRouter upstream
from haystack.components.routers import FileTypeRouter
indexing.add_component("router", FileTypeRouter(
    mime_types=["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"],
))
indexing.add_component("pdf_converter", DoclingConverter())
indexing.add_component("docx_converter", DOCXToDocument())
indexing.connect("router.application/pdf", "pdf_converter.sources")
indexing.connect("router.application/vnd.openxmlformats-officedocument.wordprocessingml.document", "docx_converter.sources")
```

**What other parsers would differ on with this document:**
- `PyPDFToDocument` (Haystack built-in): ~10× faster on native PDFs but loses multi-column reading order and table cell structure [unverified — no neutral benchmark comparing all five found]
- `UnstructuredFileConverter`: produces typed elements (`Title`, `Table`) in document metadata; simpler for heterogeneous corpora
- Custom `MarkerConverter` wrapper: highest Markdown fidelity for equations and code blocks; slower on CPU than docling

---

## Key Takeaways

- Parsing quality sets a ceiling on retrieval quality — chunks that lose table structure or reading order cannot be retrieved accurately regardless of downstream improvements
- docling and marker produce the highest structural fidelity for complex PDFs; PyMuPDF and pdfplumber are faster for simple digital PDFs
- OCR selection depends on document complexity: Tesseract for standard layouts, PaddleOCR (or RapidOCR) for difficult scans and non-Latin scripts
- Preserve section headings, page numbers, and element type as chunk metadata — this information is lost if not extracted at parse time
- Extract tables as separate Markdown chunks with the parent heading attached; for multi-page tables, only docling and marker reliably reconstruct the full object

## Unverified Claims

- marker is the slowest of the five parsers on CPU-only hardware — based on architectural inference (deep learning inference vs. rule-based extraction); no neutral benchmark comparing all five on equivalent hardware found
- PyMuPDF's speed advantage over ML-based parsers — relative speed claim based on architectural characteristics (rule-based vs. neural inference); no neutral benchmark comparing all five found
- `table.export_to_markdown()` method signature on individual table objects — confirmed that `doc.tables` is a list of table items per docling's document model; per-table markdown export method signature unverified against API reference

## Related

- [Air-Gapped RAG: Architecture Fundamentals](architecture-fundamentals.md) — overview of the full pipeline and module dependencies
- [Air-Gapped RAG: Chunking Strategies](chunking-strategies.md) — how parsed document structure informs chunking decisions
- [Air-Gapped RAG: Local Embeddings and Vector Stores](local-embeddings-vector-stores.md) — what happens to chunks after ingestion
