from faster_whisper import WhisperModel

# Load the model once when the program starts
model = WhisperModel(
    "base",
    device="cpu",
    compute_type="int8"
)


def speech_to_text(audio_file="recording.wav") -> str:

    segments, info = model.transcribe( audio_file,language="en",vad_filter=True,)

    text = ""

    for segment in segments:
        text += segment.text

    return text.strip()


if __name__ == "__main__":

    result = speech_to_text()

    print("\nYou said:")
    print(result)