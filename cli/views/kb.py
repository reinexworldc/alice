from prompt_toolkit.key_binding import KeyBindings


class KeyBindingSettings:
    def __init__(self):
        self.kb = KeyBindings()
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

        @self.kb.add("c-c")
        def _(event):
            """Ctrl+C exits the application"""
            event.app.exit()

    def get_bindings(self):
        return self.kb
