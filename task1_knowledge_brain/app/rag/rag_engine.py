import re
import json

from app.rag.vector_store import KnowledgeStore


class RagEngine:
    def __init__(self, store: KnowledgeStore):
        self.store = store

    def answer(self, question: str) -> dict:
        matches = self.store.search(question, limit=5)
        if not matches:
            return {"answer": "I couldn't find a matching help article.", "sources": [], "confidence": 0.0}
        best = matches[0]
        confidence = max(0.0, min(1.0, 1.0 - float(best["distance"])))
        useful = [match for match in matches if 1.0 - match["distance"] >= 0.12]
        sources = []
        for match in useful[:3]:
            meta = match["metadata"]
            sources.append(
                {
                    "article_url": meta["article_url"],
                    "title": meta.get("title", meta["article_url"]),
                    "excerpt": re.sub(r"\s+", " ", match["document"])[:500],
                    "image_urls": json.loads(meta.get("image_urls", "[]")),
                }
            )
        if confidence < 0.2:
            answer = "I couldn't find a reliable answer in the available help content."
        else:
            answer = sources[0]["excerpt"]
        return {"answer": answer, "sources": sources, "confidence": confidence}
