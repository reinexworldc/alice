from providers.openai.provider import OpenAIProvider 
from openai import OpenAI
from prompt_toolkit import prompt
from prompt_toolkit import print_formatted_text as print


while True:
    message = prompt("You: ")
    if message.lower() in ['exit', 'quit', 'q']:
        break
    if message:
        openai = OpenAIProvider(client=OpenAI())
        
        response = openai.model_call(
            input_content=message, 
            model="gpt-5.2",
            stream=True
        )
        
        print("AI: ", end='', flush=True)
        for chunk in response:
            if chunk.type == 'response.output_text.delta':
                print(chunk.delta, end='', flush=True)
        print()