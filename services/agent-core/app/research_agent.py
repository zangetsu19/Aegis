from __future__ import annotations

from agents import Agent, Runner

from .config import settings
from .research import ResearchTool, SearchResult
from .research_memory import ResearchMemory


class ResearchAgent:
    def __init__(self, memory: ResearchMemory):
        self.search = ResearchTool(max_results=6)
        self.memory = memory
        self.synthesizer = Agent(
            name="AEGIS Research Synthesizer",
            instructions=(
                "Synthesize research from supplied source snippets. Separate facts from "
                "inference, flag uncertainty and contradictions, and preserve source URLs. "
                "Do not invent citations or facts. Return concise markdown with Findings, "
                "Contradictions/Uncertainty, and Sources."
            ),
            model=settings.openai_model,
        )

    async def research(self, session_id: str, query: str) -> dict:
        results: list[SearchResult] = await self.search.search(query)
        sources = await self.search.fetch_sources(results)
        source_map = {source.url: source for source in sources}

        packets = []
        for result in results:
            source = source_map.get(result.url)
            content = source.text[:12000] if source else ""
            self.memory.save(session_id, query, result.title, result.url, result.snippet, content)
            packets.append(
                f"TITLE: {result.title}\nURL: {result.url}\nSNIPPET: {result.snippet}\nCONTENT: {content}"
            )

        if not packets:
            return {"query": query, "sources": [], "report": "No usable sources were found."}

        prompt = f"Research query: {query}\n\nSOURCE PACKETS:\n\n" + "\n\n---\n\n".join(packets)
        result = await Runner.run(self.synthesizer, prompt, max_turns=2)
        return {
            "query": query,
            "sources": [{"title": r.title, "url": r.url, "snippet": r.snippet} for r in results],
            "report": str(result.final_output),
        }
