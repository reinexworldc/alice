from dataclasses import dataclass
from pathlib import Path
from typing import Any

from cli.commands import CommandsHelper
from cli.prompt import PromptSessionController
from cli.views.parser import ChunkParser
from core.agent import ChatAgent
from helpers.prompt.helper import PromptsHelper
from rich.console import Console


@dataclass
class SessionContext:
    agent: ChatAgent
    controller: PromptSessionController
    parser: ChunkParser
    commands_helper: CommandsHelper
    prompts_helper: PromptsHelper
    console: Console
    memory_file_created: bool = False
    memory_file: Path | None = None
    tools_by_index: dict[int, Any] | None = None
