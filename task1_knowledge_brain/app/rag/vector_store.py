import hashlib
import json
import math
import re
from pathlib import Path

import chromadb


def embed(text: str, dimensions: int = 384) -> list[float]:
    """Create a stable, dependency-free token vector for local semantic lookup."""
    vector = [0.0] * dimensions
    for token in re.findall(r"[a-z0-9]+", text.lower()):
        digest = hashlib.blake2b(token.encode(), digest_size=8).digest()
        index = int.from_bytes(digest[:4], "little") % dimensions
        vector[index] += 1.0 if digest[4] % 2 else -1.0
    norm = math.sqrt(sum(value * value for value in vector)) or 1.0
    return [value / norm for value in vector]


class KnowledgeStore:
    def __init__(self, path: str | None = None):
        persist_path = path or str(Path("data") / "chroma")
        Path(persist_path).parent.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=persist_path)
        self.collection = self.client.get_or_create_collection(
            "knowledge", metadata={"hnsw:space": "cosine"}
        )

    def upsert(self, item_id: str, text: str, metadata: dict) -> None:
        safe_metadata = dict(metadata)
        if isinstance(safe_metadata.get("image_urls"), list):
            safe_metadata["image_urls"] = json.dumps(safe_metadata["image_urls"])
        self.collection.upsert(
            ids=[item_id],
            documents=[text],
            metadatas=[safe_metadata],
            embeddings=[embed(text)],
        )

    def search(self, query: str, limit: int = 5) -> list[dict]:
        if self.collection.count() == 0:
            return []
        results = self.collection.query(
            query_embeddings=[embed(query)],
            n_results=min(limit, self.collection.count()),
            include=["documents", "metadatas", "distances"],
        )
        rows = []
        for index, doc in enumerate(results["documents"][0]):
            rows.append(
                {
                    "document": doc,
                    "metadata": results["metadatas"][0][index],
                    "distance": results["distances"][0][index],
                }
            )
        return rows

    def delete_missing_pages(self, live_urls: set[str]) -> int:
        current = self.collection.get(include=["metadatas"])
        stale = [
            item_id
            for item_id, metadata in zip(current["ids"], current["metadatas"])
            if metadata.get("category") != "expert"
            and metadata.get("article_url") not in live_urls
        ]
        if stale:
            self.collection.delete(ids=stale)
        return len(stale)

    def page_lastmod(self, article_url: str) -> str | None:
        current = self.collection.get(
            where={"article_url": article_url},
            include=["metadatas"],
            limit=1,
        )
        if not current["metadatas"]:
            return None
        return current["metadatas"][0].get("lastmod")

    def replace_page_chunks(self, article_url: str, chunks: list[dict]) -> None:
        expected = {chunk["id"] for chunk in chunks}
        existing = self.collection.get(
            where={"article_url": article_url},
            include=["metadatas"],
        )
        stale = [item_id for item_id in existing["ids"] if item_id not in expected]
        if stale:
            self.collection.delete(ids=stale)
        for chunk in chunks:
            self.upsert(chunk["id"], chunk["text"], chunk["metadata"])
