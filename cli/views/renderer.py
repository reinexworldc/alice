from pathlib import Path

from rich.console import Console
from rich.live import Live
from rich.text import Text


class TerminalRenderer:
    """Render all conversational and tool output with one terminal style."""

    ASSISTANT_PREFIX = "alice  "
    CONTINUATION_PREFIX = "       "

    def __init__(self, console: Console | None = None):
        self.console = console or Console()
        self._assistant_active = False
        self._at_line_start = False
        self._status_live: Live | None = None
        self._status_message = ""

    def clear(self) -> None:
        self._stop_status()
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
            "get_directory": "Watching directory",
            "get_lines": "Counting lines",
            "review_code": "Reading file",
            "create_file": "Creating file",
            "apply_patch": "Modifying file",
        }
        label = labels.get(tool_name, f"Running {tool_name}")
        target = Path(path).name if path else ""
        suffix = f" {target}" if target else ""
        self._stop_status()
        self._status_message = f"{label}{suffix}"
        self._status_live = Live(
            self._status_text("…", self._status_message, "dim bright_magenta"),
            console=self.console,
            refresh_per_second=10,
        )
        self._status_live.start(refresh=True)

    def success(self, message: str | None = None) -> None:
        if self._status_live:
            self._finish_status("✓", self._status_message, "bold green")
            return

        if message is None:
            return
        self.console.print(
            self._status_text("✓", message, "bold green")
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
        if self._status_live:
            status_message = f"{self._status_message} — {message}"
            self._finish_status("✗", status_message, "bold red")
            return

        self.console.print(
            self._status_text("✗", message, "bold red", "red")
        )

    def _status_text(
        self,
        symbol: str,
        message: str,
        symbol_style: str,
        message_style: str = "dim",
    ) -> Text:
        return Text.assemble(
            (self.CONTINUATION_PREFIX, ""),
            (f"{symbol} ", symbol_style),
            (message, message_style),
        )

    def _finish_status(self, symbol: str, message: str, style: str) -> None:
        if not self._status_live:
            return
        self._status_live.update(
            self._status_text(symbol, message, style),
            refresh=True,
        )
        self._status_live.stop()
        self.console.print()
        self._status_live = None
        self._status_message = ""

    def _stop_status(self) -> None:
        if self._status_live:
            self._status_live.stop()
        self._status_live = None
        self._status_message = ""

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
