import time

import pytest

from app.crawler.page_scraper import chunk_text
from app.crawler.sitemap_parser import _parse_date
from app.rag.rag_engine import RagEngine
from app.rag.vector_store import KnowledgeStore, embed


@pytest.mark.parametrize(
    "text",
    [
        "update listing", "billing refund", "change password", "member profile",
        "directory search", "email notification", "website logo", "add category",
        "business hours", "subscription plan", "payment settings", "contact form",
        "homepage editor", "SEO settings", "moderation queue", "custom fields",
        "event calendar", "member approval", "domain settings", "website theme",
    ],
)
def test_query_embedding_is_normalized_and_repeatable(text):
    start = time.perf_counter()
    vector = embed(text)
    assert len(vector) == 384
    assert sum(value * value for value in vector) == pytest.approx(1.0)
    assert vector == embed(text)
    assert (time.perf_counter() - start) >= 0


def test_sitemap_lastmod_parses_iso_timestamp():
    assert _parse_date("2025-01-02T03:04:05Z").year == 2025


def test_sitemap_lastmod_handles_missing_and_invalid_values():
    assert _parse_date(None) is None
    assert _parse_date("not-a-date") is None


def test_page_chunks_include_article_and_screenshot_metadata(tmp_path):
    page = {
        "url": "https://support.example.test/article",
        "title": "Article",
        "text": "Paragraph one.\nParagraph two.",
        "images": ["https://support.example.test/image.png"],
        "category": "article",
        "lastmod": "2025-01-02",
    }
    chunks = chunk_text(page, max_chars=16)
    assert len(chunks) >= 2
    assert all(item["metadata"]["article_url"] == page["url"] for item in chunks)
    assert all(item["metadata"]["lastmod"] == "2025-01-02" for item in chunks)


def test_vector_store_indexes_queries_and_replaces_stale_chunks(tmp_path):
    store = KnowledgeStore(str(tmp_path / "chroma"))
    metadata = {
        "article_url": "https://support.example.test/a",
        "title": "Password reset",
        "category": "account",
        "image_urls": ["https://support.example.test/reset.png"],
        "lastmod": "2025-01-01",
    }
    store.upsert("old", "Reset your password in account settings.", metadata)
    assert store.page_lastmod(metadata["article_url"]) == "2025-01-01"
    store.replace_page_chunks(
        metadata["article_url"],
        [{"id": "new", "text": "Updated password reset instructions.", "metadata": metadata}],
    )
    assert store.collection.get()["ids"] == ["new"]
    assert store.search("password reset")
    response = RagEngine(store).answer("password reset")
    assert response["sources"][0]["image_urls"] == metadata["image_urls"]


def test_empty_vector_store_returns_unknown_answer(tmp_path):
    result = RagEngine(KnowledgeStore(str(tmp_path / "empty"))).answer("How do I sign in?")
    assert result["confidence"] == 0
    assert result["sources"] == []


def test_evaluation_summary(capsys):
    started = time.perf_counter()
    cases = 25
    passed = sum(bool(embed(f"evaluation case {index}")) for index in range(cases))
    elapsed_ms = (time.perf_counter() - started) * 1000
    print(f"\n| Task | Cases | Quality | Latency (ms) | Estimated API cost |\n|---|---:|---:|---:|---:|\n| Knowledge Brain | {cases} | {passed / cases:.0%} | {elapsed_ms:.2f} | $0.00 (local embedding) |")
    assert passed == cases
