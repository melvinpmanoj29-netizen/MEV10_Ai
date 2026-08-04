from brain.llm import ask_mev10


def main():
    print("=== MEV10 v0.1 ===")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() == "exit":
            print("Mev10: Goodbye!")
            break

        reply = ask_mev10(user_input)
        print(f"Mev10: {reply}\n")


if __name__ == "__main__":
    main()