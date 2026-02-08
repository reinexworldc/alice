from cli.prompt import PromptSessionController
from core.agent import ChatAgent
from providers.openai.provider import OpenAIProvider
from rich.console import Console
from .views.parser import ChunkParser
from core.prompts.helper import PromptsHelper
from cli.commands import CommandsHelper

def main():
    agent = ChatAgent(
        provider=OpenAIProvider(), 
    )
    controller = PromptSessionController()
    parser = ChunkParser()
    commands_helper = CommandsHelper()
    prompts_helper = PromptsHelper()
    console = Console()
    session = controller.session

    agent.add_system_prompt(prompts_helper.system_prompt())

    console.clear()

    while True:
        try:
            message = session.prompt(
                "",
                default="",
                validate_while_typing=False,
            )

            if commands_helper.is_command(message):
                commands_helper.handle_command(agent=agent, text=message)
                continue
            
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