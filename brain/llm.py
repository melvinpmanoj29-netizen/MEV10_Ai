from ollama import chat

def ask_mev10(message: str) -> str:
    print("Sending request to Ollama...")

    response = chat(
        model="qwen3:8b",
        messages=[
            {
                "role": "user",
                "content": message,
            }
        ],
    )

    print("Received response from Ollama.")

    return response.message.content