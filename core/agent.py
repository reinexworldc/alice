from providers.base import LLMProvider
from pathlib import Path
from typing import TypedDict, List, Optional


class ChatAgent:
    def __init__(
        self, provider: LLMProvider, 
        system_prompt: str | None = None
        ):
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
    def llm_output(self, user_message: str, tools: list[dict]):
        self.messages.append({
        "role": "user",
        "content": user_message,     
    })

        def stream():
            assistant_chunks = []

            for chunk in self.provider.llm_stream(messages=self.messages, tools=tools):
                if chunk["content"]:
                    assistant_chunks.append(chunk["content"])
                yield chunk

            self.messages.append({
                "role": "assistant",
                "content": "".join(assistant_chunks),
                "tools": tools   
            })

        return stream()

class AgentTools:
    @staticmethod
    def apply_path(self):
        pass

    @staticmethod
    def get_directory(path: str | Path) -> dict:
        path = Path(path).expanduser().resolve()

        if not path.exists():
            raise FileNotFoundError(f"Path does not exist: {path}")
        
        if not path.is_dir():
            raise NotADirectoryError(f"Not a directory: {path}")
        
        directories = []
        files = []

        for item in path.iterdir():
            if item.is_dir():
                directories.append(item.name)
            else:
                files.append(item.name)

        return {
            "path": str(path),
            "directories": sorted(directories),
            "files": sorted(files)     
        }
    