import json
from pathlib import Path

class Config:
    def __init__(self):
        self.path = Path(__file__).parents[1] / "config.json"

    def _exists(self) -> bool:
        return self.path.exists()

    def create(self):
        self.path.touch()

    def write(self, text: str):
        if not self._exists():
            self.create()
        with open(self.path, "w", encoding="utf-8") as f:
            f.write(text)

    def read(self) -> str | None:
        if not self._exists():
            return None
        with open(self.path, "r", encoding="utf-8") as f:
            return f.read()
