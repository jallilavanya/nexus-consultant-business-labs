# Design

## Executive summary

This MVP connects support knowledge, customer-email workflows, and meeting-based scoping in one dashboard. The operational goal is traceability: customer answers cite documentation, estimates display component tasks and assumptions, and follow-up conversations show scope changes.

## Architecture

```text
                     +------------------------+
                     | Next.js dashboard     |
                     | localhost:3000        |
                     +-----------+------------+
                                 |
                REST (browser calls three APIs)
          +----------------------+----------------------+
          |                      |                      |
 +--------v---------+   +--------v--------+   +---------v----------+
 | Knowledge Brain  |<--| Inbox Agent     |   | Meeting Scope     |
 | FastAPI :8001    |   | Express :8002   |   | FastAPI :8003     |
 | ChromaDB         |   | classify/draft  |   | extract/check/    |
 | crawler + RAG    |<--| feedback rules  |   | estimate/diff     |
 +------------------+   +-----------------+   +-------------------+
          |
          +-- public help sitemap and article pages
          +-- optional Anthropic vision API for screenshots
```

**Service boundary:** Inbox and Scope call Knowledge through `POST /api/v1/query`. They have no Python code dependency on that service. The browser calls the public service APIs.

## Component decisions

- **FastAPI/Pydantic v2** for typed Python service boundaries and generated API documentation.
- **ChromaDB persistent collection** for local vector indexing and metadata-based page replacement/deletion.
- **Local feature hashing** as a no-account, deterministic starter embedding. It is not equivalent to a trained semantic model; evaluate and replace before production.
- **Anthropic Claude vision model** for screenshot descriptions only when an API key is present. Text retrieval and API operation do not depend on an LLM.
- **Express, TypeScript strict mode, and Zod** for schema-validated inbox requests and classification values.
- **Conservative human feedback threshold:** auto-send becomes eligible after 20 unchanged approvals for the same category and is revoked after corrections/overrides. This sample implementation is an in-memory demonstration; no emails are actually sent.
- **HTTP Knowledge API integration** gives the two consuming services an independently deployable, replaceable knowledge provider.

## Data flow

1. Sitemap sync fetches page locations and `lastmod`, concurrently (maximum five page fetches), retries transient request failures with exponential backoff, and replaces changed page chunks. Missing sitemap URLs are removed from the vector collection. Sync currently compares each page's last-modified value and fetches pages without a value each time.
2. Text and visual descriptions are chunked/indexed with article URL, category, last-modified value, and image URLs.
3. Query returns an extractive passage and matching source metadata. Confidence below `0.7` creates a human task. Expert answers become searchable vector entries.
4. Inbox classifies locally, gets help-center evidence for how-to messages, and returns a personalized draft. Human actions update the category's feedback counters.
5. Scope extraction identifies request/pain-point sentences, checks each request with the Knowledge API, estimates hours at the configured hourly rate, and renders a proposal. The delta endpoint compares normalized task names for additions, modifications, and removals.

## Failure modes and safeguards

- External HTTP failures are retried by the crawler, reported by manual sync, and surfaced by dependent APIs; task 2/3 never silently treat failed documentation lookups as successful answers.
- Search with no indexed content yields an explicit unknown answer and escalation.
- API input is validated and bounded. Confidence and estimated values have numeric constraints.
- Vision API image descriptions are optional; image URL metadata is still indexed without the key.
- The crawler is opt-in and can be triggered manually; enabling it generates real network and optional model costs.
- Sample response approval is not email delivery. Human feedback state is memory-only and not fit for production auditing or durable automation.
- Demo endpoints are unauthenticated and should not be exposed publicly.
- Hash embeddings and lexical requirement extraction can produce incorrect matches or estimates; require human validation before client commitments.

## Scaling to production

Add durable task/feedback storage, authenticated operator accounts, authorization and audit trails, a true email provider with send approvals, rate limiting, observability, secret management, robust image-domain allowlists, semantic embedding evaluation, and scheduled-job leadership/idempotency. Calibrate estimates and privacy/retention policies with domain owners.
