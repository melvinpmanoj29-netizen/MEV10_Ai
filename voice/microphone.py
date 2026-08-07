import sounddevice as sd
import soundfile as sf

SAMPLE_RATE = 16000
DURATION = 5  # seconds


def record_audio(filename="recording.wav"):
    print("🎤 Recording... Speak now!")

    audio = sd.rec(
        int(DURATION * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32",
    )

    sd.wait()

    sf.write(filename, audio, SAMPLE_RATE)

    print(f"✅ Audio saved as {filename}")


if __name__ == "__main__":
    record_audio()