from dataclasses import dataclass
from pathlib import Path
from typing import Any

from cli.prompt import PromptSessionController
from cli.views.parser import ChunkParser
from core.agent import ChatAgent
from core.helpers.prompt.helper import PromptsHelper
from rich.console import Console


@dataclass
class SessionContext:
    agent: ChatAgent
    controller: PromptSessionController
    parser: ChunkParser
    prompts_helper: PromptsHelper
    console: Console
    tools_by_index: dict[int, Any] | None = None
