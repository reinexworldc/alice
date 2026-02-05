from pydantic import BaseModel
from core.provider import BaseProvider
from openai import OpenAI

class OpenAIProvider(BaseProvider):
    def __init__(
        self, 
        client: OpenAI, 
    ):
        self.client = client
    def model_call(
            self, 
            input_content: str,
            model: str,
            stream: bool
        ) -> str:
        response = self.client.responses.create(
            model=model,
            input=input_content,    
            stream=stream
        )

        if stream:
            return response
        else:
            return response.content
