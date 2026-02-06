from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML
from pydantic import BaseModel, Field, PrivateAttr
from ...views.kb import KeyBindingSettings


class PromptSessionController(BaseModel):
    kb_settings: KeyBindingSettings = Field(default_factory=KeyBindingSettings)

    _session: PromptSession = PrivateAttr()

    model_config = {"arbitrary_types_allowed": True}

    def model_post_init(self, __):
        """Create session after Pydantic initialization"""
        self._session = self._create_prompt_session()

    def _create_prompt_session(self):
        return PromptSession(
            message=HTML("<prompt> </prompt>"),
            multiline=True,
            key_bindings=self.kb_settings.get_bindings(),
            prompt_continuation=(lambda width, line_number, is_soft_wrap: "... "),
        )

    @property
    def session(self) -> PromptSession:
        return self._session
