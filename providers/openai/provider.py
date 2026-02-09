from openai import OpenAI
from providers.base import LLMProvider
from typing import Iterator


class OpenAIProvider(LLMProvider):
    def __init__(self, client: OpenAI | None = None):
        self.client = client or OpenAI()

    def llm_generate(
            self, 
            messages: list[dict], 
            tools: list[dict] | None = None,
        ) -> dict:
        response = self.client.chat.completions.create(
            model="gpt-5.2",
            messages=messages,
            tools=tools,
        )
        msg = response.choices[0].message

        return {
            "content": msg.content,
            "tool_calls": msg.tool_calls,     
        }

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
