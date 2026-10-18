# Evaluation framework

## How to run

Run Python tests from each task directory with `python -m pytest -q`, and TypeScript tests with `cd task2_inbox_agent; npm test`. The runnable suites contain **26 Knowledge checks, 28 Inbox checks, and 25 Scope checks**, including 20+ parameterized cases per task. Evaluation test output prints the measured local quality/latency and API-cost estimate.

## Evaluation results

No tests have been run as part of generating this repository. Therefore, this document intentionally does not present fabricated measured results. The tables below describe the reproducible checks and their reported measurements. Runtime/latency depends on the machine; endpoint tests requiring a real knowledge index/sitemap/model are not part of these offline unit-test counts.

| Task | Offline cases | Accuracy / quality | Execution latency | Estimated API cost |
|---|---:|---|---|---|
| Knowledge Brain | 26 | Measured by local index, vector, metadata, timestamp, and empty-store assertions | Measured during local evaluation | $0 for deterministic local embeddings |
| Inbox Agent | 28 | Measured against 25 labeled intent examples and learning-threshold assertions | Measured during local evaluation | $0 for local rule classification |
| Meeting Scope | 25 | Measured by extraction, estimation, and delta contract assertions | Measured during local evaluation | $0 for local extraction/estimation |

## External / model comparison

| Model/path | Quality | Latency | Cost | Status |
|---|---|---|---|---|
| Deterministic feature hashing (retrieval) | Not a semantic benchmark; measured contract tests only | Measure locally with tests | $0 API cost | Implemented starter |
| Local rules (inbox classifier) | 25 labeled examples; test prints measured accuracy | Measure locally with tests | $0 API cost | Implemented starter |
| Local extraction and heuristic estimator | Contract tests; not expert-reviewed scope accuracy | Measure locally with tests | $0 API cost | Implemented starter |
| Claude 3.5 Sonnet vision | No reference-caption benchmark run | Depends on image/model/network | Usage billed by provider | Optional screenshot captions |
| Claude 3.5 Haiku vs Sonnet query drafting | Not implemented or benchmarked | Not measured | Not measured | No comparison claimed |

This repository does **not** claim that the model comparison has been run. For a valid production comparison, capture a fixed, representative, privacy-reviewed dataset; define expert-reviewed answer/intent/scope gold labels; run the same cases against each candidate with pinned model versions; record quality, median/p95 latency, token use, and provider price at test time; and retain failures as regressions.

## Current limitations

- Evaluation cases are deterministic contract/heuristic checks, not a representative production holdout.
- Test output latency includes local work and does not measure full crawler or external provider latency.
- API cost is estimated as zero only for offline tests using local rules/vectors; running crawling or Anthropic vision incurs network/provider usage not included in that estimate.
- Feature hashing can return weak semantic matches, and the current confidence score is a transformed distance rather than a calibrated probability.
- Scope estimates are illustrative, not commitments or calibrated developer forecasts.
