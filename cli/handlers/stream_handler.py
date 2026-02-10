from typing import Any

from cli.views.parser import ChunkParser
from core.agent import ChatAgent


class StreamHandler:
    @staticmethod
    def stream_and_parse(
        agent: ChatAgent,
        parser: ChunkParser,
        message: str,
        tools: list[dict[str, Any]],
    ) -> tuple[list[str], list[dict[str, Any]]]:
        chunks: list[str] = []
        raw_chunks: list[dict[str, Any]] = []

        for chunk in agent.llm_output(message, tools=tools):
            raw_chunks.append(chunk)
            if chunk.get("content"):
                parser.parse(chunk=chunk["content"])
                chunks.append(chunk["content"])

        return chunks, raw_chunks
