import json
from pathlib import Path
from typing import Any

from core.agent import AgentTools, ChatAgent
from core.schemas import ToolCall
from cli.views.renderer import TerminalRenderer
from .memory_handler import MemoryHandler


class ToolsHandler:
    def __init__(
        self,
        agent: ChatAgent,
        memory_handler: MemoryHandler,
        renderer: TerminalRenderer,
    ):
        self.agent = agent
        self.tool_handlers = {
            "get_directory": AgentTools.get_directory,
            "get_lines": AgentTools.get_lines,
            "review_code": AgentTools.review_code,
            "apply_patch": AgentTools.apply_patch,
        }
        self.memory_handler = memory_handler
        self.renderer = renderer

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
        
    def _append_tool_message(self, tool_call_id: str, result: Any) -> None:
        content = json.dumps(result) if isinstance(result, dict) else str(result)
        self.agent.messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call_id,
                "content": content,
            }
        )

    # TODO: Return "welcome" message if tool call it's first call.
    def execute_tool_calls(
        self,
        tools_by_index: dict[int, dict[str, Any]],
    ) -> None:
        # TODO: separate it into uniq func.
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

            # TODO: Middleware/Context approach for memory saving.
            memory_message = f"Tool Call: {tool_name}: {args_string}"
            self.memory_handler.write_message(memory_message, "Assistant")

            if not args_string or not args_string.strip():
                result = {"error": f"{tool_name}: missing arguments"}
                self._append_tool_message(tool_call["id"], result)
                self.renderer.error(f"{tool_name}: missing arguments")
                continue

            try:
                args = json.loads(args_string)
            except json.JSONDecodeError as e:
                result = {"error": f"Invalid JSON arguments: {e}"}
                self._append_tool_message(tool_call["id"], result)
                self.renderer.error(f"{tool_name}: invalid arguments ({e})")
                continue

            if not isinstance(args, dict):
                result = {"error": "Tool arguments must be a JSON object"}
                self._append_tool_message(tool_call["id"], result)
                self.renderer.error(f"{tool_name}: arguments must be an object")
                continue

            self.renderer.action(tool_name, args.get("path", ""))

            handler = self.tool_handlers.get(tool_name)
            if handler is None:
                self._append_tool_message(
                    tool_call["id"],
                    {"error": f"Unknown tool: {tool_name}"},
                )
                self.renderer.error(f"Unknown tool: {tool_name}")
                continue

            try:
                result = handler(**args)
            except Exception as e:
                result = {"error": str(e)}

            self._append_tool_message(tool_call["id"], result)
            if isinstance(result, dict) and "error" in result:
                self.renderer.error(str(result["error"]))
            else:
                self.renderer.success()
