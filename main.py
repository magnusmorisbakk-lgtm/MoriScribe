import os
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

import numpy as np
import soundcard as sc
from faster_whisper import WhisperModel
import ollama

DURATION = 10               # Recording duration in seconds
TARGET_SAMPLE_RATE = 16000  # Sample rate (16000 is native for whisper)

# 1. Load local whisper engine
print("(1/4) Loading local Whisper model into memory")
model = WhisperModel("medium", device="cpu", compute_type="int8")

# 2. Retrieve default Speaker 
default_speaker = sc.default_speaker()
print(f"\n[Info] Capturing Output: {default_speaker.name}")

# Retrieve the loopback stream for the default speaker
loopback_mic = sc.get_microphone(id=default_speaker.id, include_loopback=True)

# 3. Capture system default audio
print(f"(2/4) Recording {DURATION} seconds of system audio...")

with loopback_mic.recorder(samplerate=TARGET_SAMPLE_RATE) as mic:
    # Captured audio is stored as an array
    audio_data = mic.record(numframes=TARGET_SAMPLE_RATE * DURATION)
    
print("(3/5) Recording complete")

# 4. Handle mono conversion for Whisper 
# The soundcard returns shape 
if audio_data.ndim > 1 and audio_data.shape[1] > 1:
    audio_mono = np.mean(audio_data, axis=1)
else:
    audio_mono = audio_data.flatten()

# Ensure that the array is float32 for Whisper
audio_mono = audio_mono.astype(np.float32)

# 5. Transcribe audio (Defaulted to norwegian)
print("[3/4] Transcribing system audio...")
segments, _ = model.transcribe(audio_mono, language="no", beam_size=5)
transcript = " ".join([segment.text for segment in segments]).strip()

print(f"\n=== TRANSKRIPT ===")
print(transcript if transcript else "[Ingen tale registrert]")

# 6. Summarize via local Ollama
if transcript:
    print("\n[4/4] Genererer sammendrag via Ollama...")
    try:
        response = ollama.chat(
            model='llama3',
            messages=[{
                'role': 'user',
                'content': f"Oppsummerer transkripsjon på norsk:\n\n{transcript}"
            }]
        )
        print(f"\n---SAMMENDRAG---")
        print(response['message']['content'])
    except Exception as err:
        print(f"[Feil] Kunne ikke koble til Ollama: {err}")