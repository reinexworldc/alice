from prompt_toolkit.key_binding import KeyBindings
from pydantic import BaseModel, Field

# Key Bindings

class KeyBindingSettings(BaseModel):
    kb: KeyBindings = Field(default_factory=KeyBindings)
    
    model_config = {
        'arbitrary_types_allowed': True     
    }
    
    def model_post_init(self, __):
        self._setup_bindings()

    def _setup_bindings(self):
        @self.kb.add("enter")
        def _(event):
            """
            Enter inserts a newline (multiline compose mode)
            """
            event.current_buffer.insert_text("\n")

        @self.kb.add("escape", "enter")
        def _(event):
            """Escape + Enter sumbits the input"""
            event.current_buffer.validate_and_handle()

        @self.kb.add("tab")
        def _(event):
            """Tab inserts indentation"""
            event.current_buffer.insert_text("    ") 

    def get_bindings(self):
        return self.kb
