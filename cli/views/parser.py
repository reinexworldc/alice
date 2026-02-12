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
    inline_code: bool = False
    buffer: str = ""
    at_line_start: bool = True
    
    BLUE: ClassVar[str] = "\033[34m"
    BOLD: ClassVar[str] = "\033[1m"
    HEADER: ClassVar[str] = f"\033[1m\033[34m" 
    CYAN: ClassVar[str] = "\033[36m"
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

        self._print_formatted(output)

    def _process_markers(self, text: str) -> str:
        """Extract markers and toggle states, returning text without markers."""
        out = []
        i = 0

        str = "```Hello!``` `How` *are u?*"
        
        # Need Fix.
        # Try to accumulate each spec. sybmol in a buffer.
        # Turn off/Turn on in real time 
        while i < len(text):
            # Check for code block marker (```) - must check before single backtick
            if text[i:i+3] == "```":
                self.active = not self.active
                i += 3
            # Future: Check for single backtick (`)
            elif text[i] == "`":
                self.inline_code = not self.inline_code
                i += 1
            # Check for bold marker (**)
            elif text[i:i+2] == "**":
                self.bold = not self.bold
                i += 2
            elif text[i] == "#" and self.at_line_start:
                # Count consecutive # symbols
                header_level = 0
                while i < len(text) and text[i] == "#" and header_level < 6:
                    header_level += 1
                    i += 1
                # Skip any spaces after the # symbols
                while i < len(text) and text[i] == " ":
                    i += 1
            # Skip leading whitespace at line start (before potential #)
            elif text[i] == " " and self.at_line_start:
                i += 1
                
                self.at_line_start = False
            else:
                char = text[i]
                out.append(char)
                
                if char == "\n":
                    self.header = False
                    self.at_line_start = True
                else:
                    self.at_line_start = False
                
                i += 1
        
        return "".join(out)
    
    def _print_formatted(self, text: str) -> None:
        """Print text with appropriate ANSI formatting based on current state."""
        if self.header:
            formatted = f"{self.HEADER}{text}{self.RESET}"
        elif self.active:
            formatted = f"{self.BLUE}{text}{self.RESET}"
        elif self.inline_code:
            formatted = f"{self.CYAN}{text}{self.RESET}"
        elif self.bold:
            formatted = f"{self.BOLD}{text}{self.RESET}"
        else:
            formatted = text

        print(formatted, end="", flush=True)