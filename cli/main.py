from cli.handlers.command_handler import CommandHandler
from cli.handlers.context import SessionContext
from cli.handlers.input_handler import InputHandler
from cli.handlers.memory_handler import MemoryHandler
from cli.handlers.stream_handler import StreamHandler
from cli.handlers.tools_handler import ToolsHandler
from cli.prompt import PromptSessionController
from cli.views.parser import ChunkParser
from cli.commands import CommandsHelper
from core.agent import ChatAgent
from helpers.prompt.helper import PromptsHelper
from providers.openai.provider import OpenAIProvider
from rich.console import Console


def main():
    agent = ChatAgent(provider=OpenAIProvider())
    controller = PromptSessionController()
    parser = ChunkParser()
    commands_helper = CommandsHelper()
    prompts_helper = PromptsHelper()
    console = Console()
    context = SessionContext(
        agent=agent,
        controller=controller,
        parser=parser,
        commands_helper=commands_helper,
        prompts_helper=prompts_helper,
        console=console,
    )
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

            if CommandHandler.handle_command_if_any(context, message):
                continue

            MemoryHandler.ensure_memory_file(context)
            if message:
                MemoryHandler.write_user_message(context, message)

                tools = ToolsHandler.load_tools()
                chunks, raw_chunks = StreamHandler.stream_and_parse(
                    agent=context.agent,
                    parser=context.parser,
                    message=message,
                    tools=tools,
                )

                context.tools_by_index = ToolsHandler.collect_tool_calls(raw_chunks)
                ToolsHandler.execute_tool_calls(context.agent, context.tools_by_index)

                llm_message = "".join(chunks)
                MemoryHandler.write_assistant_message(context, llm_message)

            print("")
        except KeyboardInterrupt:
            continue
        except EOFError:
            break

if __name__ == "__main__":
    main()
