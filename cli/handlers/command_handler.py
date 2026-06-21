from cli.handlers.context import SessionContext
from core.helpers.prompt.helper import PromptsHelper
from core.helpers.prompt.errors import PromptNotFoundError


class CommandHandler:
    def __init__(self):
        self.prompts_helper = PromptsHelper()

    def handle_command_if_any(self, context: SessionContext, message: str) -> bool:
        if self.is_command(message):
            self.handle_command(context=context, text=message)
            return True

        return False

    def is_command(self, text: str) -> bool:
        return text.startswith("/")

    def handle_command(self, context: SessionContext, text: str) -> None:
        parts: list = text[1:].strip().split()
        command: str = parts[0]
        args: list[str] = parts[1:]

        if command == "workflow":
            if not args:
                context.renderer.warning("Использование: /workflow <name>")
                return

            workflow = args[0]

            try:
                context.agent.add_system_prompt(
                    self.prompts_helper.workflow_prompt(workflow)
                )
                context.renderer.success(f"Workflow переключён на {workflow}")

            except PromptNotFoundError as e:
                context.renderer.error(str(e))

            return
