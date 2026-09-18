import io
import queue
import signal
import sys
import threading
import time
import wave
import requests
import numpy as np
import soundcard as sc
import ollama

from config import (
    WHISPER_URL,
    OLLAMA_HOST,
    LLM_MODEL,
    CHUNK_DURATION,
    TARGET_SAMPLE_RATE,
    BLOCK_SIZE
)




audio_queue = queue.Queue()
running = True

# Record local system audio
def record_system_audio(duration, sample_rate):
    default_speaker = sc.default_speaker()
    print(f"Capturing output from source: {default_speaker.name}")
    print(f"\n(1/4) Recording {duration} seconds of system audio...")

    loopback_mic = sc.get_microphone(id=default_speaker.id, include_loopback=True)

    with loopback_mic.recorder(samplerate=sample_rate) as mic:
        audio_data = mic.record(numframes=sample_rate * duration)

    # Converts stereo to mono 
    if audio_data.ndim > 1 and audio_data.shape[1] > 1:
        audio_mono = np.mean(audio_data, axis=1)
    else:
        audio_mono = audio_data.flatten()

    pcm16_data = (audio_mono * 32767).astype(np.int16)

    # Create in memory byte buffer, instead of creating a temp .wav file
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, "wb") as wav_file:
        wav_file.setnchannels(1)           # Mono
        wav_file.setsampwidth(2)           # 16-bit
        wav_file.setframerate(sample_rate) # 16000 Hz
        wav_file.writeframes(pcm16_data.tobytes())

    wav_buffer.seek(0)
    print("(1/4) Recording audio sample completed.")
    return wav_buffer

# Send audio file to remote server for transcription (Whisper)
def remote_transcribe(wav_buffer):
    print("(2/4) Sending audio file to remote server for transcription")

    try:
        files = {"file": ("capture.wav", wav_buffer, "audio/wav")}
        data = {
            "model": "Systran/faster-whisper-medium",
            "language": "en"
        }

        # Send memory buffer to remote whisper server endpoint
        response = requests.post(WHISPER_URL, files=files, data=data, timeout=30)
        response.raise_for_status()

        result = response.json()
        return result.get("text", "").strip()
    
    except requests.exceptions.RequestException as err:
        print(f"Failed to reach remote Whisper server ({WHISPER_URL}): {err}")
        return None

# Sends transcription to remote server for summarization (Ollama)
def summarize_remote(transcript_text):
    print(f"\n(3/4) Sending transcript to TrueNAS server ({LLM_MODEL}) for summarization...")
    
    try:
        client = ollama.Client(host=OLLAMA_HOST)
        response = client.chat(
            model=LLM_MODEL,
            messages=[{
                'role': 'user',
                'content': f"Oppsummer følgende transkripsjon i korte kulepunkter på norsk:\n\n{transcript_text}"
            }]
        )
        return response['message']['content']

    except Exception as err:
        print(f"Failed to reach Ollama server ({OLLAMA_HOST}): {err}")
        return None

if __name__ == "__main__":
    # 1: Record audio on host PC
    wav_buffer = record_system_audio(DURATION, TARGET_SAMPLE_RATE)

    # 2: Send byte memory buffer to server for whisper speech to text
    transcript = remote_transcribe(wav_buffer)

    print("\n---TRANSKRIPT---")
    if transcript:
        print(transcript)
        
        # Step 3: Send text to TrueNAS Ollama for LLM Summarization
        summary = summarize_remote(transcript)
        
        if summary:
            print("\n---SAMMENDRAG---")
            print(summary)
    else:
        print("Ingen tale registrert eller feil ved transkripsjon.")