from openai import OpenAI
from providers.base import LLMProvider


class OpenAIProvider(LLMProvider):
    def __init__(self, client: OpenAI | None = None):
        self.client = client or OpenAI()

    def output_generate(self, prompt: str, messages: list[dict]) -> str:
        response = self.client.chat.completions.create(
            model="gpt-5.2",
            messages=messages
        )
        return response.choices[0].message.content

    def output_stream(self, prompt: str, messages: list[dict]):
        stream = self.client.chat.completions.create(
            model="gpt-5.2",
            messages=messages,
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta
            if delta and delta.content:
                yield delta.content
