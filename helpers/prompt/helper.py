from pathlib import Path
from .errors import PromptNotFoundError


class PromptsHelper:
    def __init__(self):
        self.PROMPTS_DIR = Path(__file__).resolve().parents[2] / "prompts"

    def load_prompt(self, path: Path) -> str:
        return path.read_text(encoding="utf-8")

    def system_prompt(self) -> str:
        return self.load_prompt(self.PROMPTS_DIR / "system_prompt.md")

    def workflow_prompt(self, name: str) -> str:
        workflow = self.PROMPTS_DIR / "workflows" / f"{name}.md"

        if not workflow.exists():
            raise PromptNotFoundError(f"Workflow prompt not found: {workflow}")

        return self.load_prompt(workflow)

    def prompt_path(self, name: str) -> Path:
        return Path(self.PROMPTS_DIR / name).resolve()
