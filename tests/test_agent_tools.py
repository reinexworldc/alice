import tempfile
import unittest
from pathlib import Path

from core.agent import AgentTools


class ApplyPatchTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.path = Path(self.temp_dir.name) / "example.txt"
        self.path.write_text("one\ntwo\nthree\n", encoding="utf-8")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_supports_all_edit_operations_against_original_lines(self):
        result = AgentTools.apply_patch(
            path=self.path,
            new_lines=[
                {"operation": "insert_before", "line": 1, "content": "zero\n"},
                {"operation": "replace", "line": 2, "content": "TWO\n"},
                {"operation": "insert_after", "line": 2, "content": "two-and-half\n"},
                {"operation": "delete", "line": 3},
            ],
        )

        self.assertEqual(
            self.path.read_text(encoding="utf-8"),
            "zero\none\nTWO\ntwo-and-half\n",
        )
        self.assertEqual(result["applied_edits"], 4)

    def test_legacy_items_still_replace_lines(self):
        AgentTools.apply_patch(
            path=self.path,
            new_lines=[{"line": 2, "content": "changed\n"}],
        )

        self.assertEqual(
            self.path.read_text(encoding="utf-8"),
            "one\nchanged\nthree\n",
        )

    def test_insert_before_line_after_end_appends(self):
        AgentTools.apply_patch(
            path=self.path,
            new_lines=[
                {"operation": "insert_before", "line": 4, "content": "four\n"}
            ],
        )

        self.assertEqual(
            self.path.read_text(encoding="utf-8"),
            "one\ntwo\nthree\nfour\n",
        )

    def test_invalid_edit_does_not_modify_file(self):
        original = self.path.read_text(encoding="utf-8")

        with self.assertRaises(IndexError):
            AgentTools.apply_patch(
                path=self.path,
                new_lines=[{"operation": "delete", "line": 10}],
            )

        self.assertEqual(self.path.read_text(encoding="utf-8"), original)


if __name__ == "__main__":
    unittest.main()
