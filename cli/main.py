from cli.prompt import PromptSessionController
from core.agent import ChatAgent, AgentTools
from providers.openai.provider import OpenAIProvider
from rich.console import Console
from .views.parser import ChunkParser
from helpers.prompt.helper import PromptsHelper
from cli.commands import CommandsHelper
from core.memory import MemoryHelper
from datetime import datetime, timezone
import json
from pathlib import Path
from schemas import ToolCall, Chunk


def main():
    agent = ChatAgent(
        provider=OpenAIProvider(),
    )
    controller = PromptSessionController()
    parser = ChunkParser()
    commands_helper = CommandsHelper()
    prompts_helper = PromptsHelper()
    console = Console()
    session = controller.session

    agent.add_system_prompt(prompts_helper.system_prompt())

    console.clear()

    memory_file_created = False

    while True:
        try:
            message: str = session.prompt(
                "> ",
                default="",
                validate_while_typing=False,
            )

            if not message.strip():
                continue

            if message.strip().lower() in ["exit", "quit", "q"]:
                break

            if commands_helper.is_command(message):
                commands_helper.handle_command(agent=agent, text=message)
                continue

            if not memory_file_created:
                # Upgrade after >> Session id & Prompt Hash
                name = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
                file = MemoryHelper.create_memory_file(name)
                memory_file_created = True

            if memory_file_created and message:
                # Write user message to memory file
                MemoryHelper.write_memory(file=file, text=message, role="User")

                # Storage for reconstructing complete assistant response
                chunks = []  # Collects text content pieces from streaming chunks
                tools_by_id = {}  # Accumulates tool call arguments by tool ID

                # Load available tools for the agent
                with open(
                    Path(__file__).resolve().parents[1] / "core" / "tools_content.json"
                ) as f:
                    tools = json.load(f)

                # === STREAMING CHUNK PROCESSING ===
                # Raw output from LLM comes as a stream of chunks
                # Each chunk can contain:
                #   - delta content (text being generated)
                #   - tool_calls (function calls with incremental arguments)
                #   - finish_reason (when stream ends)
                chunk: Chunk
                for chunk in agent.llm_output(message, tools=tools):
                    if chunk.get("content"):
                        # Display chunk to user in real-time
                        parser.parse(chunk=chunk["content"])
                        # === TEXT CONTENT EXTRACTION ===
                        # chunk["content"] contains incremental text tokens
                        # Example: {"content": "The weather", ...}
                        #          {"content": " is sunny", ...}
                        #          {"content": " today.", ...}
                        chunks.append(chunk["content"])

                    # === TOOL CALL RECONSTRUCTION ===
                    # Tool calls arrive incrementally across multiple chunks
                    # Must reassemble complete JSON arguments from fragments
                    # 
                    # Example raw chunk sequence:
                    # Chunk 1: {
                    #   "tool_calls": [{
                    #     "id": "call_abc123",
                    #     "type": "function",
                    #     "function": {"name": "get_directory", "arguments": "{\"path"}
                    #   }]
                    # }
                    # Chunk 2: {
                    #   "tool_calls": [{
                    #     "id": "call_abc123",
                    #     "function": {"arguments": "\": \"/home\""}
                    #   }]
                    # }
                    # Chunk 3: {
                    #   "tool_calls": [{
                    #     "id": "call_abc123",
                    #     "function": {"arguments": "}"}
                    #   }]
                    # }
                    if chunk.get("tool_calls"):
                        tool_call: ToolCall
                        for tool_call in chunk["tool_calls"]:
                            tool_id = tool_call.get("id")
                            if tool_id:
                                # Initialize tool call structure on first encounter
                                if tool_id not in tools_by_id:
                                    tools_by_id[tool_id] = {
                                        "id": tool_id,
                                        "type": tool_call.get("type"),  # Usually "function"
                                        "function": {
                                            "name": tool_call.get("function", {}).get(
                                                "name", ""
                                            ),
                                            "arguments": "",  # Will accumulate JSON string
                                        },
                                    }

                                # Append incremental argument fragment
                                # Builds complete JSON string: "" -> "{\"path" -> "{\"path\": \"/home\"" -> "{\"path\": \"/home\"}"
                                args_chunk = tool_call.get("function", {}).get(
                                    "arguments", ""
                                )
                                tools_by_id[tool_id]["function"]["arguments"] += (
                                    args_chunk
                                )

                # === TOOL EXECUTION ===
                # After streaming completes, execute all accumulated tool calls
                # The arguments string is now complete and can be parsed as JSON
                for tool_id, tool_call in tools_by_id.items():
                    tool_name = tool_call["function"]["name"]
                    # Parse complete JSON arguments string into Python dict
                    # Example: "{\"path\": \"/home\"}" -> {"path": "/home"}
                    args = json.loads(tool_call["function"]["arguments"])

                    # Execute the appropriate tool function
                    if tool_name == "get_directory":
                        result = AgentTools.get_directory(**args)
                        # Add tool result to conversation context
                        # LLM will receive this in next turn to formulate response
                        agent.messages.append(
                            {
                                "role": "tool",
                                "tool_name": tool_name,
                                "content": json.dumps(result),
                            }
                        )

                # === FINAL RESPONSE ASSEMBLY ===
                # Combine all text chunks into complete assistant message
                # Example: ["The weather", " is sunny", " today."] -> "The weather is sunny today."
                llm_message = " ".join(chunks)

                # Write complete assistant response to memory
                MemoryHelper.write_memory(file=file, text=llm_message, role="Assistant")

            print("")

        except KeyboardInterrupt:
            continue
        except EOFError:
            break


if __name__ == "__main__":
    main()