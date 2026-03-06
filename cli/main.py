from .handlers.command_handler import CommandHandler
from .handlers.context import SessionContext
from .handlers.input_handler import InputHandler
from core.handlers.memory_handler import MemoryHandler
from core.handlers.stream_handler import StreamHandler
from core.handlers.tools_handler import ToolsHandler
from .prompt import PromptSessionController
from .views.parser import ChunkParser
from core.agent import ChatAgent
from core.helpers.prompt.helper import PromptsHelper
from core.providers.openai.provider import OpenAIProvider
from core.providers.transformers import TransformersProvider
from rich.console import Console
from utils.config_utils import Config


def main():
    config = Config()

    if not config.exists():
        print("Choose agent provider (openai / transformers):")
        agent_provider = input().lower()

        if agent_provider == "openai":
            config.write({"provider": "openai"})
            agent = ChatAgent(provider=OpenAIProvider())

        elif agent_provider == "transformers":
            print("Choose model (llama):")
            model_name = input().lower()

            if model_name == "llama":
                config.write({"provider": "transformers", "model": "meta-llama/Llama-3.1-8B"})
                agent = ChatAgent(provider=TransformersProvider("meta-llama/Llama-3.1-8B"))

    else:
        data = config.read()

        if data["provider"] == "openai":
            agent = ChatAgent(provider=OpenAIProvider())
        
        elif data["provider"] == "transfomers":
            agent = ChatAgent(provider=TransformersProvider(data["model"]))

    controller = PromptSessionController()
    parser = ChunkParser()
    prompts_helper = PromptsHelper()
    console = Console()
    context = SessionContext(
        agent=agent,
        controller=controller,
        parser=parser,
        prompts_helper=prompts_helper,
        console=console,
    )
    memory = MemoryHandler()
    tools_handler = ToolsHandler(agent=agent, memory_handler=memory)
    commands_handler = CommandHandler()
    session = context.controller.session

    context.agent.add_system_prompt(context.prompts_helper.system_prompt())

    context.console.clear()

    while True:
        try:
            message = InputHandler.read_user_input(session)
            if message is None:
                continue

            if InputHandler.is_exit_command(message):
                break

            if commands_handler.handle_command_if_any(context, message):
                continue

            memory.ensure_memory_file()
            if message:
                memory.write_user_message(message)

                followup_message = message
                # Future: separate tool call logic.
                while True:
                    tools = tools_handler.load_tools()
                    chunks, raw_chunks = StreamHandler.stream_and_parse(
                        agent=context.agent,
                        parser=context.parser,
                        message=followup_message,
                        tools=tools,
                    )
                    context.tools_by_index = tools_handler.collect_tool_calls(
                        raw_chunks
                    )

                    if not context.tools_by_index:
                        break

                    tools_handler.execute_tool_calls(context.tools_by_index)

                    followup_message = "continue"

                llm_message = "".join(chunks)
                memory.write_assistant_message(llm_message)
            print("")
        except KeyboardInterrupt:
            continue
        except EOFError:
            break


if __name__ == "__main__":
    main()
