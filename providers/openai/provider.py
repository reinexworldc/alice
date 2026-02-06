from openai import OpenAI
from providers.base import LLMProvider


class OpenAIProvider(LLMProvider):
    def __init__(self, client: OpenAI | None = None):
        self.client = client or OpenAI()

    def generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model="gpt-5.2",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    def stream(self, prompt: str):
        stream = self.client.chat.completions.create(
            model="gpt-5.2",
            messages=[{"role": "user", "content": prompt}],
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta
            if delta and delta.content:
                yield delta.content
