from prompt_toolkit.formatted_text import HTML
from prompt_toolkit import print_formatted_text
from cli.prompt import PromptSessionController
from core.agent import ChatAgent
from providers.openai.provider import OpenAIProvider
import os
from rich.console import Console
from rich.markdown import Markdown
from rich.live import Live

def main():
    agent = ChatAgent(OpenAIProvider())
    controller = PromptSessionController()
    session = controller.session
    console = Console()
    
    os.system('cls' if os.name == 'nt' else 'clear')
    
    while True:
        try:
            text = session.prompt(
                "",
                bottom_toolbar=HTML(
                    "<hint>Enter: newline * Escape+Enter: send * Tab: indent</hint>"
                ),
                default="",
                validate_while_typing=False,
            )
            
            if not text.strip():
                continue
                
            if text.strip().lower() in ["exit", "quit", "q"]:
                break

            full_response = ""
            with Live(console=console, refresh_per_second=10) as live:
                for chunk in agent.stream(text):
                    full_response += chunk
                    md = Markdown(full_response)
                    live.update(md)

        except KeyboardInterrupt:
            continue
        except EOFError:
            break

if __name__ == "__main__":
    main()