from prompt_toolkit import PromptSession


class InputHandler:
    @staticmethod
    def read_user_input(session: PromptSession) -> str | None:
        message: str = session.prompt(
            "> ",
            default="",
            validate_while_typing=False,
        )

        if not message.strip():
            return None

        return message

    @staticmethod
    def is_exit_command(message: str) -> bool:
        return message.strip().lower() in ["exit", "quit", "q"]
