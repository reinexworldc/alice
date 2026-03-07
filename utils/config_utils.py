import json
from pathlib import Path

class Config:
    def __init__(self):
        self.path = Path(__file__).parents[1] / "config.json"

    def exists(self) -> bool:
        return self.path.exists()

    def create(self):
        self.path.touch()

    def write(self, data: dict):
        if not self.exists():
            self.create()
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)        

    def read(self) -> dict | None:
        if not self.exists():
            return None
        with open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)                 