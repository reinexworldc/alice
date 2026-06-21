from dataclasses import dataclass
from typing import Any

from cli.prompt import PromptSessionController
from cli.views.parser import ChunkParser
from cli.views.renderer import TerminalRenderer
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
    renderer: TerminalRenderer
    tools_by_index: dict[int, Any] | None = None
