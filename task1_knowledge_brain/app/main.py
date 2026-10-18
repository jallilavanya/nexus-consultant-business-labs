import asyncio
import hashlib
import logging
import os

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.crawler.page_scraper import chunk_text, fetch_page
from app.crawler.sitemap_parser import parse_sitemap
from app.models.schemas import (
    EscalateRequest,
    ExpertResolveRequest,
    QueryRequest,
    QueryResponse,
    SyncResponse,
)
from app.rag.rag_engine import RagEngine
from app.rag.vector_store import KnowledgeStore
from app.rag.vision_processor import describe_image

app = FastAPI(title="AI Tech Consultant - Knowledge Brain", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
store = KnowledgeStore(os.getenv("CHROMA_PATH", "data/chroma"))
rag = RagEngine(store)
semaphore = asyncio.Semaphore(5)
tasks: dict[str, dict] = {}
schedule_task: asyncio.Task | None = None


async def _sync_page(client: httpx.AsyncClient, entry: dict) -> int:
    lastmod = entry.get("lastmod") or ""
    if lastmod and store.page_lastmod(entry["url"]) == lastmod:
        return 0
    async with semaphore:
        page = await fetch_page(client, entry["url"])
    page["lastmod"] = lastmod
    descriptions = await asyncio.gather(
        *(_describe_image_limited(image_url, client) for image_url in page["images"]),
        return_exceptions=True,
    )
    for image_url, description in zip(page["images"], descriptions):
        if isinstance(description, Exception):
            logging.warning("Screenshot description failed for %s: %s", image_url, description)
        elif description:
            page["text"] += f"\nScreenshot at {image_url}: {description}"
    chunks = chunk_text(page)
    store.replace_page_chunks(entry["url"], chunks)
    return len(chunks)


async def _describe_image_limited(image_url: str, client: httpx.AsyncClient):
    async with semaphore:
        return await describe_image(image_url, client)


async def sync_knowledge() -> dict:
    async with httpx.AsyncClient(
        timeout=30, follow_redirects=True, headers={"User-Agent": "AI-Tech-Consultant/1.0"}
    ) as client:
        entries = await parse_sitemap(client)
        results = await asyncio.gather(
            *(_sync_page(client, entry) for entry in entries),
            return_exceptions=True,
        )
        failures = [result for result in results if isinstance(result, Exception)]
        if failures:
            raise RuntimeError(f"{len(failures)} of {len(entries)} sitemap pages failed; first: {failures[0]}")
        deleted = store.delete_missing_pages({entry["url"] for entry in entries})
        return {"found": len(entries), "indexed": sum(results), "deleted": deleted}


async def _daily_sync() -> None:
    while True:
        try:
            await sync_knowledge()
        except Exception:
            logging.exception("Daily knowledge sync failed")
        await asyncio.sleep(24 * 60 * 60)


@app.on_event("startup")
async def startup() -> None:
    global schedule_task
    if os.getenv("ENABLE_DAILY_CRAWL", "false").lower() == "true":
        schedule_task = asyncio.create_task(_daily_sync())


@app.on_event("shutdown")
async def shutdown() -> None:
    if schedule_task:
        schedule_task.cancel()
        try:
            await schedule_task
        except asyncio.CancelledError:
            pass


@app.get("/health")
async def health():
    return {"status": "ok", "indexed_chunks": store.collection.count()}


@app.post("/api/v1/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    result = rag.answer(request.question)
    escalated = False
    if result["confidence"] < 0.7:
        task_id = hashlib.sha256(request.question.encode()).hexdigest()[:16]
        tasks.setdefault(
            task_id,
            {
                "id": task_id,
                "question": request.question,
                "answer": result["answer"],
                "confidence": result["confidence"],
                "status": "open",
            },
        )
        escalated = True
    result["escalation_created"] = escalated
    return result


@app.post("/api/v1/escalate")
async def escalate(request: EscalateRequest):
    task_id = hashlib.sha256(f"{request.question}:{len(tasks)}".encode()).hexdigest()[:16]
    tasks[task_id] = {
        "id": task_id,
        **request.model_dump(),
        "status": "open",
    }
    return {"task_id": task_id, "status": "open"}


@app.get("/api/v1/escalate")
async def list_escalations():
    return {"tasks": list(tasks.values())}


@app.post("/api/v1/expert-resolve")
async def expert_resolve(request: ExpertResolveRequest):
    item_id = hashlib.sha256(f"expert:{request.question}".encode()).hexdigest()
    url = str(request.article_url) if request.article_url else "expert://resolved"
    store.upsert(
        item_id,
        f"Question: {request.question}\nExpert answer: {request.answer}",
        {
            "article_url": url,
            "title": "Expert resolution",
            "category": "expert",
            "image_urls": [],
        },
    )
    return {"status": "ingested", "id": item_id}


@app.post("/api/v1/sync", response_model=SyncResponse)
async def sync_endpoint():
    try:
        return await sync_knowledge()
    except (httpx.HTTPError, RuntimeError, ValueError) as error:
        raise HTTPException(status_code=502, detail=str(error)) from error
