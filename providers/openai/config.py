from pydantic import BaseModel

class OpenAIConfig(BaseModel):
    model: str
    base_prompt: str
