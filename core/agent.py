from providers.base import LLMProvider


class ChatAgent:
    def __init__(self, provider: LLMProvider, system_prompt: str | None = None):
        self.provider = provider
        self.messages = []

        if system_prompt:
            self.messages.append({
                "role": "system",
                "content": system_prompt,    
            })
            
    def add_system_prompt(self, text: str):
        self.messages.append({
            "role": "system",
            "content": text,    
        })        

    # Calls provider.stream() or provider.generate() (implemented by concrete provider, e.g. OpenAIProvider)
    def llm_output(self, user_message: str):
        self.messages.append({
        "role": "user",
        "content": user_message,     
    })

        def stream():
            assistant_chunks = []

            for chunk in self.provider.llm_stream(self.messages):
                assistant_chunks.append(chunk)
                yield chunk

            self.messages.append({
                "role": "assistant",
                "content": "".join(assistant_chunks)     
            })

        return stream()
