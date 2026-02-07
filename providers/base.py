from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    def output_generate(self, prompt: str) -> str:
        raise NotImplementedError

    def output_stream(self, prompt: str):
        yield self.generate(prompt)
