from datetime import datetime, timezone

from cli.handlers.context import SessionContext
from helpers.memory import MemoryHelper


class MemoryHandler:
    @staticmethod
    def ensure_memory_file(context: SessionContext) -> None:
        if context.memory_file_created:
            return

        name = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        context.memory_file = MemoryHelper.create_memory_file(name)
        context.memory_file_created = True

    @staticmethod
    def write_user_message(context: SessionContext, message: str) -> None:
        if context.memory_file is None:
            return

        MemoryHelper.write_memory(file=context.memory_file, text=message, role="User")

    @staticmethod
    def write_assistant_message(context: SessionContext, message: str) -> None:
        if context.memory_file is None:
            return

        MemoryHelper.write_memory(
            file=context.memory_file, text=message, role="Assistant"
        )
