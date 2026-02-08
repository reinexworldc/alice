from pathlib import Path


class PromptsHelper:
    def __init__(self):
        self.PROMPTS_DIR = Path(__file__).resolve().parents[1] / "prompts"

    def load_prompt(self, path: Path) -> str:
        return path.read_text(encoding="utf-8")

    def system_prompt(self, path: Path) -> str:
        return self.load_prompt(self.PROMPTS_DIR / "system.md")
    
    def workflow_prompt(self, name: str) -> str:
        return self.load_prompt(self.PROMPTS_DIR / f"{name}.md")