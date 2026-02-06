from providers.base import LLMProvider


class ChatAgent:
    def __init__(self, provider: LLMProvider):
        self.provider = provider

    def handle(self, text: str) -> str:
        return self.provider.generate(text)

    def stream(self, text: str):
        if hasattr(self.provider, "stream"):
            return self.provider.stream(text)
        return iter([self.provider.generate(text)])
