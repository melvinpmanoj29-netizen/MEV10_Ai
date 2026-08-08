import re
import subprocess
import sys
import wave
from pathlib import Path
import winsound


VOICE_MODEL = "en_US-ryan-medium"

OUTPUT_FILE = Path("voice/mev10_response.wav")
TEMP_DIR = Path("voice/tts_temp")

PAUSE_SECONDS = 0.25


def clean_for_speech(text: str) -> str:
    """Remove formatting and symbols that should not be spoken."""

    # Remove code blocks
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)

    # Remove Markdown headings
    text = re.sub(r"^\s*#+\s*", "", text, flags=re.MULTILINE)

    # Remove Markdown formatting
    text = re.sub(r"[*_~`]+", "", text)

    # Remove Markdown links but keep visible text
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)

    # Remove emojis and symbols
    text = "".join(
        char
        for char in text
        if not (
            0x1F300 <= ord(char) <= 0x1FAFF
            or 0x2600 <= ord(char) <= 0x27BF
        )
    )

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


def generate_sentence_audio(sentence: str, output_file: Path) -> None:
    """Generate a WAV file for one sentence."""

    subprocess.run(
        [
            sys.executable,
            "-m",
            "piper",
            "-m",
            VOICE_MODEL,
            "-f",
            str(output_file),
            "--",
            sentence,
        ],
        check=True,
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


def speak(text: str) -> None:
    """Convert text to speech using Piper and play it."""

    text = clean_for_speech(text)

    if not text:
        return

    sentences = split_sentences(text)

    TEMP_DIR.mkdir(parents=True, exist_ok=True)

    audio_files = []

    try:

        # Generate all sentences first
        for index, sentence in enumerate(sentences):

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