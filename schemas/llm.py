from typing import TypedDict, List, Optional

class FunctionCall(TypedDict):
    name: str
    arguments: str

class ToolCall(TypedDict):
    id: str
    type: str
    function: FunctionCall

class Chunk(TypedDict):
    content: Optional[str]
    tool_calls: Optional[List[ToolCall]]