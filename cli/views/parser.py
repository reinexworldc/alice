from pydantic import BaseModel


class ChunkParser(BaseModel):
    """
    A parser that toggles colored output when detecting code block markers (```)
    and handles bold text markers (**), removing the markers from output.

    This class processes streaming text chunks and prints them in blue when inside
    a code block (between ``` markers) and in bold when between ** markers. The
    markers themselves are removed from the output.

    Attributes:
        active (bool): Whether we're currently inside a code block. Defaults to False.
        bold (bool): Whether we're currently in bold text. Defaults to False.
    """

    active: bool = False
    bold: bool = False
    buffer: str = ""

    def parse(self, chunk: str) -> str:
        """
        Process a text chunk, remove markers, and print it with appropriate formatting.

        This method:
        1. Detects ``` and ** markers in the input
        2. Toggles active/bold state when markers found and removes them from output
        3. Prints chunk in blue if inside code block, bold if between **, or normal

        Args:
            chunk (str): A piece of streaming text to process. Can be a single
                        character, word, or larger text fragment.

        Returns:
            str: The processed chunk with markers removed.

        ANSI codes used:
            - \033[34m : Blue text (code blocks)
            - \033[1m  : Bold text
            - \033[0m  : Reset formatting

        Example:
            >>> parser = ChunkParser()
            >>> parser.parse("Hello ")          # Normal: "Hello "
            >>> parser.parse("```")             # Marker removed, toggles code block
            >>> parser.parse("code")            # Blue: "code"
            >>> parser.parse("```")             # Marker removed, toggles off
            >>> parser.parse("**")              # Marker removed, toggles bold
            >>> parser.parse("bold")            # Bold: "bold"
            >>> parser.parse("**")              # Marker removed, toggles bold off
        """

        text = self.buffer + chunk
        self.buffer = ""

        out = []
        i = 0
        n = len(text)

        while i < n:
            if text.startswith("```", i):
                self.active = not self.active
                i += 3
                continue

            if text.startswith("**", i):
                self.bold = not self.bold
                i += 2
                continue

            out.append(text[i])
            i += 1

        if out:
            s = "".join(out)
        else:
            s = ""

        tail = ""
        j = len(s)
        while j > 0 and s[j - 1] == "`" and len(tail) < 2:
            tail = "`" + tail
            j -= 1

        if tail == "" and j > 0 and s[j - 1] == "*":
            tail = "*"
            j -= 1

        if tail:
            self.buffer = tail
            s = s[:j]

        if s:
            if self.active:
                print(f"\033[34m{s}\033[0m", end="", flush=True)
            elif self.bold:
                print(f"\033[1m{s}\033[0m", end="", flush=True)
            else:
                print(s, end="", flush=True)

        return s
