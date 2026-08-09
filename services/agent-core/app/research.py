from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import quote_plus

import httpx

from .web import WebResearchTool, WebResult


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str


class ResearchTool:
    """Provider-neutral research layer with a lightweight public search backend."""

    def __init__(self, max_results: int = 5):
        self.max_results = max_results
        self.web = WebResearchTool()

    async def search(self, query: str) -> list[SearchResult]:
        # DuckDuckGo's HTML endpoint keeps v0.6 provider-independent.
        url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            response = await client.get(url, headers={"User-Agent": "AEGIS/0.6 research client"})
            response.raise_for_status()
            html = response.text

        from html.parser import HTMLParser

        class Parser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.results: list[SearchResult] = []
                self._href = ""
                self._title = ""
                self._snippet = ""
                self._mode = ""

            def handle_starttag(self, tag, attrs):
                attrs = dict(attrs)
                classes = attrs.get("class", "")
                if tag == "a" and "result__a" in classes:
                    self._href = attrs.get("href", "")
                    self._title = ""
                    self._mode = "title"
                elif "result__snippet" in classes:
                    self._snippet = ""
                    self._mode = "snippet"

            def handle_data(self, data):
                if self._mode == "title":
                    self._title += data
                elif self._mode == "snippet":
                    self._snippet += data

            def handle_endtag(self, tag):
                if tag == "a" and self._mode == "title" and self._href:
                    self.results.append(SearchResult(self._title.strip(), self._href, ""))
                    self._mode = ""
                elif self._mode == "snippet":
                    if self.results:
                        self.results[-1].snippet = self._snippet.strip()
                    self._mode = ""

        parser = Parser()
        parser.feed(html)
        return parser.results[: self.max_results]

    async def fetch_sources(self, results: list[SearchResult]) -> list[WebResult]:
        fetched: list[WebResult] = []
        for result in results:
            try:
                fetched.append(await self.web.fetch(result.url))
            except Exception:
                continue
        return fetched
