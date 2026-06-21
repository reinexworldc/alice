from typing import Any

from cli.views.parser import ChunkParser
from cli.views.renderer import TerminalRenderer
from core.agent import ChatAgent


class StreamHandler:
    @staticmethod
    def stream_and_parse(
        agent: ChatAgent,
        parser: ChunkParser,
        message: str,
        tools: list[dict],
        renderer: TerminalRenderer,
    ) -> tuple[list[str], list[dict]]:
        chunks: list[str] = []
        raw_chunks: list[dict] = []
        
        chunk: dict
        for chunk in agent.llm_output(message, tools=tools):
            raw_chunks.append(chunk)
            if chunk.get("content"):
                content: str = chunk["content"]
                renderer.assistant_chunk(parser.parse(content))
                chunks.append(content)

        renderer.assistant_end()

        return chunks, raw_chunks
