# AI Tech Consultant

A local, containerized MVP with three cooperating services and a unified Next.js dashboard:

- **Knowledge Brain** — asynchronously crawls the Brilliant Directories support sitemap, indexes articles in persistent ChromaDB, retrieves grounded sources, and optionally generates screenshots' visual descriptions using Anthropic.
- **Inbox Agent** — classifies messages, retrieves documentation for how-to replies, serves 50 sample emails, and tracks human review feedback before enabling a category's auto-send threshold.
- **Meeting Scope** — extracts candidate requirements from transcripts, checks product documentation over the Knowledge Brain HTTP API, estimates effort, creates a Markdown proposal, and compares follow-up scope changes.
- **Dashboard** — interactive Knowledge, Inbox, and Scope tabs.

## Prerequisites

- Docker Desktop with the Compose plugin.
- Optional: Anthropic API key for screenshot visual descriptions. Local services and text search do not require it.
- Network access to the support sitemap to run a real knowledge sync.

## Configure and run

Copy `.env.example` to `.env` and set `ANTHROPIC_API_KEY` only if using the optional vision feature. Start the full system from the repository root:

```powershell
docker compose up --build
```

Open the dashboard at <http://localhost:3000>. API docs are available at <http://localhost:8001/docs> (Knowledge Brain), <http://localhost:8002/api/v1/health> (Inbox), and <http://localhost:8003/docs> (Scope Engine).

The crawler runs on startup only when `ENABLE_DAILY_CRAWL=true`; it syncs immediately and then every 24 hours. To index the support site manually, use `POST http://localhost:8001/api/v1/sync`. It can take time and makes external requests. You can inspect open human tasks at `GET /api/v1/escalate` and add an expert response using `POST /api/v1/expert-resolve`.

The vector store uses a deterministic local feature-hashing embedding to keep the starter runnable without an embedding account or model download. Production retrieval quality requires replacing this with a benchmarked semantic embedding model. Anthropic is only called for screenshot descriptions when an API key is configured. The included answer generator is extractive; it does not invent an LLM-generated answer.

The inbox review controls record **demo feedback only**—they do not send email. The auto-send threshold and revocation are in-memory and reset when the service restarts. Do not connect this demo to live sending without durable audit storage, authentication, policy checks, and explicit operational approval.

## APIs

| Service | Endpoint | Purpose |
|---|---|---|
| Knowledge | `POST /api/v1/query` | Grounded answer, sources, confidence, and low-confidence escalation |
| Knowledge | `POST /api/v1/escalate` / `GET /api/v1/escalate` | Create/list unresolved expert tasks |
| Knowledge | `POST /api/v1/expert-resolve` | Index an expert-written resolution |
| Knowledge | `POST /api/v1/sync` | Synchronize sitemap pages and remove deleted content |
| Inbox | `GET /api/v1/emails` | Load the 50-example inbox |
| Inbox | `POST /api/v1/draft` | Classify and draft; how-to intent queries Knowledge via HTTP |
| Inbox | `POST /api/v1/feedback` | Record operator approval, edit, override, or failure |
| Scope | `POST /api/v1/scope` | Requirements, product checks, estimate, proposal |
| Scope | `POST /api/v1/scope/delta` | Compare the revised scope against a supplied baseline |

Task 2 and Task 3 use only Task 1's REST API for knowledge access; neither imports its Python code.

## Local development and tests

Python, run separately from each task directory:

```powershell
cd task1_knowledge_brain
python -m pip install -r requirements.txt
python -m pytest -q
```


```powershell
cd task3_meeting_scope
python -m pip install -r requirements.txt
python -m pytest -q
```

TypeScript:

```powershell
cd task2_inbox_agent
npm install
npm test
npx tsc --noEmit
```

Dashboard:

```powershell
cd frontend
npm install
npm run dev
```

For local dashboard development, run all three APIs too. `NEXT_PUBLIC_*_API_URL` variables can point to other hosts; configure API CORS origins accordingly.

See [DESIGN.md](./DESIGN.md), [EVALS.md](./EVALS.md), and [AI_LOG.md](./AI_LOG.md) for boundaries, evaluation methodology, and known limitations.
