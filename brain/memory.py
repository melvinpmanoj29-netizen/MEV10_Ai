import json
import re
from pathlib import Path


MEMORY_FILE = Path("memory/user_memory.json")


def load_memory() -> dict:
    """Load persistent user memory from disk."""

    if not MEMORY_FILE.exists():
        return {}

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    except (json.JSONDecodeError, OSError):
        return {}


def save_memory(memory: dict) -> None:
    """Save persistent user memory to disk."""

    MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(MEMORY_FILE, "w", encoding="utf-8") as file:
        json.dump(memory, file, indent=4, ensure_ascii=False)


def remember_name(message: str) -> None:
    """Detect and save the user's name when explicitly provided."""

    patterns = [
        r"\bmy name is\s+([A-Za-z][A-Za-z .'-]{0,50})",
        r"\bcall me\s+([A-Za-z][A-Za-z .'-]{0,50})",
    ]

    for pattern in patterns:
        match = re.search(pattern, message, re.IGNORECASE)

        if match:
            name = match.group(1).strip(" .,!?:;")

            memory = load_memory()
            memory["name"] = name
            save_memory(memory)

            print(f"💾 Remembered your name: {name}")
            return


def get_memory_context() -> str:
    """Return persistent memory in a format suitable for the LLM."""

    memory = load_memory()

    if not memory:
        return ""

    lines = ["Persistent information about the user:"]

    if "name" in memory:
        lines.append(f"- The user's name is {memory['name']}.")

    return "\n".join(lines)