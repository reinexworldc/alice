from providers.openai.provider import OpenAIProvider 
from openai import OpenAI

while True:
    message = input()
    if message:
        openai = OpenAIProvider(client=OpenAI())
        
        response = openai.model_call(
            input_content=message, 
            model="gpt-5.2",
            stream=True
        )
        
        for chunk in response:
            if chunk.type == 'response.output_text.delta':
                print(chunk.delta, end='', flush=True)
        print()
