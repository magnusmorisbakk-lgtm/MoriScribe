import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# Audio capture settings
BLOCK_SIZE = int(os.getenv("BLOCK_SIZE", 4096))
TARGET_SAMPLE_RATE = int(os.getenv("TARGET_SAMPLE_RATE", 16000))
CHUNK_DURATION = float(os.getenv("CHUNK_DURATION", 4))
OVERLAP_DURATION = float(os.getenv("OVERLAP_DURATION", 0.5))
RMS_THRESHOLD = float(os.getenv("RMS_THRESHOLD", 0.01))

# Server IP and endpoints
SERVER_IP = os.getenv("SERVER_IP", "127.0.0.1")
OLLAMA_PORT = os.getenv("OLLAMA_PORT", "11434")
WHISPER_PORT = os.getenv("WHISPER_PORT", "9000")

OLLAMA_HOST = f"http://{SERVER_IP}:{OLLAMA_PORT}"
WHISPER_URL = f"http://{SERVER_IP}:{WHISPER_PORT}/v1/audio/transcriptions"
LLM_MODEL = os.getenv("LLM_MODEL", "qwen2.5:3b")