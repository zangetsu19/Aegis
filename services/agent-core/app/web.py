from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse

import httpx


@dataclass
class WebResult:
    url: str
    title: str
    text: str


class WebResearchTool:
    """Small, bounded web fetcher for the first AEGIS research milestone."""

    def __init__(self, timeout: float = 15.0, max_chars: int = 20_000):
        self.timeout = timeout
        self.max_chars = max_chars

    async def fetch(self, url: str) -> WebResult:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("Only absolute HTTP(S) URLs are allowed")

        headers = {"User-Agent": "AEGIS/0.5 research client"}
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            content_type = response.headers.get("content-type", "")
            if "text" not in content_type and "json" not in content_type:
                raise ValueError("Unsupported content type")
            text = response.text[: self.max_chars]

        title = parsed.netloc
        return WebResult(url=str(response.url), title=title, text=text)
