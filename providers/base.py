from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    def llm_generate(self, prompt: str) -> str:
        raise NotImplementedError

    def llm_stream(self, prompt: str):
        yield self.llm_generate(prompt)
