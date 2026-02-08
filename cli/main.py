from cli.prompt import PromptSessionController
from core.agent import ChatAgent
from providers.openai.provider import OpenAIProvider
from rich.console import Console
from .views.parser import ChunkParser
from core.prompts.helper import PromptsHelper
from cli.commands import CommandsHelper
from core.memory import MemoryHelper
from datetime import datetime, timezone

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

    memory_file_created = False

    while True:
        try:
            message: str = session.prompt(
                "> ",
                default="",
                validate_while_typing=False,
            )
                
            if not message.strip():
                continue
                
            if message.strip().lower() in ["exit", "quit", "q"]:
                break

            if commands_helper.is_command(message):
                commands_helper.handle_command(agent=agent, text=message)
                continue
            
            if not memory_file_created:
                # Upgrade after >> Session id & Prompt Hash
                name = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
                file = MemoryHelper.create_memory_file(name)
                memory_file_created = True

            if memory_file_created and message:
                MemoryHelper.write_memory(
                    file=file, 
                    text=message, 
                    role="User"
                )

                chunks = []
                for chunk in agent.llm_output(message):
                    parser.parse(chunk=chunk)
                    chunks.append(chunk)
                
                llm_message = " ".join(chunks)

                MemoryHelper.write_memory(
                    file=file, 
                    text=llm_message, 
                    role="Assistant"
                )

            print("") 

        except KeyboardInterrupt:
            continue
        except EOFError:
            break

if __name__ == "__main__":
    main()