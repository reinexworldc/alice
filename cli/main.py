from .handlers.command_handler import CommandHandler
from .handlers.context import SessionContext
from .handlers.input_handler import InputHandler
from core.handlers.memory_handler import MemoryHandler
from core.handlers.stream_handler import StreamHandler
from core.handlers.tools_handler import ToolsHandler
from .prompt import PromptSessionController
from .views.parser import ChunkParser
from core.helpers.commands import CommandsHelper
from core.agent import ChatAgent
from core.helpers.prompt.helper import PromptsHelper
from core.providers.openai.provider import OpenAIProvider
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
    tools_handler = ToolsHandler(agent=agent)
    memory = MemoryHandler()
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

            memory.ensure_memory_file(context)
            if message:
                memory.write_user_message(context, message)

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
                memory.write_assistant_message(context, llm_message)
            print("")
        except KeyboardInterrupt:
            continue
        except EOFError:
            break


if __name__ == "__main__":
    main()
