from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML
from cli.views.kb import KeyBindingSettings


class PromptSessionController:
    def __init__(self):
        self.kb_settings = KeyBindingSettings()
        self._session = self._create_prompt_session()

    def _create_prompt_session(self) -> PromptSession:
        return PromptSession(
            message=HTML("<prompt> </prompt>"),
            multiline=True,
            key_bindings=self.kb_settings.get_bindings(),
            prompt_continuation=(lambda width, line_number, is_soft_wrap: ""),
        )

    @property
    def session(self) -> PromptSession:
        return self._session
