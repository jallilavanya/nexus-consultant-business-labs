import base64
import mimetypes
import os

import httpx


async def describe_image(image_url: str, client: httpx.AsyncClient) -> str | None:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    image_response = await client.get(image_url)
    image_response.raise_for_status()
    content_type = image_response.headers.get("content-type", "image/png").split(";")[0]
    media_type = content_type if content_type.startswith("image/") else mimetypes.guess_type(image_url)[0]
    if media_type not in {"image/jpeg", "image/png", "image/gif", "image/webp"}:
        return None
    encoded = base64.b64encode(image_response.content).decode("ascii")
    response = await client.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": os.getenv("ANTHROPIC_VISION_MODEL", "claude-3-5-sonnet-latest"),
            "max_tokens": 300,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": encoded,
                            },
                        },
                        {
                            "type": "text",
                            "text": "Describe the visible software UI, including options, buttons, and settings.",
                        },
                    ],
                }
            ],
        },
        timeout=60,
    )
    response.raise_for_status()
    return "\n".join(
        item["text"] for item in response.json().get("content", []) if item.get("type") == "text"
    )

