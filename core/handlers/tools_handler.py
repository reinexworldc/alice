import json
from pathlib import Path
from typing import Any

from core.agent import AgentTools, ChatAgent
from core.schemas import ToolCall
from .memory_handler import MemoryHandler 


class ToolsHandler:
    def __init__(self, agent: ChatAgent):
        self.agent = agent
        self.tool_handlers = {
            "get_directory": AgentTools.get_directory,
            "get_lines": AgentTools.get_lines,
            "review_code": AgentTools.review_code,
            "apply_patch": AgentTools.apply_patch,
        }
        self.memory_handler = MemoryHandler()

    # TODO: Separate static methods to utils ?
    @staticmethod
    def load_tools() -> list[dict[str, Any]]:
        tools_path = Path(__file__).resolve().parents[2] / "core" / "tools_content.json"
        with open(tools_path) as f:
            tools = json.load(f)
        return tools

    @staticmethod
    def collect_tool_calls(chunks: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
        tools_by_index: dict[int, dict[str, Any]] = {}

        for chunk in chunks:
            if not chunk.get("tool_calls"):
                continue

            tool_call: ToolCall
            for tool_call in chunk["tool_calls"]:
                tool_index = getattr(tool_call, "index", None)
                if tool_index is None:
                    continue

                function_obj = getattr(tool_call, "function", None)
                if tool_index not in tools_by_index:
                    tool_id = getattr(tool_call, "id", "None")
                    function_name = (
                        getattr(function_obj, "name", "") if function_obj else ""
                    )

                    tools_by_index[tool_index] = {
                        "id": tool_id,
                        "index": tool_index,
                        "type": getattr(tool_call, "type", "function"),
                        "function": {
                            "name": function_name,
                            "arguments": "",
                        },
                    }

                if function_obj:
                    args_chunk = getattr(function_obj, "arguments", "")
                    if args_chunk:
                        tools_by_index[tool_index]["function"]["arguments"] += (
                            args_chunk
                        )

        return tools_by_index
        
    @staticmethod
    def narrate(args_string: str, tool_name: str ):
        name = Path(json.loads(args_string).get("path", "")).name
        if tool_name == "get_directory":
            print(f"Looking at dir >> {name}")

        if tool_name == "get_lines":
            print(f"Checking lines count in >> {name}")

        if tool_name == "review_code":
            print(f"Looking at file >> {name}")

        # TODO: Diff log.
        if tool_name == "apply_patch":
            print(f"Apply patch to file >> {name}")

    def _append_tool_message(self, tool_call_id: str, result: Any) -> None:
        content = json.dumps(result) if isinstance(result, dict) else str(result)
        self.agent.messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call_id,
                "content": content,
            }
        )

    # Future: Return "welcome" message if tool call it's first call.
    def execute_tool_calls(
        self,
        tools_by_index: dict[int, dict[str, Any]],
    ) -> None:
        # Mb separate it into uniq func.
        self.agent.messages.append(
            {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {
                        "id": tool_call["id"],
                        "type": tool_call["type"],
                        "function": {
                            "name": tool_call["function"]["name"],
                            "arguments": tool_call["function"]["arguments"],
                        },
                    }
                    for tool_call in tools_by_index.values()
                ],
            }
        )

        for tool_call in tools_by_index.values():
            tool_name = tool_call["function"]["name"]
            args_string = tool_call["function"]["arguments"]

            ToolsHandler.narrate(args_string=args_string, tool_name=tool_name)

            if not args_string or not args_string.strip():
                continue

            try:
                args = json.loads(args_string)
            except json.JSONDecodeError as e:
                print(f"Warning: Invalid JSON for tool {tool_name}: {args_string}")
                print(f"Error: {e}")
                continue

            handler = self.tool_handlers.get(tool_name)
            if handler is None:
                self._append_tool_message(
                    tool_call["id"],
                    {"error": f"Unknown tool: {tool_name}"},
                )
                continue

            try:
                result = handler(**args)
            except Exception as e:
                result = {"error": str(e)}

            self._append_tool_message(tool_call["id"], result)
