import re
import wave
from pathlib import Path
import winsound
import unicodedata

from piper.voice import PiperVoice

VOICE_MODEL = "en_US-ryan-medium"
MODEL_PATH = Path("en_US-ryan-medium.onnx")

print("🔊 Loading MEV10 voice...")

PIPER_VOICE = PiperVoice.load(
    str(MODEL_PATH)
)

print("✅ MEV10 voice ready.")

OUTPUT_FILE = Path("voice/mev10_response.wav")
TEMP_DIR = Path("voice/tts_temp")

PAUSE_SECONDS = 0.25


def clean_for_speech(text: str) -> str:
    """Remove formatting, emojis, and non-speech symbols."""

    # Remove code blocks
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)

    # Remove Markdown headings
    text = re.sub(r"^\s*#+\s*", "", text, flags=re.MULTILINE)

    # Remove Markdown formatting
    text = re.sub(r"[*_~`]+", "", text)

    # Remove numbered Markdown list markers
    text = re.sub(r"(?m)^\s*\d+\.\s*", "", text)

    # Remove Markdown links but keep visible text
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)

    cleaned = []

    for char in text:
        category = unicodedata.category(char)

        # Remove emoji/symbol characters
        if (
            0x1F300 <= ord(char) <= 0x1FAFF
            or 0x2600 <= ord(char) <= 0x27BF
        ):
            continue

        # Remove Unicode marks such as emoji variation selectors
        # and combining characters that should not be spoken alone.
        if category.startswith("M"):
            continue

        cleaned.append(char)

    text = "".join(cleaned)

    # Remove unnecessary symbols
    text = re.sub(r"[|<>]", " ", text)

    # Collapse spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Clean excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def split_sentences(text: str) -> list[str]:
    """Split text into sentences."""

    sentences = re.split(r"(?<=[.!?])\s+", text)

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


def generate_sentence_audio(
    sentence: str,
    output_file: Path,
) -> None:
    """Generate a WAV file using the already-loaded Piper model."""

    with wave.open(str(output_file), "wb") as wav_file:
        PIPER_VOICE.synthesize_wav(
            sentence,
            wav_file,
        )


def combine_audio(files: list[Path], output_file: Path) -> None:
    """Combine WAV files with a controlled pause between them."""

    with wave.open(str(files[0]), "rb") as first:
        params = first.getparams()

    with wave.open(str(output_file), "wb") as output:

        output.setparams(params)

        for index, file in enumerate(files):

            with wave.open(str(file), "rb") as audio:
                frames = audio.readframes(audio.getnframes())

            output.writeframes(frames)

            # Add controlled silence between sentences
            if index < len(files) - 1:

                silence_frames = int(
                    params.framerate * PAUSE_SECONDS
                )

                silence = b"\x00" * (
                    silence_frames *
                    params.nchannels *
                    params.sampwidth
                )

                output.writeframes(silence)

def speak_sentence(sentence: str) -> None:
    """Generate and immediately play one sentence."""

    sentence = clean_for_speech(sentence)

    if not sentence:
        return

    temp_file = TEMP_DIR / "stream_sentence.wav"

    TEMP_DIR.mkdir(parents=True, exist_ok=True)

    try:
        generate_sentence_audio(
            sentence,
            temp_file,
        )

        winsound.PlaySound(
            str(temp_file),
            winsound.SND_FILENAME,
        )

    finally:
        if temp_file.exists():
            temp_file.unlink()


def speak(text: str) -> None:
    """Convert text to speech using Piper and play it."""

    text = clean_for_speech(text)

    if not text:
        return

    sentences = split_sentences(text)

    sentences = [
        sentence
        for sentence in sentences
        if sentence.strip()
    ]

    TEMP_DIR.mkdir(parents=True, exist_ok=True)

    audio_files = []

    try:

        # Generate all sentences first
        for index, sentence in enumerate(sentences):

            if not sentence.strip():
                continue

            temp_file = TEMP_DIR / f"sentence_{index}.wav"

            generate_sentence_audio(
                sentence,
                temp_file,
            )

            audio_files.append(temp_file)

        # Combine them into one WAV
        combine_audio(
            audio_files,
            OUTPUT_FILE,
        )

        # Play ONE continuous audio file
        winsound.PlaySound(
            str(OUTPUT_FILE),
            winsound.SND_FILENAME,
        )

    finally:

        # Delete temporary sentence files
        for file in audio_files:

            if file.exists():
                file.unlink()


if __name__ == "__main__":

    speak(
        "Hello! 😊 "
        "I am MEV10. "
        "I can help you with programming, learning, and productivity."
    )