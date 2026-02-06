from prompt_toolkit.formatted_text import HTML
from cli.prompt import PromptSessionController
from core.agent import ChatAgent
from providers.openai.provider import OpenAIProvider


def main():
    agent = ChatAgent(OpenAIProvider())
    controller = PromptSessionController()
    session = controller.session

    while True:
        try:
            text = session.prompt(
                bottom_toolbar=HTML(
                    "<hint>Enter: newline * Escape+Enter: send * Tab: indent</hint>"
                ),
                default="",
                validate_while_typing=False,
            )

            if not text.strip():
                continue
            if text.strip().lower() in ["exit", "quit", "q"]:
                break

            print()
            for chunk in agent.stream(text):
                print(chunk, end="", flush=True)
            print("\n")
        except KeyboardInterrupt:
            continue
        except EOFError:
            break


if __name__ == "__main__":
    main()
