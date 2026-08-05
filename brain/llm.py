from ollama import chat

from brain.prompts import SYSTEM_PROMPT
from brain.history import conversation_history


def ask_mev10(message: str) -> str:

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        }
    ]

    messages.extend(conversation_history)

    messages.append(
        {
            "role": "user",
            "content": message,
        }
    )

    response = chat(
        model="qwen3:8b",
        messages=messages,
    )

    reply = response.message.content

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