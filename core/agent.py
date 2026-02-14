from providers.base import LLMProvider
from pathlib import Path
from itertools import islice

# Future: Separate logic. 
class ChatAgent:
    """
    A conversational agent that manages chat history and interfaces with LLM providers.
    
    This class maintains a conversation context and handles streaming responses from
    language models. It supports system prompts and tool usage.
    
    Attributes:
        provider (LLMProvider): The LLM provider instance (e.g., OpenAI, Anthropic)
        messages (list): Conversation history stored as a list of message dictionaries
    """
    
    def __init__(
        self, 
        provider: LLMProvider, 
        system_prompt: str | None = None
    ):
        """
        Initialize the ChatAgent with an LLM provider and optional system prompt.
        
        Args:
            provider: An instance of LLMProvider that handles the actual LLM API calls
            system_prompt: Optional initial system prompt to set the agent's behavior
        """
        self.provider = provider
        self.messages = []
        if system_prompt:
            self.messages.append({
                "role": "system",
                "content": system_prompt,
            })
            
    def add_system_prompt(self, text: str):
        """
        Add an additional system prompt to the conversation history.
        
        Useful for dynamically updating the agent's instructions mid-conversation.
        
        Args:
            text: The system prompt text to add
        """
        self.messages.append({
            "role": "system",
            "content": text,    
        })
        
    def llm_output(self, user_message: str, tools: list[dict]):
        """
        Generate a streaming LLM response to a user message.
        
        This method adds the user message to history, streams the response from the
        provider, and appends the complete assistant response to the message history.
        
        Args:
            user_message: The user's input text
            tools: List of tool definitions available to the LLM
            
        Returns:
            Generator that yields response chunks with structure: {"content": str, ...}
            Each chunk contains partial response content that can be displayed in real-time.
        """
        # Add user message to conversation history
        self.messages.append({
            "role": "user",
            "content": user_message,     
        })
        
        def stream():
            """
            Internal generator that handles streaming and message history updates.
            
            Yields response chunks while collecting them to build the full assistant message.
            """
            assistant_chunks = []
            for chunk in self.provider.llm_stream(messages=self.messages, tools=tools):
                if chunk["content"]:
                    assistant_chunks.append(chunk["content"])
                yield chunk
            
            # Add complete assistant response to history
            self.messages.append({
                "role": "assistant",
                "content": "".join(assistant_chunks),
                "tools": tools   
            })
        
        return stream()


# Future: Separate to uniq file.
class AgentTools:
    """
    Static utility class providing file system and other tool functions for agents.
    
    This class contains methods that can be exposed as tools to LLMs, allowing them
    to interact with the file system and perform other operations.
    """

    @staticmethod
    def get_lines(path: str | Path) -> int:
        path = Path(path).expanduser().resolve()
        if not path.is_file():
            raise IsADirectoryError(f"Path is not a file: {path}")

        with open(path, "rb") as f:
            line_count: int = sum(1 for _ in f)
        return line_count
    
    @staticmethod
    def review_code(path: Path, start: int, end: int) -> str:
        path = Path(path).expanduser().resolve()
        if not path.is_file():
            raise IsADirectoryError(f"Path is not a file: {path}") 
        
        with open(path, "r", encoding="utf-8") as f:
            lines = list(islice(f, start - 1, end))

        return lines 

    @staticmethod
    def apply_patch():
        pass
    
    @staticmethod
    def get_directory(path: str | Path) -> dict:
        """
        List contents of a directory, separating files and subdirectories.
        
        This tool allows an agent to explore the file system structure by reading
        directory contents. Useful for understanding project layout or finding files.
        
        Args:
            path: Path to the directory (string or Path object). Supports ~ for home directory.
            
        Returns:
            dict: Directory information with structure:
                {
                    "path": str,              # Resolved absolute path
                    "directories": list[str], # Sorted list of subdirectory names
                    "files": list[str]        # Sorted list of file names
                }
                
        Raises:
            FileNotFoundError: If the specified path doesn't exist
            NotADirectoryError: If the path exists but isn't a directory
            
        Example:
            >>> AgentTools.get_directory("~/projects")
            {
                "path": "/home/user/projects",
                "directories": ["project1", "project2"],
                "files": ["README.md", "setup.py"]
            }
        """
        # Expand user home directory and resolve to absolute path
        path = Path(path).expanduser().resolve()
        
        if not path.exists():
            raise FileNotFoundError(f"Path does not exist: {path}")
        
        if not path.is_dir():
            raise NotADirectoryError(f"Not a directory: {path}")
        
        # Separate directories and files
        directories = []
        files = []
        for item in path.iterdir():
            if item.is_dir():
                directories.append(item.name)
            else:
                files.append(item.name)
        
        return {
            "path": str(path),
            "directories": sorted(directories),
            "files": sorted(files)     
        }
    