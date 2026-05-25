---
title: "Air-Gapped RAG: Deployment, Operations, and Compliance"
description: "Containerize, operate, and audit an air-gapped RAG system in production — artifact signing, CVE scanning, access control, and SOC 2/FedRAMP/HIPAA compliance artifacts."
tags:
  - training
  - workflows
  - security
  - tool-agnostic
---

# Air-Gapped RAG: Deployment, Operations, and Compliance

> Building an air-gapped RAG pipeline is the first half — keeping it patched, auditable, and compliant without public internet access is the operational discipline that separates a demo from a production deployment.

This module covers containerizing the full stack for offline delivery, maintaining it under an air-gap update discipline, enforcing access control and audit logging, and generating the compliance artifacts that regulated environments require. Defence and classified deployments extend the posture with FIPS 140-3 cryptography, STIG-hardened base images, NIST SP 800-53 control mappings, and RMF artifact templates.

The deployment unit is a Haystack pipeline served via [Hayhooks](https://github.com/deepset-ai/hayhooks) — one FastAPI container that loads the indexing and query pipelines from YAML and exposes them as REST endpoints. Every other stage (Qdrant, Ollama) is a sidecar container on the same compose network.

---

## Containerization and Model Bundling

An air-gapped deployment ships as a self-contained artifact set: container images, model weights, and embedding models bundled together so that no network access is required after delivery.

**Exporting container images across the air-gap boundary:**

Docker's [`docker save`](https://docs.docker.com/reference/cli/docker/image/save/) and `docker load` workflow transfers complete images including all layers:

```bash
# On the network-connected build host
docker save my-rag-stack:v1.2.0 | gzip > rag-stack-v1.2.0.tar.gz

# Transfer to the air-gapped host via approved media, then:
docker load < rag-stack-v1.2.0.tar.gz
```

**Bundling model weights offline:**

GGUF weights (llama.cpp) and AWQ weights are single-file or small-directory artifacts that copy into the container image at build time or mount as volumes from a local model store. Load time requires no network access.

HuggingFace embedding models (e.g., [`nomic-ai/nomic-embed-text-v1.5`](https://huggingface.co/nomic-ai/nomic-embed-text-v1.5), [`sentence-transformers/all-MiniLM-L6-v2`](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)) download their weights to a local cache directory. Set [`local_files_only=True`](https://huggingface.co/docs/transformers/installation#offline-mode) to prevent any outbound fetch attempts at runtime:

```python
from sentence_transformers import SentenceTransformer  # https://github.com/UKPLab/sentence-transformers

model = SentenceTransformer(
    "/opt/models/nomic-embed-text-v1.5",
    device="cpu",
)
# No network access occurs; raises EnvironmentError if weights are missing
```

Pre-download the full model directory on the network side and transfer it into the air-gapped environment as part of the initial deployment bundle.

---

## Air-Gapped Update Discipline

Updates cross the air-gap boundary as signed artifacts — this prevents unsigned or tampered images from entering the environment.

**Artifact signing with cosign:**

[sigstore/cosign](https://github.com/sigstore/cosign) signs container images and produces verifiable signatures that do not require network access to verify (using offline key pairs rather than the default Rekor transparency log):

```bash
# Sign on the network side (build host)
cosign sign --key cosign.key my-rag-stack:v1.2.0

# Verify on the air-gapped host before loading
cosign verify --key cosign.pub my-rag-stack:v1.2.0
```

For environments where even the cosign binary cannot reach the public Rekor log, bypass the transparency log check with `--tlog-upload=false` at sign time and `--insecure-ignore-tlog` at verify time — signatures then rely on the offline key pair alone [unverified — cosign's CLI flags have shifted across versions; confirm the exact names against the release you ship].

**Offline CVE scanning with Trivy:**

[Trivy](https://aquasecurity.github.io/trivy/latest/docs/advanced/air-gap/) explicitly supports air-gapped scanning. Download the vulnerability database on the network side, transfer it, and point Trivy at the local copy:

```bash
# Download DB on network host
trivy --cache-dir /tmp/trivy-cache image --download-db-only

# Transfer /tmp/trivy-cache to air-gapped host, then scan:
trivy image --offline-scan --cache-dir /opt/trivy-cache my-rag-stack:v1.2.0
```

Sync the vulnerability database on a defined cadence (weekly at minimum) — an offline DB becomes stale and misses newly discovered CVEs.

---

## Access Control

Three isolation models for multi-tenant RAG deployments, ordered by isolation strength:

| Model | Mechanism | Trade-off |
|-------|-----------|-----------|
| Separate deployments | Each security domain runs its own stack | Strongest isolation; highest operational cost |
| Collection-per-tenant | One Qdrant/Chroma instance, separate collections per tenant | Medium isolation; shared compute |
| Metadata filtering | Single collection, per-query filter on `tenant_id` field | Lowest cost; requires correct filter on every query |

[Chroma's multi-tenancy documentation](https://docs.trychroma.com/production/administration/multi-tenancy) covers collection-per-tenant and database-level isolation. [Qdrant collections](https://qdrant.tech/documentation/concepts/collections/) support multiple named collections on a single node with independent HNSW indexes.

For metadata filtering to provide meaningful isolation, the filter must be enforced at the query layer — not left to the application to apply voluntarily. Wrap the retriever in a thin service that injects the tenant filter from the authenticated session, not from the query payload.

**Per-user document visibility** requires attaching allowed document IDs or classification labels to each user's session and enforcing them as mandatory filters. Qdrant payload indexing on a `clearance_level` or `allowed_users` field supports this without a separate access control service.

---

## Audit Logging

An audit log for a RAG system must capture enough information to answer: who queried, what they queried, what the system retrieved, and what answer was served.

**Minimum audit log schema:**

```json
{
  "event_id": "uuid",
  "timestamp": "ISO-8601",
  "user_id": "string",
  "session_id": "string",
  "query_text": "string",
  "retrieved_chunks": [
    { "chunk_id": "string", "source_doc": "string", "page": 1, "score": 0.87 }
  ],
  "answer_text": "string",
  "model_id": "string",
  "latency_ms": 320
}
```

`chunk_id` must map back to the source document and page number — this is the link that compliance reviewers use to verify the system served content from authorized sources only.

Write logs to append-only storage. For HIPAA and FedRAMP, tamper-evidence is a requirement: use a write-once log store or a log integrity mechanism ([NIST SP 800-53 AU-9](https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final) specifies audit log protection controls). For AI agents that call tools directly, a [cryptographic audit trail with hash-chained receipts](../../security/cryptographic-governance-audit-trail.md) provides stronger tamper-evidence and satisfies EU AI Act Article 12 record-keeping requirements. A simple approach for the RAG query layer: periodically hash the log file and store the hash in a separate tamper-evident location.

---

## Model Rotation

Swapping embedding models requires re-indexing the corpus because the new model's vector space is not aligned with the old model's vectors. There is no migration path that avoids this.

Strategies for minimizing downtime:

1. **Parallel collections** — index the full corpus with the new model into a second collection while the old collection serves traffic. Switch query routing to the new collection after validation. [Qdrant collections](https://qdrant.tech/documentation/concepts/collections/) and [Chroma](https://docs.trychroma.com/) both support multiple simultaneous collections.
2. **Dual-query window** — query both old and new collections, merge results by score, and monitor recall metrics on both during transition.
3. **Scheduled maintenance window** — acceptable when document corpus is small enough to re-index in a defined window (minutes to hours depending on corpus size and hardware).

LLM rotation (swapping the generation model) does not require re-indexing — only the serving container changes.

---

## Backup and Recovery

**Vector store snapshots:**

Qdrant exposes a REST API for snapshot creation and restoration. Snapshots are self-contained files that can be stored in the air-gapped environment's backup system:

```bash
# Create snapshot
curl -X POST "http://localhost:6333/collections/my_collection/snapshots"

# List snapshots
curl "http://localhost:6333/collections/my_collection/snapshots"

# Restore from snapshot (on a new node or after data loss)
curl -X POST "http://localhost:6333/collections/my_collection/snapshots/recover" \
  -H "Content-Type: application/json" \
  -d '{"location": "file:///backups/my_collection-snapshot-1.snapshot"}'
```

See [Qdrant snapshots documentation](https://qdrant.tech/documentation/concepts/snapshots/) for the full API.

Chroma persists to a local directory (SQLite + HNSW on disk). Back it up as a filesystem snapshot — stop writes, copy the directory, resume. For production use, run Chroma in its [server mode](https://docs.trychroma.com/production/deployment) with a dedicated data volume.

**Source document corpus versioning:**

The vector index is derivable from the document corpus — the corpus is the source of truth. Version the source documents independently (e.g., with a hash manifest) so that the index can be regenerated from scratch if corrupted. Store the corpus backup separate from the index backup.

---

## Compliance Artifacts

The compliance posture for an air-gapped RAG system depends on the regulatory framework in scope. Key requirements per framework:

**HIPAA (medical documents containing PHI):**
- Encrypt at rest (AES-256) and in transit (TLS 1.2+)
- Audit logs as described above — who accessed what PHI, when
- Business Associate Agreement with the software vendor if they have access to PHI (in fully air-gapped deployments, this primarily applies to on-premises software licenses, not cloud providers)
- Workforce training records and written policies for data handling

**SOC 2 Type II:**
- Document the system boundary: what enters (source documents), who can query (access control matrix), how answers are generated (model and retrieval pipeline documentation)
- Demonstrate consistent control operation over the audit period — logs must be complete, retained per the organization's retention policy, and tamper-evident
- Change management records for model updates and configuration changes

**FedRAMP:**
- System Security Plan (SSP) documenting all components, data flows, and controls (see the RMF section below for the SSP outline)
- FIPS 140-3 validated cryptography for encryption at rest and in transit — this constrains TLS configuration and key management choices (see FIPS 140-3 section below)
- Continuous monitoring plan with defined vulnerability scanning cadence (Trivy weekly, STIG scan per release)
- Air-gapped deployments simplify the external attack surface but the internal network boundary (who can reach the RAG service) must be formally defined and controlled

**DoD Impact Levels (IL2 through IL6):**
- STIG-hardened base images (DISA Iron Bank) — see STIG section below
- RMF authorization package: SSP + SAR + POA&M — see RMF section below
- NIST SP 800-53 control mapping — see control mapping table below
- SBOM generated and attested with every signed release — see SBOM section below

For all frameworks, the audit log schema above is the foundation. Generate compliance artifacts from log queries rather than maintaining them manually.

---

## Hands-On: Hayhooks Stack and Audit Log Generation

The deployment unit for a Haystack-based air-gapped RAG system is a [Hayhooks](https://github.com/deepset-ai/hayhooks) container that loads the pipeline YAML files produced in Modules 5–8 and serves them as FastAPI endpoints. Hayhooks handles the HTTP layer, concurrency, and pipeline lifecycle; your code is just the three YAML files.

### Project layout

```
air-gapped-rag/
├── pipelines/
│   ├── indexing.yaml          # Module 5 indexing pipeline
│   ├── query.yaml             # Module 7 query + generation pipeline
│   └── evaluation.yaml        # Module 8 evaluation pipeline
├── models/                    # pre-downloaded weights, mounted read-only
│   ├── nomic-embed-text-v1.5/
│   ├── Splade_PP_en_v1/
│   ├── bge-reranker-v2-m3/
│   └── qwen2.5-7b-q4_k_m.gguf
├── golden_set.yaml            # Module 8 evaluation golden set
├── Dockerfile                 # Hayhooks + signed dependency set
├── compose.yaml               # full stack definition
└── sbom.cdx.json              # generated by Syft at build time
```

### Dockerfile (Hayhooks container)

```dockerfile
# Start from a STIG-hardened Red Hat UBI image. For true classified deployments,
# use a DISA-approved STIG base such as the Iron Bank UBI9 STIG image.
FROM registry1.dso.mil/ironbank/redhat/ubi/ubi9:latest AS base

# Install Python and FIPS-enabled OpenSSL provider.
# On RHEL 9, this is `openssl-fips-provider`.
RUN dnf install -y python3.11 python3.11-pip openssl-fips-provider && \
    dnf clean all && \
    rm -rf /var/cache/dnf

# Enable FIPS 140-3 mode system-wide (persists for the process lifetime)
RUN update-crypto-policies --set FIPS

# Pinned, vendored Python dependencies from an internal PyPI mirror.
# Every package in requirements.lock has been approved and has an SBOM entry.
COPY requirements.lock /tmp/requirements.lock
RUN pip3.11 install --no-index \
    --find-links=/opt/pypi-mirror \
    --require-hashes \
    -r /tmp/requirements.lock

# Copy pipelines, models, and application code
WORKDIR /app
COPY pipelines/ /app/pipelines/
COPY models/ /opt/models/
COPY hayhooks_server.py /app/

# Offline-only environment variables — any outbound fetch raises immediately
ENV HF_HOME=/opt/hf-cache \
    HF_HUB_OFFLINE=1 \
    HF_DATASETS_OFFLINE=1 \
    TRANSFORMERS_OFFLINE=1 \
    HAYSTACK_TELEMETRY_ENABLED=False

USER 10001:10001
EXPOSE 1416
CMD ["python3.11", "-m", "hayhooks", "run", "--pipelines-dir", "/app/pipelines", "--host", "0.0.0.0", "--port", "1416"]
```

### compose.yaml (full stack)

```yaml
services:
  qdrant:
    image: qdrant/qdrant:v1.9.0
    volumes:
      - qdrant_data:/qdrant/storage
    expose:
      - "6333"

  llm:
    image: ollama/ollama:0.5.4
    volumes:
      - /opt/models:/opt/ollama/models:ro
    environment:
      - OLLAMA_HOST=0.0.0.0:11434     # container network boundary replaces localhost
      - OLLAMA_MODELS=/opt/ollama/models
    expose:
      - "11434"

  hayhooks:
    image: my-rag-stack:v1.2.0        # signed image built from the Dockerfile above
    depends_on:
      - qdrant
      - llm
    volumes:
      - /opt/models:/opt/models:ro
      - audit_logs:/var/log/rag-audit
    environment:
      - QDRANT_URL=http://qdrant:6333
      - OLLAMA_URL=http://llm:11434
      - AUDIT_LOG_PATH=/var/log/rag-audit/queries.jsonl
    # Only the Hayhooks service publishes to the host, and only to 127.0.0.1.
    ports:
      - "127.0.0.1:1416:1416"

volumes:
  qdrant_data:
  audit_logs:
```

Network topology notes:

1. `qdrant` and `llm` use `expose` rather than `ports`, so they are reachable on the compose network but not on the host — the container boundary does the work that `OLLAMA_HOST=127.0.0.1` does on bare metal ([see Module 7](local-llm-inference.md#binding-and-air-gap-verification)).
2. Only `hayhooks` publishes to the host, and only to `127.0.0.1:1416`, so a peer on the LAN cannot reach the stack.
3. Every service runs as a non-root user inside its container (`USER 10001:10001` in the Hayhooks Dockerfile; Qdrant and Ollama default to non-root in their upstream images).

### Hayhooks pipeline server

```python
# hayhooks_server.py — minimal Hayhooks config loaded at container startup
from pathlib import Path
from hayhooks import create_app
from haystack import Pipeline

PIPELINE_DIR = Path("/app/pipelines")

def load_pipelines() -> dict[str, Pipeline]:
    return {
        stem: Pipeline.loads((PIPELINE_DIR / f"{stem}.yaml").read_text())
        for stem in ("indexing", "query", "evaluation")
    }

# Hayhooks discovers this function and mounts each pipeline under /<name>/run
# e.g. POST /query/run with JSON body {"dense_query": {"text": "..."}, ...}
app = create_app(pipelines=load_pipelines())
```

The YAML files are the audit artifact. The Python wrapper is ~10 lines and has no business logic of its own — `hayhooks` handles HTTP serialization, pipeline execution, and error handling.

### Audit log schema (Hayhooks middleware)

Hayhooks supports FastAPI middleware, so the audit log is a thin wrapper around every `/query/run` call that captures the request body, the pipeline output, and the user identity from the auth layer:

```python
# audit_middleware.py — add to hayhooks_server.py
import json, uuid, datetime
from starlette.middleware.base import BaseHTTPMiddleware

class AuditMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, log_path: str):
        super().__init__(app)
        self.log_path = log_path

    async def dispatch(self, request, call_next):
        if not request.url.path.startswith("/query/"):
            return await call_next(request)
        body = await request.body()
        request._body = body   # preserve for downstream
        response = await call_next(request)
        entry = {
            "event_id": str(uuid.uuid4()),
            "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
            "user_id": request.headers.get("x-user-id", "unknown"),
            "session_id": request.headers.get("x-session-id", "unknown"),
            "query": json.loads(body).get("query", ""),
            "status": response.status_code,
            # retrieved_chunks + answer_text are extracted from response body
            # by a second middleware that buffers the stream
        }
        with open(self.log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")
        return response
```

Run the Module 8 golden query set against this stack to verify end-to-end retrieval quality matches the pre-deployment baseline before going live.

---

## Software Bill of Materials (SBOM)

For defence and regulated deployments, every signed container image must ship with an accompanying SBOM that names every package, version, and license present in the image. SBOMs are the primary artifact auditors use to map your software to approved software lists and to detect dependencies with known CVEs after the fact.

### Generating an SBOM with Syft

[Syft](https://github.com/anchore/syft) (Anchore) generates SBOMs in CycloneDX, SPDX, and Syft-native formats. It runs fully offline against a local image, reads package manifests from the filesystem, and identifies every binary, library, and language-ecosystem package in one pass:

```bash
# Generate a CycloneDX SBOM for the signed image
syft scan my-rag-stack:v1.2.0 \
  -o cyclonedx-json=sbom.cdx.json \
  -o spdx-json=sbom.spdx.json

# Attest the SBOM alongside the image signature with cosign
cosign attest --key cosign.key \
  --predicate sbom.cdx.json \
  --type cyclonedx \
  my-rag-stack:v1.2.0
```

[CycloneDX](https://cyclonedx.org/) is the more common format for defence and regulated environments; [SPDX](https://spdx.dev/) is the ISO/IEC 5962 standard. Generating both is cheap and lets downstream consumers use whichever their tooling prefers.

### Minimum direct dependency set for the Haystack reference stack

The Haystack path gives you a small, enumerable direct dependency list. Every package below is Apache 2.0 or MIT licensed, appears in the SBOM, and has to be approved once during your initial authorization process. Transitive dependencies are pulled from the same internal PyPI mirror and appear in the SBOM automatically:

| Package | Purpose | License |
|---|---|---|
| `haystack-ai` | Core framework | Apache 2.0 |
| `qdrant-haystack` | Qdrant document store integration | Apache 2.0 |
| `ollama-haystack` | Ollama generator integration | Apache 2.0 |
| `docling-haystack` | docling parser integration | MIT |
| `sentence-transformers` | Embedders and cross-encoder rerankers | Apache 2.0 |
| `hayhooks` | FastAPI wrapper for Haystack pipelines | Apache 2.0 |
| `qdrant-client` | Transitive — pulled by `qdrant-haystack` | Apache 2.0 |
| `ollama` (Python client) | Transitive — pulled by `ollama-haystack` | MIT |
| `transformers` | Transitive — pulled by `sentence-transformers` | Apache 2.0 |
| `torch` | Transitive — pulled by `sentence-transformers` | BSD 3-Clause |

Seven direct packages. The SBOM expands this to approximately 80–120 transitive packages depending on your Torch variant (CPU-only Torch is smaller than the CUDA build); compare against the current course's raw-library approach which produces an SBOM with 150+ direct and transitive packages.

### Verifying SBOM against an approved software list

Many defence environments maintain an Approved Software List (ASL) or equivalent. Compare your SBOM against it before deployment:

```bash
# Example: check every package in the SBOM against a plain-text ASL
jq -r '.components[] | "\(.name)@\(.version)"' sbom.cdx.json | sort > sbom-packages.txt
comm -23 sbom-packages.txt approved-software-list.txt > unapproved-packages.txt
if [ -s unapproved-packages.txt ]; then
    echo "Unapproved packages detected:"
    cat unapproved-packages.txt
    exit 1
fi
```

Run this step in CI on the network-connected build host before the image is signed and transferred across the air gap. A package that was not in the ASL at build time is not allowed to enter the classified environment.

---

## Dependency Provenance

SBOMs tell you *what* is in the image; provenance tells you *where it came from and whether it was tampered with in transit*. For defence deployments, both are required.

### Pinning and hash-verifying Python dependencies

Use `pip`'s `--require-hashes` mode with a fully locked requirements file. Every package entry includes a SHA-256 hash of the wheel; pip refuses to install any wheel whose hash does not match:

```bash
# On the network-connected build host
pip-compile --generate-hashes requirements.in -o requirements.lock

# requirements.lock excerpt:
# haystack-ai==2.7.0 \
#     --hash=sha256:abc123... \
#     --hash=sha256:def456...
# qdrant-haystack==4.1.0 \
#     --hash=sha256:...

# In the air-gapped container build:
pip install --no-index --find-links=/opt/pypi-mirror --require-hashes -r requirements.lock
```

The `/opt/pypi-mirror` directory is the internal mirror you transferred across the air gap. Every wheel in it must match a hash in `requirements.lock`, or the install fails closed.

### Signing and verifying model weights

Model weights do not ship through PyPI, so hash-based provenance has to be explicit. Before transferring weights across the air gap, sign them with cosign (or generate SHA-256 checksums and sign the checksum file):

```bash
# On the network-connected build host — download and sign
huggingface-cli download nomic-ai/nomic-embed-text-v1.5 \
    --local-dir /opt/models/nomic-embed-text-v1.5
cosign sign-blob --key cosign.key \
    /opt/models/nomic-embed-text-v1.5/model.safetensors \
    --output-signature nomic-embed-text-v1.5.sig

# On the air-gapped host — verify before loading
cosign verify-blob --key cosign.pub \
    --signature nomic-embed-text-v1.5.sig \
    /opt/models/nomic-embed-text-v1.5/model.safetensors
```

Automate this as a pre-flight check in the container's entrypoint: if any model file fails signature verification, refuse to start the pipeline. This catches tampering between the sign step and the air-gapped load step.

---

## FIPS 140-3 Cryptography

[FIPS 140-3](https://csrc.nist.gov/Projects/cryptographic-module-validation-program) is the current US federal standard for cryptographic module validation, superseding FIPS 140-2 (which was sunset for new validations in September 2021). Any cryptography performed by the RAG stack — TLS for internal service-to-service communication, audit log integrity hashing, container image signatures — must use a FIPS 140-3 validated module if the deployment is FedRAMP High, IL4, IL5, IL6, or classified.

### Enabling FIPS on the host OS

On Red Hat Enterprise Linux 9 and Rocky Linux 9:

```bash
# Enable FIPS mode (requires reboot)
fips-mode-setup --enable
reboot

# Verify after reboot
fips-mode-setup --check
# Expected: "FIPS mode is enabled."
cat /proc/sys/crypto/fips_enabled
# Expected: 1
```

On Ubuntu 20.04/22.04, FIPS 140-3 validated modules require [Ubuntu Pro](https://ubuntu.com/pro) with FIPS enabled — this is a commercial feature. For fully open-source alternatives, use RHEL 9 or a rebuild (Rocky, AlmaLinux) with the OpenSSL FIPS provider.

### FIPS-constrained Python cryptography

The Python cryptography stack must use the system OpenSSL in FIPS mode rather than bundled copies. Two concrete rules:

1. **No `cryptography` wheels with bundled OpenSSL.** The `cryptography` package ships with a bundled OpenSSL by default; in FIPS mode you must build it against the system OpenSSL instead (`CRYPTOGRAPHY_OPENSSL_NO_LEGACY=1` and build from source against the FIPS-enabled OpenSSL).
2. **No `bcrypt` or `hashlib.blake2b`-dependent flows in audit-critical code paths.** FIPS 140-3 excludes certain algorithms — bcrypt is not approved; BLAKE2 is not approved. Stick to SHA-256, SHA-384, SHA-512, and HMAC-SHA-* for audit log integrity hashing.

Haystack itself uses no cryptography in the hot path — all hashing and signing happens at build time and at the audit-log layer. The constraint is on *your* code, not the framework.

### TLS between internal services

For IL4+ environments, even internal compose-network service-to-service traffic may need TLS. Configure Qdrant and Ollama with TLS:

```yaml
services:
  qdrant:
    image: qdrant/qdrant:v1.9.0
    environment:
      - QDRANT__SERVICE__ENABLE_TLS=true
      - QDRANT__TLS__CERT=/etc/qdrant/certs/cert.pem
      - QDRANT__TLS__KEY=/etc/qdrant/certs/key.pem
      - QDRANT__TLS__CA_CERT=/etc/qdrant/certs/ca.pem
    volumes:
      - ./certs:/etc/qdrant/certs:ro
```

Use an internal Certificate Authority to issue these certs. Rotate on the compliance cadence your authorization requires (typically 90 days for IL4+).

---

## STIG-Hardened Base Images

Defense deployments require base images that comply with DISA Security Technical Implementation Guides (STIGs). The [Iron Bank](https://p1.dso.mil/services/iron-bank) DoD container hardening program publishes STIG-compliant images for Red Hat UBI, Rocky Linux, Ubuntu, and many application runtimes; Iron Bank images ship pre-hardened and come with an accompanying STIG compliance report.

### Choosing a STIG base

For the Haystack stack, build from one of:

- `registry1.dso.mil/ironbank/redhat/ubi/ubi9` — Red Hat UBI 9, STIG-hardened, free to use
- `registry1.dso.mil/ironbank/rocky/rockylinux9` — Rocky Linux 9 equivalent
- `registry1.dso.mil/ironbank/opensource/python/python39` — pre-built Python on UBI

Iron Bank images are signed, scanned, and include a compliance report referencing the specific STIG version they satisfy. The Dockerfile earlier in this module uses `registry1.dso.mil/ironbank/redhat/ubi/ubi9:latest` as the base for this reason.

### STIG compliance scanning

Run a STIG compliance scan against the built image before signing and releasing it. [OpenSCAP](https://www.open-scap.org/) is the open-source scanner; Iron Bank images ship with matching SCAP content:

```bash
# Pull the STIG SCAP content for UBI 9
oscap-podman my-rag-stack:v1.2.0 xccdf eval \
    --profile xccdf_org.ssgproject.content_profile_stig \
    --results /tmp/stig-results.xml \
    --report /tmp/stig-report.html \
    /usr/share/xml/scap/ssg/content/ssg-rhel9-ds.xml
```

The report lists every control, pass/fail status, and remediation guidance. Treat any failed high-severity control as a release blocker.

### Qdrant and Ollama on STIG bases

Upstream Qdrant and Ollama images are not Iron Bank hardened. Two options:

1. **Rebuild from source** on an Iron Bank UBI base. Both projects have Dockerfiles in their repos that can be adapted to multi-stage builds on UBI.
2. **Accept the upstream image with compensating controls** — document the non-STIG base in the System Security Plan, note the compensating network isolation and SBOM coverage, and get ATO acceptance.

For IL2/IL4 deployments, option 2 is often acceptable with documentation. For IL5/IL6 and classified, option 1 is usually required.

---

## NIST SP 800-53 Control Mapping

[NIST SP 800-53 Revision 5](https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final) is the control catalog that underpins FedRAMP, CMMC, RMF, and most federal authorization frameworks. The Haystack RAG stack touches a specific subset of controls — here is the mapping auditors will ask for:

### Control families and stack mappings

| Family | Control | What the RAG stack provides | Evidence artifact |
|---|---|---|---|
| **AC** Access Control | AC-2 Account Management | User identity on every query via `x-user-id` header | Audit log entries with `user_id` field |
| **AC** | AC-3 Access Enforcement | Tenant filter enforced in query service layer, not application | `query.yaml` showing retriever filters |
| **AC** | AC-6 Least Privilege | Non-root container users (`USER 10001:10001`) | Dockerfile review |
| **AU** Audit and Accountability | AU-2 Event Logging | Minimum audit log schema above | `queries.jsonl` sample |
| **AU** | AU-3 Content of Audit Records | event_id, timestamp, user_id, query, retrieved chunks, answer, model, latency | Schema documentation |
| **AU** | AU-9 Protection of Audit Information | Append-only log store + tamper-evident hash chain | Hash chain verification script |
| **AU** | AU-11 Audit Record Retention | Retention per organization policy (typically 1+ year) | Retention policy reference |
| **CM** Configuration Management | CM-2 Baseline Configuration | Pipeline YAML files + pinned requirements | `indexing.yaml`, `query.yaml`, `requirements.lock` |
| **CM** | CM-3 Configuration Change Control | Signed pipeline releases + YAML diff review | Cosign attestation history |
| **CM** | CM-6 Configuration Settings | STIG-hardened base image, documented deviations | OpenSCAP scan report |
| **CM** | CM-8 System Component Inventory | CycloneDX SBOM | `sbom.cdx.json` |
| **IA** Identification and Authentication | IA-2 Identification and Authentication | Reverse-proxy or API gateway in front of Hayhooks | Gateway config + STIG scan |
| **RA** Risk Assessment | RA-5 Vulnerability Monitoring and Scanning | Trivy offline scan against synced DB; STIG scan on release | Weekly scan reports |
| **SA** System and Services Acquisition | SA-11 Developer Testing and Evaluation | Haystack evaluation pipeline running golden set | Evaluation report |
| **SC** System and Communications Protection | SC-7 Boundary Protection | Container network isolation + host `127.0.0.1:1416` bind | `compose.yaml` network config |
| **SC** | SC-8 Transmission Confidentiality and Integrity | TLS between internal services (IL4+) | TLS certificate chain |
| **SC** | SC-12 Cryptographic Key Establishment and Management | Cosign key management for image signing | Key management procedure document |
| **SC** | SC-13 Cryptographic Protection | FIPS 140-3 validated modules via `update-crypto-policies --set FIPS` | FIPS mode check output |
| **SC** | SC-28 Protection of Information at Rest | Full-disk encryption on the host; encrypted Qdrant volume | LUKS config, volume mount options |
| **SI** System and Information Integrity | SI-4 System Monitoring | Audit log stream fed to SIEM; query latency metrics | SIEM dashboard reference |
| **SI** | SI-7 Software, Firmware, and Information Integrity | SBOM attestation, model weight signature verification | Cosign verify-blob logs |

Generate the mapping as a living document stored alongside the pipeline YAML. Update it every time the stack changes.

### AU-3 audit log completeness check

NIST AU-3 requires audit records to contain enough information to establish what event occurred, when, where, the source, the outcome, and the identities involved. The audit log schema earlier in this module covers all six — here is the explicit mapping:

| AU-3 requirement | Audit log field |
|---|---|
| What type of event occurred | `event_type` (derived from URL path: `query`, `index`, `eval`) |
| When it occurred | `timestamp` (ISO-8601 with timezone) |
| Where it occurred | `service` (Hayhooks instance hostname + container ID) |
| Source of the event | `user_id`, `session_id`, request IP (from reverse proxy) |
| Outcome | `status` (HTTP status code), `error_message` if non-2xx |
| Identity of individuals or subjects | `user_id` |

Missing any of these is an AU-3 finding at audit time. Do not rely on the application layer to populate these fields voluntarily — enforce them in the middleware and reject any request that arrives without the required headers.

---

## RMF Artifact Templates

The [Risk Management Framework (RMF)](https://csrc.nist.gov/projects/risk-management) is the DoD and federal civilian process for authorizing information systems to operate. Authorization to Operate (ATO) requires a defined package of artifacts — the three most load-bearing for the RAG stack are the System Security Plan (SSP), the Security Assessment Report (SAR), and the Plan of Action and Milestones (POA&M).

### System Security Plan (SSP) outline for the RAG stack

An SSP is the canonical description of the system and how it satisfies its assigned controls. The Haystack RAG stack SSP is short because the architecture is simple. Outline:

1. **System Identification**
   - System name, version, responsible owner
   - Categorization: FIPS 199 impact levels (confidentiality, integrity, availability)
   - Authorization boundary: the compose stack + the host it runs on + the corpus storage volume
2. **System Description**
   - Purpose: retrieval-augmented question answering over an on-premises document corpus
   - Users: internal-only, authenticated via the upstream API gateway
   - Information types processed: reference NIST SP 800-60 classifications for the specific corpus content
3. **System Environment**
   - Architecture diagram: the Module 2 seven-stage diagram + the compose topology from earlier in this module
   - Hardware: reference Module 2 hardware sizing
   - Software inventory: the SBOM (`sbom.cdx.json`)
4. **System Interconnections**
   - None for fully air-gapped deployments. For internal-network-connected variants, list every external service and its authorization
5. **Applicable Laws, Regulations, and Policies**
   - HIPAA, ITAR, CUI Registry, or the specific regulation driving the air-gapped posture
6. **System Security Plan Approval**
   - Signature block for the Authorizing Official
7. **Control Implementation Summary**
   - The NIST SP 800-53 control mapping table above, expanded into per-control narratives
8. **Supporting Documentation**
   - Pipeline YAML files (`indexing.yaml`, `query.yaml`, `evaluation.yaml`)
   - Dockerfile, compose.yaml, requirements.lock
   - Audit log schema, retention policy, SIEM integration documentation
   - Incident response procedures
   - Configuration management procedures

Store the SSP in a controlled document repository adjacent to the pipeline YAML — when the pipeline changes, the SSP change-control is triggered automatically.

### Security Assessment Report (SAR)

The SAR is the independent assessor's report against the SSP. For the RAG stack, the SAR should cover:

- **Control testing results**: for each control in the mapping table, did the implementation pass, fail, or receive "not applicable"?
- **Vulnerability scan results**: Trivy (CVE), OpenSCAP (STIG), Bandit (Python static analysis)
- **Penetration test results**: focused on prompt injection (test corpus with adversarial documents), authentication bypass at the API gateway, and tenant isolation enforcement
- **Residual risks**: any risks accepted by the Authorizing Official, documented with mitigating controls

Assessors for classified systems typically require specific certifications (CISSP, CEH, CISA). Budget for an external assessor in the initial authorization cost.

### Plan of Action and Milestones (POA&M)

The POA&M tracks every finding from the SAR that was not fully remediated before ATO. Each entry includes:

- Finding ID and source (SAR section reference)
- Control family and specific control
- Weakness description
- Scheduled completion date
- Point of contact
- Resources required
- Status (open, in progress, closed, risk accepted)

For the RAG stack, common POA&M entries include:

- Non-STIG upstream Qdrant/Ollama images (compensating controls documented)
- Transitive Python dependencies without FIPS validation (documented non-use of those transitive paths)
- Embedding model weights not cryptographically signed by the original publisher (compensating internal re-signing documented)

Update the POA&M monthly. Track open findings against their scheduled completion dates.

### Impact level cheat sheet

The control depth scales with the system's impact level:

| Impact level | Authorizing framework | Additional requirements over baseline |
|---|---|---|
| Low | FedRAMP Low / IL2 | Baseline NIST SP 800-53 Low controls |
| Moderate | FedRAMP Moderate / IL4 | + FIPS 140-3 cryptography, + DAR encryption, + more frequent scanning |
| High | FedRAMP High / IL5 | + STIG-hardened base images, + continuous monitoring, + hardware root of trust |
| Classified | IL6 / classified | + TEMPEST considerations, + physical isolation, + cleared personnel only |

Identify your target impact level before starting the authorization work. The control depth and cost differ by an order of magnitude between Low and High.

---

## Key Takeaways

- Ship container images and model weights as signed, version-tagged artifacts transferred via approved media — `docker save`/`docker load` with cosign signatures; sign model weights separately with `cosign sign-blob`
- Ship a CycloneDX SBOM with every signed release (Syft generates it offline); compare against your approved software list before transfer
- Pin Python dependencies with `pip-compile --generate-hashes` and install with `--require-hashes` to fail closed on any tampered or unexpected wheel
- Build from a STIG-hardened base image (DISA Iron Bank UBI9); run OpenSCAP at release time and treat high-severity failures as blockers
- Enable FIPS 140-3 system-wide (`update-crypto-policies --set FIPS`) for any deployment targeting FedRAMP Moderate or higher; avoid non-approved algorithms (bcrypt, BLAKE2) in audit-critical code paths
- The Haystack stack maps to NIST SP 800-53 controls cleanly — pipeline YAML files cover CM-2/CM-3, the SBOM covers CM-8, the audit log middleware covers AU-2/AU-3/AU-9
- RMF authorization requires SSP, SAR, and POA&M — the SSP is short because the architecture is simple (compose stack + host + corpus volume); keep it alongside the pipeline YAML so change-control triggers together
- Hayhooks is the deployment unit: one FastAPI container that loads the pipeline YAML files and serves them as REST endpoints; application code is ~10 lines
- Enforce tenant isolation and document visibility filters at the query service layer, not in application code that callers can bypass
- The minimum audit log captures user, query, retrieved chunk IDs with source mapping, answer text, and model ID — this schema satisfies HIPAA access accounting, SOC 2 evidence, FedRAMP AU-2, and DoD NIST SP 800-53 AU-3 requirements in one pass
- Embedding model rotation always requires full re-indexing; use parallel collections to minimize downtime
- Back up the source document corpus separately from the vector index — the index is derivable, the corpus is not

## Unverified Claims

- Exact cosign flag names for offline transparency-log bypass (`--tlog-upload=false`, `--insecure-ignore-tlog`) should be confirmed against the current cosign release before use in production scripts — cosign's CLI flags have changed across versions.

## Related

- [Air-Gapped RAG: Overview and When to Use It](overview.md)
- [Air-Gapped RAG: Architecture Fundamentals](architecture-fundamentals.md)
- [Air-Gapped RAG: Document Ingestion and Parsing](document-ingestion-and-parsing.md)
- [Air-Gapped RAG: Chunking Strategies](chunking-strategies.md)
- [Air-Gapped RAG: Local Embeddings and Vector Stores](local-embeddings-vector-stores.md)
- [Air-Gapped RAG: Retrieval and Re-Ranking](retrieval-and-reranking.md)
- [Air-Gapped RAG: Local LLM Inference](local-llm-inference.md)
- [Air-Gapped RAG: Grounding, Citations, and Evaluation](grounding-citations-evaluation.md)
