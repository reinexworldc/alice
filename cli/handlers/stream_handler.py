from typing import Any

from cli.views.parser import ChunkParser
from core.agent import ChatAgent


class StreamHandler:
    @staticmethod
    def stream_and_parse(
        agent: ChatAgent,
        parser: ChunkParser,
        message: str,
        tools: list[dict],
    ) -> tuple[list[str], list[dict]]:
        chunks: list[str] = []
        raw_chunks: list[dict] = []
        
        chunk: dict
        for chunk in agent.llm_output(message, tools=tools):
            raw_chunks.append(chunk)
            if chunk.get("content"):
                content: str = chunk["content"]
                parser.parse(content)
                chunks.append(content)

        return chunks, raw_chunks
