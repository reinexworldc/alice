from pathlib import Path

from dotenv import load_dotenv
from huggingface_hub import login
from rich.console import Console

from .handlers.command_handler import CommandHandler
from .handlers.context import SessionContext
from .handlers.input_handler import InputHandler
from core.handlers.memory_handler import MemoryHandler
from core.handlers.stream_handler import StreamHandler
from core.handlers.tools_handler import ToolsHandler
from .prompt import PromptSessionController
from .views.parser import ChunkParser
from .views.renderer import TerminalRenderer
from core.agent import ChatAgent
from core.helpers.prompt.helper import PromptsHelper
from core.providers.openai.provider import OpenAIProvider
from core.providers.transformers import TransformersProvider
from utils.config_utils import Config
from core.providers.config import ProvidersConfig


def main():
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")

    config = Config()
    data = config.read()

    # TODO: Separate to unic file.
    if not data:
        config.write({"provider": "", "model": ""})
        data = {"provider": "", "model": ""}

    def _data_to_num(data: dict):
        return {i + 1: key for i, key in enumerate(data)}

    def _print_config(data: dict):
        for i, name in enumerate(data, start=1):
            print(f"{i}: {name}")

    if data["provider"] == "":
        print("Select provider")
        providers = ProvidersConfig.available_providers()
        _print_config(providers)
        provider_to_num = _data_to_num(providers)
        num = int(input())
        data["provider"] = provider_to_num[num]

    if ProvidersConfig.supports_optional_auth(data["provider"]):
        token = input(
            "Hugging Face token (optional, press Enter to skip): "
        ).strip()
        if token:
            login(token=token)

    if data["model"] == "":
        print(f"Select model")
        models = ProvidersConfig.available_models(data["provider"])
        _print_config(models)
        model_to_num = _data_to_num(models)
        num = int(input())
        data["model"] = model_to_num[num]

    config.write(data)

    provider = ProvidersConfig.create(data["provider"], data["model"])
    agent = ChatAgent(provider=provider)

    controller = PromptSessionController()
    parser = ChunkParser()
    prompts_helper = PromptsHelper()
    console = Console()
    renderer = TerminalRenderer(console)
    context = SessionContext(
        agent=agent,
        controller=controller,
        parser=parser,
        prompts_helper=prompts_helper,
        console=console,
        renderer=renderer,
    )
    memory = MemoryHandler()
    tools_handler = ToolsHandler(
        agent=agent,
        memory_handler=memory,
        renderer=renderer,
    )
    commands_handler = CommandHandler()
    session = context.controller.session

    context.agent.add_system_prompt(context.prompts_helper.system_prompt())

    context.renderer.clear()

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
                memory.write_message(message, "User")

                followup_message = message
                # Future: separate tool call logic.
                while True:
                    tools = tools_handler.load_tools()
                    chunks, raw_chunks = StreamHandler.stream_and_parse(
                        agent=context.agent,
                        parser=context.parser,
                        message=followup_message,
                        tools=tools,
                        renderer=renderer,
                    )
                    context.tools_by_index = tools_handler.collect_tool_calls(
                        raw_chunks
                    )

                    if not context.tools_by_index:
                        break

                    tools_handler.execute_tool_calls(context.tools_by_index)

                    followup_message = "continue"

                llm_message = "".join(chunks)
                memory.write_message(llm_message, "Assistant")
            renderer.console.print()
        except KeyboardInterrupt:
            continue
        except EOFError:
            break


if __name__ == "__main__":
    main()
