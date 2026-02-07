from prompt_toolkit.formatted_text import HTML
from prompt_toolkit import print_formatted_text
from cli.prompt import PromptSessionController
from core.agent import ChatAgent
from providers.openai.provider import OpenAIProvider
import os
from rich.console import Console, Group
from rich.markdown import Markdown
from rich.live import Live
from rich.panel import Panel
import sys
from .views.parser import ChunkParser

def main():
    agent = ChatAgent(OpenAIProvider())
    controller = PromptSessionController()
    parser = ChunkParser()
    session = controller.session
    console = Console()

    console.clear()
    
    while True:
        try:
            text = session.prompt(
                "",
                default="",
                validate_while_typing=False,
            )
            
            if not text.strip():
                continue
                
            if text.strip().lower() in ["exit", "quit", "q"]:
                break

            for chunk in agent.stream(text):
                parser.parse(chunk=chunk)
            print()
                    
        except KeyboardInterrupt:
            continue
        except EOFError:
            break

if __name__ == "__main__":
    main()