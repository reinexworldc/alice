from pathlib import Path
from core.utils.normalize import normalize_filename
from typing import Literal
import json

Role = Literal["Assistant", "User"]


class MemoryHelper:
    @staticmethod
    def create_memory_file(raw_name: str) -> Path:
        memory_dir = Path(__file__).resolve().parents[1] / "memory"
        safe_name = normalize_filename(raw_name)
        file_path = memory_dir / f"{safe_name}.jsonl"

        try:
            memory_dir.mkdir(parents=True, exist_ok=True)
            file_path.touch(exist_ok=True)
            return file_path
        except OSError as exc:
            raise RuntimeError(f"Failed to create memory file at {file_path}") from exc

    @staticmethod
    def write_memory(file: Path, text: str, role: Role) -> None:
        try:
            record = {
                "role": role,
                "text": text,
            }
            with file.open("a", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\n")
        except OSError as exc:
            raise RuntimeError(f"Failed to write memory file at {file}") from exc
