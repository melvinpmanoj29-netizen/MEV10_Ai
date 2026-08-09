from faster_whisper import WhisperModel


# Load Whisper once when MEV10 starts.
model = WhisperModel(
    "small.en",
    device="cpu",
    compute_type="int8",
)


def speech_to_text(audio_file="recording.wav") -> str:

    segments, info = model.transcribe(
        audio_file,
        language="en",
        task="transcribe",

        # More reliable than greedy decoding.
        beam_size=5,

        # Each voice command should be independent.
        condition_on_previous_text=False,

        # Remove non-speech regions.
        vad_filter=True,

        vad_parameters={
            "min_silence_duration_ms": 500,
        },
    )

    text = ""

    for segment in segments:
        text += segment.text

    return text.strip()


if __name__ == "__main__":

    result = speech_to_text()

    print("\nYou said:")
    print(result)