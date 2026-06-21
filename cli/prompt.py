from getpass import getuser

from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML, FormattedText
from prompt_toolkit.styles import Style
from cli.views.kb import KeyBindingSettings


class PromptSessionController:
    def __init__(self):
        self.kb_settings = KeyBindingSettings()
        self._session = self._create_prompt_session()

    def _create_prompt_session(self) -> PromptSession:
        style = Style.from_dict(
            {
                "user": "bold ansicyan",
                "bottom-toolbar": "bg:#222222 #aaaaaa",
            }
        )
        return PromptSession(
            message=FormattedText([("class:user", f"{getuser()} › ")]),
            multiline=True,
            key_bindings=self.kb_settings.get_bindings(),
            prompt_continuation=(lambda width, line_number, is_soft_wrap: ""),
            bottom_toolbar=HTML(" Enter: send · Esc+Enter: new line "),
            style=style,
        )

    @property
    def session(self) -> PromptSession:
        return self._session
