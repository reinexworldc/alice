from providers.base import LLMProvider


class ChatAgent:
    def __init__(self, provider: LLMProvider):
        self.provider = provider,

    # Calls provider.stream() or provider.generate() (implemented by concrete provider, e.g. OpenAIProvider)
    def llm_output(self, message: str):
        if hasattr(self.provider, "stream"):
            return self.provider.output_stream(message)
        return iter([self.provider.output_generate(message)])
