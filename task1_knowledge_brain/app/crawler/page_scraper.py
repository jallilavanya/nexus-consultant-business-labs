import asyncio
import hashlib
import random
import re
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup


async def fetch_page(client: httpx.AsyncClient, url: str, attempts: int = 4) -> dict:
    for attempt in range(attempts):
        try:
            response = await client.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            for element in soup(["script", "style", "nav", "footer", "header"]):
                element.decompose()
            title = soup.title.get_text(" ", strip=True) if soup.title else url
            body = soup.find("main") or soup.find("article") or soup.body or soup
            paragraphs = [
                text
                for node in body.find_all(["p", "h1", "h2", "h3", "li"])
                if (text := node.get_text(" ", strip=True))
            ]
            images = [
                image.get("src")
                for image in body.find_all("img")
                if image.get("src", "").startswith(("http://", "https://"))
            ]
            return {
                "url": url,
                "title": title,
                "text": "\n".join(paragraphs),
                "images": images,
                "category": urlparse(url).path.strip("/").split("/")[0] or "support",
            }
        except (httpx.HTTPError, ValueError):
            if attempt == attempts - 1:
                raise
            await asyncio.sleep(min(2**attempt + random.random(), 20))
    raise RuntimeError(f"Unable to fetch {url}")


def chunk_text(page: dict, max_chars: int = 1200) -> list[dict]:
    paragraphs = re.split(r"\n+", page["text"])
    chunks: list[str] = []
    current = ""
    for paragraph in paragraphs:
        if not paragraph:
            continue
        if current and len(current) + len(paragraph) > max_chars:
            chunks.append(current)
            current = ""
        current = f"{current}\n{paragraph}".strip()
    if current:
        chunks.append(current)
    image_context = "\n".join(f"Screenshot: {image}" for image in page["images"])
    if image_context:
        chunks.append(image_context)
    return [
        {
            "id": hashlib.sha256(f"{page['url']}:{index}".encode()).hexdigest(),
            "text": f"{page['title']}\n{chunk}",
            "metadata": {
                "article_url": page["url"],
                "title": page["title"][:500],
                "category": page["category"],
                "image_urls": page["images"],
                "lastmod": page.get("lastmod") or "",
            },
        }
        for index, chunk in enumerate(chunks)
    ]
