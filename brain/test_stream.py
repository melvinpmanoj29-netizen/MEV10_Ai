from brain.llm import stream_mev10


print("MEV10: ", end="", flush=True)

for chunk in stream_mev10("Hello, how are you?"):
    pass

print("\nDone.")