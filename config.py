# config.py

# Audio capture setting
BLOCK_SIZE = 4096
TARGET_SAMPLE_RATE = 16000      # Sample rate (16000 Hz is native for Whisper)
CHUNK_DURATION = 4              # Records 4 second audio chunks
OVERLAP_DURATION = 0.5          # 1 second overlap between chunks
RMS_THRESHOLD = 0.01            # Energy threshold for silence in audio capture

# Server IP and endpoints
SERVER_IP = "192.168.0.179"
OLLAMA_HOST = f"http://{SERVER_IP}:30068"
WHISPER_URL = f"http://{SERVER_IP}:9000/v1/audio/transcriptions"
LLM_MODEL = "qwen2.5:3b"