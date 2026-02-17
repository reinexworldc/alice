from abc import ABC, abstractmethod
from typing import Any, Iterator


class LLMProvider(ABC):
    @abstractmethod
    def llm_generate(self, messages: list[dict]) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def llm_stream(
        self, messages: list[dict], tools: list[dict]
    ) -> Iterator[dict[str, Any]]:
        """Stream LLM responses chunk by chunk."""
        pass
