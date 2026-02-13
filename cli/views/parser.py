from pydantic import BaseModel
from typing import ClassVar


class ChunkParser(BaseModel):
    """
    A parser that toggles colored output when detecting code block markers (```)
    and handles bold text markers (**), removing the markers from output.
    """

    active: bool = False
    bold: bool = False
    header: bool = False
    header_lvl: int = 0
    header_space: bool = False
    inline_code: bool = False
    pending_backticks: int = 0
    at_line_start: bool = True

    BLUE: ClassVar[str] = "\033[34m"
    BOLD: ClassVar[str] = "\033[1m"
    ORANGE: ClassVar[str] = "\033[38;5;208m"
    RESET: ClassVar[str] = "\033[0m"

    def parse(self, chunk: str) -> None:
        """
        Process a text chunk, remove markers, and print with appropriate formatting.

        Args:
            chunk (str): A piece of streaming text to process.

        Returns:
            str: The processed chunk with markers removed.
        """
        text = chunk
        output = self._process_markers(text)
        if output:
            print(output, end="", flush=True)

    def _process_markers(self, text: str) -> str:
        """Extract markers and toggle states, returning text without markers."""
        output: list[str] = []

        if self.active:
            output.append(self.BLUE)
        elif self.inline_code:
            output.append(self.ORANGE)

        for char in text:
            if char == "\n":
                if self.header_lvl:
                    output.append("#" * self.header_lvl)
                    if self.header_space:
                        output.append(" ")
                    self.header_lvl = 0
                    self.header_space = False
                if self.header:
                    output.append(self.RESET)
                    self.header = False
                self.at_line_start = True
                output.append(char)
                continue

            if char == "`":
                self.pending_backticks += 1
                continue

            if (
                self.at_line_start
                and not self.active
                and not self.inline_code
                and char == "#"
            ):
                self.header_lvl += 1
                continue

            if (
                self.at_line_start
                and self.header_lvl
                and not self.active
                and not self.inline_code
                and char == " "
            ):
                self.header_space = True
                continue

            if self.pending_backticks:
                count = self.pending_backticks
                self.pending_backticks = 0

                if count == 3:
                    self.active = not self.active
                    if self.active:
                        output.append(self.BLUE)
                        self.inline_code = False
                    else:
                        output.append(self.RESET)
                elif count == 1 and not self.active:
                    self.inline_code = not self.inline_code
                    output.append(self.ORANGE if self.inline_code else self.RESET)

            if (
                self.header_lvl
                and self.at_line_start
                and not self.active
                and not self.inline_code
            ):
                # Future: different output for header lvls.
                lvl = self.header_lvl
                self.header_lvl = 0
                if self.header_space:
                    output.append(" ")
                self.header_space = False
                self.header = True
                output.append(self.BOLD)
                self.at_line_start = False

            output.append(char)
            self.at_line_start = False

        return "".join(output)

# Future: **bold** processing 