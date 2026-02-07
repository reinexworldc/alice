from cli.prompt import PromptSessionController
from core.agent import ChatAgent
from providers.openai.provider import OpenAIProvider
from rich.console import Console
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
            message = session.prompt(
                "",
                default="",
                validate_while_typing=False,
            )
            
            if not message.strip():
                continue
                
            if message.strip().lower() in ["exit", "quit", "q"]:
                break

            for chunk in agent.llm_output(message):
                parser.parse(chunk=chunk)
            print()
                    
        except KeyboardInterrupt:
            continue
        except EOFError:
            break

if __name__ == "__main__":
    main()