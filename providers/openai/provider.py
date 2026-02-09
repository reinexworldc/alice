from openai import OpenAI
from providers.base import LLMProvider
from typing import Iterator


class OpenAIProvider(LLMProvider):
    def __init__(self, client: OpenAI | None = None):
        self.client = client or OpenAI()

    def llm_generate(
            self, 
            message: str, 
            tools: list[dict]
        ) -> str:
        response = self.client.chat.completions.create(
            model="gpt-5.2",
            messages=[{"role": "user", "content": message}],
            tools=tools,
        )
        return response.choices[0].message.content

    def llm_stream(
            self, 
            messages: list[dict], 
            tools: list[dict]
        ) -> Iterator[str]:
        stream = self.client.chat.completions.create(
            model="gpt-5.2",
            messages=messages,
            tools=tools,
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta
            if delta and delta.content:
                yield delta.content
