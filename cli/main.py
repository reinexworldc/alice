from providers.openai.provider import OpenAIProvider 
from openai import OpenAI
from prompt_toolkit import PromptSession
from prompt_toolkit import print_formatted_text as print
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.formatted_text import HTML

from .kb import KeyBindingSettings

def main():
    kb_settings = KeyBindingSettings()

    session = PromptSession(
        message=HTML("<prompt> </prompt>"),
        multiline=True,
        key_bindings=kb_settings.get_bindings(),
        prompt_continuation=(
            lambda width, line_number, is_soft_wrap:
            " " * width     
        )
    )

    while True:
        try:
            text = session.prompt(
                bottom_toolbar=HTML(
                    "<hint>Enter: newline * Escape+Enter: send * Tab: indent</hint>"     
                ),
                default="",
                validate_while_typing=False
            )

            if not text.strip():
                continue
            if text.strip().lower() in ['exit', 'quit', 'q']:
                break

            if text:
                openai = OpenAIProvider(client=OpenAI())
                
                response = openai.model_call(
                    input_content=text, 
                    model="gpt-5.2",
                    stream=True
                )

                print("AI: ", end='', flush=True)
                for chunk in response:
                    if chunk.type == 'response.output_text.delta':
                        print(chunk.delta, end='', flush=True)
                print()

        except KeyboardInterrupt:
            continue
        except EOFError:
            break

if __name__ == '__main__':
    main()