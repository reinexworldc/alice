from abc import ABC, abstractmethod
from typing import Iterator


class LLMProvider(ABC):
    @abstractmethod
    def llm_generate(self, messages: list[dict]) -> str:
        raise NotImplementedError

    @abstractmethod
    def llm_stream(
        self, 
        messages: list[dict], 
        tools: list[dict]
    ) -> Iterator[str]:
        """Stream LLM responses chunk by chunk."""
        pass