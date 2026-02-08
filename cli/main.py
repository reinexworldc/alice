from cli.prompt import PromptSessionController
from core.agent import ChatAgent
from providers.openai.provider import OpenAIProvider
from rich.console import Console
from .views.parser import ChunkParser
from pathlib import Path

def main():
    root = Path(__file__).resolve().parents[1]
    prompts_path = root / "prompts"

    system_prompt = (prompts_path / "system_prompt.md").read_text(
        encoding="utf-8"
    ) if prompts_path.exists() else ""

    agent = ChatAgent(
        provider=OpenAIProvider(), 
        system_prompt=system_prompt,
    )

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