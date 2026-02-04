from pydantic import BaseModel
from core.provider import BaseProvider
from openai import AsyncOpenAI
from .config import OpenAIConfig

class OpenAIProvider(BaseProvider):
    def __init__(
        self, 
        client: AsyncOpenAI, 
        config: OpenAIConfig
    ):
        self.client = client
        self.config = config
    # Api mismatch >> self.client.responses.create 
    async def async_model_call(
            self, 
            input_content: str
        ) -> str:
        response = await self.client.responses.create(
            model=self.config.model,
            input=input_content    
        )

        return response.output_text
