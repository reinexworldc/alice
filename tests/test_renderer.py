import io
import unittest

from rich.console import Console

from cli.views.renderer import TerminalRenderer


class TerminalRendererTests(unittest.TestCase):
    def setUp(self):
        self.output = io.StringIO()
        console = Console(
            file=self.output,
            force_terminal=False,
            color_system=None,
            width=120,
        )
        self.renderer = TerminalRenderer(console)

    def test_streams_assistant_with_continuation_indentation(self):
        self.renderer.assistant_chunk("Первая строка\n")
        self.renderer.assistant_chunk("Вторая строка")
        self.renderer.assistant_end()

        self.assertEqual(
            self.output.getvalue(),
            "alice  Первая строка\n       Вторая строка\n",
        )

    def test_renders_tool_statuses(self):
        self.renderer.action("review_code", "/project/core/agent.py")
        self.renderer.success("review_code завершён")
        self.renderer.error("Не удалось прочитать файл")

        self.assertEqual(
            self.output.getvalue(),
            "       … Читаю файл agent.py\n"
            "       ✓ review_code завершён\n"
            "       ✗ Не удалось прочитать файл\n",
        )


if __name__ == "__main__":
    unittest.main()
