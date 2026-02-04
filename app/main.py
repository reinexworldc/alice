from providers.openai.provider import OpenAIProvider
import asyncio
from openai import AsyncOpenAI
from providers.openai.config import OpenAIConfig

async def main():
    openai = OpenAIProvider(client=AsyncOpenAI, config=OpenAIConfig)
    content = await openai.async_model_call(
        input_content="What planet is this?"
    )
    print(content)

if __name__ == "__main__":
    asyncio.run(main())
