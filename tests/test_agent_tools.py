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


class CreateFileTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_creates_file_and_parent_directories(self):
        path = self.root / "nested" / "example.txt"

        result = AgentTools.create_file(path=path, content="Hello, Alice!\n")

        self.assertEqual(path.read_text(encoding="utf-8"), "Hello, Alice!\n")
        self.assertEqual(result["written_characters"], 14)
        self.assertFalse(result["overwritten"])

    def test_refuses_to_overwrite_existing_file_by_default(self):
        path = self.root / "example.txt"
        path.write_text("original", encoding="utf-8")

        with self.assertRaises(FileExistsError):
            AgentTools.create_file(path=path, content="replacement")

        self.assertEqual(path.read_text(encoding="utf-8"), "original")

    def test_can_explicitly_overwrite_existing_file(self):
        path = self.root / "example.txt"
        path.write_text("original", encoding="utf-8")

        result = AgentTools.create_file(
            path=path,
            content="replacement",
            overwrite=True,
        )

        self.assertEqual(path.read_text(encoding="utf-8"), "replacement")
        self.assertTrue(result["overwritten"])


class MoveFileTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.source = self.root / "before.txt"
        self.source.write_text("source content", encoding="utf-8")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_renames_file(self):
        destination = self.root / "after.txt"

        result = AgentTools.move_file(self.source, destination)

        self.assertFalse(self.source.exists())
        self.assertEqual(destination.read_text(encoding="utf-8"), "source content")
        self.assertEqual(result["destination"], str(destination.resolve()))
        self.assertFalse(result["overwritten"])

    def test_moves_file_and_creates_destination_directories(self):
        destination = self.root / "nested" / "after.txt"

        AgentTools.move_file(self.source, destination)

        self.assertFalse(self.source.exists())
        self.assertEqual(destination.read_text(encoding="utf-8"), "source content")

    def test_refuses_to_overwrite_destination_by_default(self):
        destination = self.root / "after.txt"
        destination.write_text("destination content", encoding="utf-8")

        with self.assertRaises(FileExistsError):
            AgentTools.move_file(self.source, destination)

        self.assertEqual(self.source.read_text(encoding="utf-8"), "source content")
        self.assertEqual(
            destination.read_text(encoding="utf-8"),
            "destination content",
        )

    def test_can_explicitly_overwrite_destination(self):
        destination = self.root / "after.txt"
        destination.write_text("destination content", encoding="utf-8")

        result = AgentTools.move_file(
            self.source,
            destination,
            overwrite=True,
        )

        self.assertFalse(self.source.exists())
        self.assertEqual(destination.read_text(encoding="utf-8"), "source content")
        self.assertTrue(result["overwritten"])


if __name__ == "__main__":
    unittest.main()
