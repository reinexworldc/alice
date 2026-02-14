import json
from pathlib import Path
from typing import Any

from core.agent import AgentTools, ChatAgent
from schemas import ToolCall


class ToolsHandler:
    @staticmethod
    def _append_tool_message(agent: ChatAgent, tool_call_id: str, result: Any) -> None:
        content = json.dumps(result) if isinstance(result, dict) else str(result)
        agent.messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call_id,
                "content": content,
            }
        )

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
    def execute_tool_calls(
        # Future: Return "welcome" message if tool call it's first call.
        agent: ChatAgent,
        tools_by_index: dict[int, dict[str, Any]],
    ) -> None:
        # Mb separate it into uniq func.
        agent.messages.append(
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

        tool_handlers = {
            "get_directory": AgentTools.get_directory,
            "get_lines": AgentTools.get_lines,
            "review_code": AgentTools.review_code,
        }

        for tool_call in tools_by_index.values():
            tool_name = tool_call["function"]["name"]
            args_string = tool_call["function"]["arguments"]

            if not args_string or not args_string.strip():
                continue

            try:
                args = json.loads(args_string)
            except json.JSONDecodeError as e:
                print(f"Warning: Invalid JSON for tool {tool_name}: {args_string}")
                print(f"Error: {e}")
                continue

            handler = tool_handlers.get(tool_name)
            if handler is None:
                ToolsHandler._append_tool_message(
                    agent,
                    tool_call["id"],
                    {"error": f"Unknown tool: {tool_name}"},
                )
                continue

            try:
                result = handler(**args)
            except Exception as e:
                result = {"error": str(e)}

            ToolsHandler._append_tool_message(agent, tool_call["id"], result)
