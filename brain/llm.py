from ollama import chat

from brain.prompts import SYSTEM_PROMPT
from brain.history import conversation_history


def ask_mev10(message: str):

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        }
    ]

    messages.extend(conversation_history[-10:])

    messages.append(
        {
            "role": "user",
            "content": message,
        }
    )

    stream = chat(
        model="qwen3:8b",
        messages=messages,
        stream=True,
        think=False,
    )

    print("\nMEV10: ", end="", flush=True)

    reply = ""

    for chunk in stream:
        text = chunk.message.content
        print(text, end="", flush=True)
        reply += text

    print()

    conversation_history.append(
        {
            "role": "user",
            "content": message,
        }
    )

    conversation_history.append(
        {
            "role": "assistant",
            "content": reply,
        }
    )

    return reply