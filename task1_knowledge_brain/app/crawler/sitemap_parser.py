from datetime import datetime
from xml.etree import ElementTree

import httpx


SITEMAP_URL = "https://support.brilliantdirectories.com/support/sitemap.xml"


async def parse_sitemap(client: httpx.AsyncClient, sitemap_url: str = SITEMAP_URL):
    response = await client.get(sitemap_url)
    response.raise_for_status()
    root = ElementTree.fromstring(response.content)
    pages = []
    for node in root.iter():
        if node.tag.rsplit("}", 1)[-1] != "url":
            continue
        values = {
            child.tag.rsplit("}", 1)[-1]: (child.text or "").strip()
            for child in node
        }
        if values.get("loc"):
            pages.append(
                {
                    "url": values["loc"],
                    "lastmod": values.get("lastmod"),
                    "lastmod_dt": _parse_date(values.get("lastmod")),
                }
            )
    return pages


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None

