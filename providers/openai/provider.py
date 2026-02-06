from pydantic import BaseModel, Field
from core.provider import BaseProvider
from openai import OpenAI
from typing import Iterator

class OpenAIProvider(BaseProvider, BaseModel):
    client: OpenAI = Field(default_factory=OpenAI)
    
    model_config = {
        'arbitrary_types_allowed': True  # Allow OpenAI client
    }

    def model_call(
            self, 
            input_content: str,
            model: str = "gpt-4",
            stream: bool = False
        ) -> str | Iterator[str]:
        """Call OpenAI API with streaming support"""
        response = self.client.responses.create(
            model=model,
            messages=[{"role": "user", "content": input_content}],    
            stream=stream
        )

        if stream:
            return response
        else:
            return response.content
        
    def _stream_response(self, response) -> Iterator[str]:
        """Generator that yields content chunks"""
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
