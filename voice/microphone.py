import sounddevice as sd
import soundfile as sf
import numpy as np
import time
from collections import deque


SAMPLE_RATE = 16000

# Stop after this much continuous silence
SILENCE_TIMEOUT = 3.0

# Audio chunks are 100 ms
CHUNK_DURATION = 0.1

# Keep this much audio before speech starts.
# This prevents clipping the first word.
PRE_ROLL_SECONDS = 0.5

# Number of consecutive speech chunks required
# before we consider the user to have started speaking.
SPEECH_CONFIRMATION_CHUNKS = 3

# Minimum RMS threshold.
# Prevents extremely quiet background noise from being
# interpreted as speech.
MIN_SPEECH_THRESHOLD = 0.008


def calculate_volume(audio):
    """Calculate RMS volume of an audio chunk."""

    return float(np.sqrt(np.mean(audio ** 2)))


def record_audio(filename="recording.wav"):
    print("🎤 Recording... Speak now!")

    chunk_size = int(CHUNK_DURATION * SAMPLE_RATE)
    pre_roll_chunks = int(PRE_ROLL_SECONDS / CHUNK_DURATION)

    # Keep a small amount of audio before speech starts.
    pre_roll = deque(maxlen=pre_roll_chunks)

    audio_chunks = []

    started_speaking = False
    consecutive_speech_chunks = 0
    last_speech_time = None

    try:

        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="float32",
            blocksize=chunk_size,
        ) as stream:

            # ---------------------------------
            # Noise-floor calibration
            # ---------------------------------

            noise_samples = []

            for _ in range(5):
                audio, overflowed = stream.read(chunk_size)

                audio = audio.copy()

                pre_roll.append(audio)

                volume = calculate_volume(audio)

                noise_samples.append(volume)

            noise_floor = float(np.median(noise_samples))

            # Adaptive threshold
            speech_threshold = max(
                MIN_SPEECH_THRESHOLD,
                noise_floor * 3.0,
            )

            print(
                f"🎚️ Noise floor: {noise_floor:.5f} | "
                f"Speech threshold: {speech_threshold:.5f}"
            )

            # ---------------------------------
            # Listen
            # ---------------------------------

            while True:

                audio, overflowed = stream.read(chunk_size)

                audio = audio.copy()

                volume = calculate_volume(audio)

                current_time = time.time()

                # Always maintain the pre-roll buffer
                if not started_speaking:
                    pre_roll.append(audio)

                # ---------------------------------
                # Speech detection
                # ---------------------------------

                if volume > speech_threshold:

                    consecutive_speech_chunks += 1

                else:

                    consecutive_speech_chunks = 0

                # ---------------------------------
                # Confirm speech
                # ---------------------------------

                if (
                    not started_speaking
                    and consecutive_speech_chunks
                    >= SPEECH_CONFIRMATION_CHUNKS
                ):

                    started_speaking = True

                    # Include the audio immediately before
                    # speech was detected.
                    audio_chunks.extend(
                        list(pre_roll)
                    )

                    audio_chunks.append(audio)

                    last_speech_time = current_time

                    print("🎙️ Speech detected...")

                    continue

                # ---------------------------------
                # Already speaking
                # ---------------------------------

                if started_speaking:

                    audio_chunks.append(audio)

                    if volume > speech_threshold:

                        last_speech_time = current_time

                    else:

                        if (
                            last_speech_time is not None
                            and
                            current_time - last_speech_time
                            >= SILENCE_TIMEOUT
                        ):

                            print(
                                "🤫 3 seconds of silence detected."
                            )

                            break

    except KeyboardInterrupt:

        print("\n🛑 Recording interrupted.")

    # ---------------------------------
    # No speech detected
    # ---------------------------------

    if not audio_chunks:

        print("⚠️ No speech detected.")

        # Save an empty/silent recording rather than crashing.
        silence = np.zeros(
            int(SAMPLE_RATE * 0.1),
            dtype=np.float32,
        )

        sf.write(
            filename,
            silence,
            SAMPLE_RATE,
        )

        return

    # ---------------------------------
    # Combine audio
    # ---------------------------------

    audio = np.concatenate(
        audio_chunks,
        axis=0,
    )

    # ---------------------------------
    # Remove excessive trailing silence
    # ---------------------------------

    trim_samples = int(
        SILENCE_TIMEOUT * SAMPLE_RATE
    )

    if len(audio) > trim_samples:

        audio = audio[:-trim_samples]

    # ---------------------------------
    # Save
    # ---------------------------------

    sf.write(
        filename,
        audio,
        SAMPLE_RATE,
    )

    print(
        f"✅ Audio saved as {filename}"
    )


if __name__ == "__main__":
    record_audio()