from cli.handlers.context import SessionContext


class CommandHandler:
    @staticmethod
    def handle_command_if_any(context: SessionContext, message: str) -> bool:
        if context.commands_helper.is_command(message):
            context.commands_helper.handle_command(agent=context.agent, text=message)
            return True

        return False
