from pathlib import Path

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_ollama import ChatOllama


MODEL_NAME = "llama3.1:latest"
PROMPT_FILE = Path(__file__).parent / "prompts" / "board_adviser.txt"


def load_system_prompt() -> str:
    """Load the Board Adviser instructions from disk."""
    try:
        prompt = PROMPT_FILE.read_text(encoding="utf-8").strip()
    except FileNotFoundError as exc:
        raise SystemExit(
            f"System prompt not found: {PROMPT_FILE}\n"
            "Keep the prompts folder beside main.py."
        ) from exc

    if not prompt:
        raise SystemExit(f"System prompt is empty: {PROMPT_FILE}")

    return prompt


def main() -> None:
    system_prompt = load_system_prompt()

    llm = ChatOllama(
        model=MODEL_NAME,
        temperature=0.2,
    )

    messages = [SystemMessage(content=system_prompt)]

    print("\nJasonAI Board Adviser is ready.")
    print("Type 'exit' or 'quit' to close.\n")

    while True:
        try:
            question = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nJasonAI closed.\n")
            break

        if question.lower() in {"exit", "quit"}:
            print("\nJasonAI closed.\n")
            break

        if not question:
            continue

        messages.append(HumanMessage(content=question))

        try:
            response = llm.invoke(messages)
        except Exception as exc:
            messages.pop()
            print(f"\nJasonAI error: {exc}\n")
            continue

        messages.append(AIMessage(content=response.content))
        print(f"\nJasonAI:\n{response.content}\n")


if __name__ == "__main__":
    main()
