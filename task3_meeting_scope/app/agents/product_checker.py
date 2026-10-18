import os

import httpx


async def check_product_fit(feature: str) -> dict:
    url = f"{os.getenv('KNOWLEDGE_API_URL', 'http://localhost:8001').rstrip('/')}/api/v1/query"
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.post(url, json={"question": feature})
        response.raise_for_status()
        result = response.json()
    supported = result["confidence"] >= 0.7
    return {
        "product_fit": "built_in" if supported else "needs_review",
        "evidence": result["answer"],
        "confidence": result["confidence"],
    }

