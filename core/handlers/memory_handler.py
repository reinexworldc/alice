from datetime import datetime, timezone
from pathlib import Path
from typing import Literal
import json

from cli.handlers.context import SessionContext
from utils import normalize

Role = Literal["Assistant", "User"]

class MemoryHandler:
    def __init__(self):
        self.memory_dir = Path(__file__).resolve().parents[2] / "memory"
    
    def create_memory_file(self, raw_name: str) -> Path:
        safe_name = normalize.normalize_filename(raw_name)
        file_path = self.memory_dir / f"{safe_name}.jsonl"

        try:
            self.memory_dir.mkdir(parents=True, exist_ok=True)
            file_path.touch(exist_ok=True)
            return file_path
        except OSError as exc:
            raise RuntimeError(f"Failed to create memory file at {file_path}") from exc
        
    def ensure_memory_file(self, context: SessionContext) -> None:
        if context.memory_file_created:
            return

        name = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        context.memory_file = self.create_memory_file(name)
        context.memory_file_created = True

    def write_memory(self, file: Path, text: str, role: Role) -> None:
        try:
            record = {
                "role": role,
                "text": text,
            }
            with file.open("a", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\n")
        except OSError as exc:
            raise RuntimeError(f"Failed to write memory file at {file}") from exc
        
    # TODO: Dry 
    def write_user_message(self, context: SessionContext, message: str) -> None:
        if context.memory_file is None:
            return

        self.write_memory(
            file=context.memory_file, text=message, role="User"
        )

    # TODO: Dry 
    def write_assistant_message(self, context: SessionContext, message: str) -> None:
        if context.memory_file is None:
            return

        self.write_memory(
            file=context.memory_file, text=message, role="Assistant"
        )
