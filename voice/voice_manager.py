import re
import queue
import threading
import time
import winsound
from pathlib import Path

from voice.microphone import record_audio
from voice.speech_to_text import speech_to_text
from voice.text_to_speech import (
    generate_sentence_audio,
    clean_for_speech,
    TEMP_DIR,
    PAUSE_SECONDS,
)
from brain.llm import stream_mev10


AUDIO_FILE = "voice/recording.wav"


def tts_generator(sentence_queue, audio_queue):
    """
    Generate WAV files from sentences.

    This runs independently from the audio player so Piper can
    prepare upcoming sentences while Ryan is speaking.
    """

    sentence_index = 0

    while True:

        sentence = sentence_queue.get()

        if sentence is None:
            sentence_queue.task_done()

            # Tell audio player that generation is completely finished.
            audio_queue.put(None)

            break

        try:
            sentence = clean_for_speech(sentence)

            if not sentence:
                continue

            temp_file = (
                TEMP_DIR / f"stream_sentence_{sentence_index}.wav"
            )

            sentence_index += 1

            TEMP_DIR.mkdir(parents=True, exist_ok=True)

            print(
                f"\n⚙️ Preparing audio: {sentence}"
            )

            generate_sentence_audio(
                sentence,
                temp_file,
            )

            # Put the already-generated WAV into the audio queue.
            audio_queue.put(temp_file)

        finally:
            sentence_queue.task_done()


def audio_player(audio_queue):
    """
    Play already-generated WAV files.

    Since Piper generation happens in another thread,
    this thread should have very little delay between sentences.
    """

    first_sentence = True

    while True:

        audio_file = audio_queue.get()

        if audio_file is None:
            audio_queue.task_done()
            break

        try:

            # Add the controlled pause between sentences.
            if not first_sentence:
                time.sleep(PAUSE_SECONDS)

            first_sentence = False

            print("🔊 Speaking...")

            winsound.PlaySound(
                str(audio_file),
                winsound.SND_FILENAME,
            )

        finally:

            if audio_file.exists():
                audio_file.unlink()

            audio_queue.task_done()


def voice_chat():

    print("\n🎤 Listening...")
    record_audio(AUDIO_FILE)

    print("📝 Understanding...")
    user_text = speech_to_text(AUDIO_FILE)

    if not user_text:
        print("MEV10: I didn't hear anything.")
        return

    print(f"You: {user_text}")
    print("🧠 Processing...\n")

    sentence_queue = queue.Queue()
    audio_queue = queue.Queue()

    # -----------------------------
    # TTS generation thread
    # -----------------------------

    generator_thread = threading.Thread(
        target=tts_generator,
        args=(sentence_queue, audio_queue),
        daemon=True,
    )

    # -----------------------------
    # Audio playback thread
    # -----------------------------

    player_thread = threading.Thread(
        target=audio_player,
        args=(audio_queue,),
        daemon=True,
    )

    generator_thread.start()
    player_thread.start()

    sentence_buffer = ""

    print("MEV10: ", end="", flush=True)

    try:

        # Qwen streams response chunks.
        for chunk in stream_mev10(user_text):

            sentence_buffer += chunk

            while True:

                match = re.search(
                    r"(.+?[.!?])(?:\s+|$)",
                    sentence_buffer,
                    re.DOTALL,
                )

                if not match:
                    break

                sentence = match.group(1).strip()

                sentence_buffer = sentence_buffer[
                    match.end():
                ]

                clean_sentence = clean_for_speech(sentence)

                if not clean_sentence:
                    continue

                print(
                    f"\n🔊 Sentence ready: {clean_sentence}"
                )

                sentence_queue.put(clean_sentence)

        # -----------------------------
        # Remaining text
        # -----------------------------

        remaining = sentence_buffer.strip()

        if remaining:

            clean_remaining = clean_for_speech(remaining)

            if clean_remaining:

                print(
                    f"\n🔊 Sentence ready: {clean_remaining}"
                )

                sentence_queue.put(clean_remaining)

    finally:

        # Tell generator that Qwen has finished.
        sentence_queue.put(None)

        # Wait until every sentence has been processed
        # by the Piper generator.
        sentence_queue.join()

        generator_thread.join()

        # Wait until every generated WAV has been played.
        audio_queue.join()

        player_thread.join()

    print("\n")


if __name__ == "__main__":
    voice_chat()