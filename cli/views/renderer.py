from pathlib import Path

from rich.console import Console
from rich.text import Text


class TerminalRenderer:
    """Render all conversational and tool output with one terminal style."""

    ASSISTANT_PREFIX = "alice  "
    CONTINUATION_PREFIX = "       "

    def __init__(self, console: Console | None = None):
        self.console = console or Console()
        self._assistant_active = False
        self._at_line_start = False

    def clear(self) -> None:
        self.console.clear()

    def assistant_chunk(self, content: str) -> None:
        if not content:
            return

        if not self._assistant_active:
            self.console.print(
                Text(self.ASSISTANT_PREFIX, style="bold bright_magenta"),
                end="",
            )
            self._assistant_active = True
            self._at_line_start = False

        indented = self._indent_continuations(content)
        self._write_ansi(indented)

    def assistant_end(self) -> None:
        if self._assistant_active:
            self.console.print()
        self._assistant_active = False
        self._at_line_start = False

    def action(self, tool_name: str, path: str = "") -> None:
        self.assistant_end()
        labels = {
            "get_directory": "Просматриваю каталог",
            "get_lines": "Считаю строки",
            "review_code": "Читаю файл",
            "apply_patch": "Изменяю файл",
        }
        label = labels.get(tool_name, f"Запускаю {tool_name}")
        target = Path(path).name if path else ""
        suffix = f" {target}" if target else ""
        self.console.print(
            Text.assemble(
                (self.CONTINUATION_PREFIX, ""),
                ("… ", "dim bright_magenta"),
                (f"{label}{suffix}", "dim"),
            )
        )

    def success(self, message: str) -> None:
        self.console.print(
            Text.assemble(
                (self.CONTINUATION_PREFIX, ""),
                ("✓ ", "bold green"),
                (message, "dim"),
            )
        )

    def warning(self, message: str) -> None:
        self.console.print(
            Text.assemble(
                (self.CONTINUATION_PREFIX, ""),
                ("! ", "bold yellow"),
                (message, "yellow"),
            )
        )

    def error(self, message: str) -> None:
        self.console.print(
            Text.assemble(
                (self.CONTINUATION_PREFIX, ""),
                ("✗ ", "bold red"),
                (message, "red"),
            )
        )

    def _indent_continuations(self, content: str) -> str:
        output = []
        for char in content:
            if self._at_line_start and char != "\n":
                output.append(self.CONTINUATION_PREFIX)
                self._at_line_start = False

            output.append(char)
            if char == "\n":
                self._at_line_start = True

        return "".join(output)

    def _write_ansi(self, content: str) -> None:
        parts = content.split("\n")
        for index, part in enumerate(parts):
            if part:
                self.console.print(Text.from_ansi(part), end="", soft_wrap=True)
            if index < len(parts) - 1:
                self.console.print()
