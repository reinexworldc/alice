from core.prompts.helper import PromptsHelper
from core.agent import ChatAgent
from core.prompts.errors import PromptNotFoundError

class CommandsHelper:
    def __init__(self):
        self.prompts_helper = PromptsHelper()

    def is_command(self, text: str) -> bool:
        return text.startswith("/") 

    def handle_command(self, agent: ChatAgent, text: str) -> None:
        parts: list = text[1:].strip().split()
        command: str = parts[0]
        args: list[str] = parts[1:]

        if command == "workflow":
            if not args:
                print("Usage: /workflow <name>")
                return

            workflow = args[0]

            try:
                agent.add_system_prompt(
                    self.prompts_helper.workflow_prompt(workflow)
                )
                print(f"Switched workflow to '{workflow}'")

            except PromptNotFoundError as e:
                print(f"Error: {e}")

            return
        
    def clear():
        pass
    
    def reset_workflow():
        pass
