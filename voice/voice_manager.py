from voice.microphone import record_audio
from voice.speech_to_text import speech_to_text
from voice.text_to_speech import speak
from brain.llm import ask_mev10


AUDIO_FILE = "voice/recording.wav"


def voice_chat():

    print("\n🎤 Listening...")
    record_audio(AUDIO_FILE)

    print("📝 Understanding...")
    user_text = speech_to_text(AUDIO_FILE)

    if not user_text:
        print("MEV10: I didn't hear anything.")
        return

    print(f"You: {user_text}")

    print("🧠 Processing...")
    response = ask_mev10(user_text)

    print("\n🔊 Speaking...")
    speak(response)


if __name__ == "__main__":
    voice_chat()