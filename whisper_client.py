# whisper_client.py
import requests
import numpy as np
from audio_recorder import create_wav_buffer
from config import WHISPER_URL, TARGET_SAMPLE_RATE

def transcribe_audio_chunk(audio_data: np.ndarray) -> str | None:
    # Converts audio array into wav buffer in memory and posts to whisper endpoint
    wav_buffer = create_wav_buffer(audio_data, TARGET_SAMPLE_RATE)

    try:
        files = {"file": ("chunk.wav", wav_buffer, "audio/wav")}
        data = {
            "model": "Systran/faster-whisper-medium",
            "language": "no"
        }

        response = requests.post(WHISPER_URL, files=files, data=data, timeout=5)
        response.raise_for_status()

        result = response.json()
        return result.get("text", "").strip()

    except requests.exceptions.RequestException as err:
        print(f"\nWhisper request failed {err}")
        return None