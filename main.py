import os
import wave
import requests
import numpy as np
import soundcard as sc
import ollama

# -------------------------
# Configuration and settings
# -------------------------
DURATION = 30                   # Recording duration in seconds
TARGET_SAMPLE_RATE = 16000      # Sample rate (16000 Hz is native for Whisper)
TEMP_AUDIO_FILE = "capture.wav" # Temporary output file

# IP of remote server
SERVER_IP = "192.168.0.180"

# Service endpoints
OLLAMA_HOST = f"http://{SERVER_IP}:30068"
WHISPER_URL = f"http://{SERVER_IP}:8000/v1/audio/transcriptions"
LLM_MODEL = "qwen2.5:3b"

# Record local system audio
def record_system_audio(duration, sample_rate, output_path):
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

    with wave.open(output_path, "wb") as wav_file:
        wav_file.setnchannels(1)           # Mono
        wav_file.setsampwidth(2)           # 16-bit
        wav_file.setframerate(sample_rate) # 16000 Hz
        wav_file.writeframes(pcm16_data.tobytes())

    print("(1/4) Recording audio sample completed.")

# Send audio file to remote server for transcription (Whisper)
def remote_transcribe(audio_path):
    print("(2/4) Sending audio file to remote server for transcription")

    try:
        with open(audio_path, "rb") as audio_file:
            files = {"file": (os.path.basename(audio_path), 
                                                    audio_file, "audio/wav")}
            data = {
                "model": "Systran/faster-whisper-medium", # Transcription model
                "language": "en"    # Norwegian    
            }
            
            # Send file to remote whisper webserver endpoint over LAN
            response = requests.post(WHISPER_URL, files=files, data=data, timeout=30)
            response.raise_for_status()

            # Parse JSON output returned by API
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
    record_system_audio(DURATION, TARGET_SAMPLE_RATE, TEMP_AUDIO_FILE)

    # 2: Send audio to server for Whisper speech to text
    transcript = remote_transcribe(TEMP_AUDIO_FILE)

    # Remove local temporary .wav file
    if os.path.exists(TEMP_AUDIO_FILE):
        os.remove(TEMP_AUDIO_FILE)

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