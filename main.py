from brain.llm import ask_mev10


def main():
    print("=== MEV10 v0.3 ===")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() == "exit":
            print("Mev10: Goodbye!")
            break

        ask_mev10(user_input)
        print()


if __name__ == "__main__":
    main()