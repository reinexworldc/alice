from providers.openai.provider import OpenAIProvider 
from openai import OpenAI
from pydantic import BaseModel


class LLMChat(BaseModel):
    def create_response(self, text):
        openai = OpenAIProvider(client=OpenAI())
                    
        response = openai.model_call(
        input_content=text, 
            model="gpt-5.2",
            stream=True
        )

        return response

    def handle_response(self):
        response = self.create_response()
        for chunk in response:
            if chunk.type == 'response.output_text.delta':
                print(chunk.delta, end='', flush=True)
