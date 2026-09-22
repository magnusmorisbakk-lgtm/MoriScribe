# MoriScribe 

MoriScribe is a local system audio transcriber and AI-based summarizer built with Python. The program captures system output audio from default speakers and transcribes speech using `faster-whisper`. Structured summaries are generated locally using Ollama.


## The Vision
Learn how to build a lightweight client application that turns spoken audio into notes locally, without external cloud APIs, subscriptions, or third-party services.

* **Focus on privacy:** Audio and transcripts do not leave your home network. No cloud tracking or external telemetry.
* **Client offloading:** The host PC handles zero AI computation. This means fewer resources used where it's needed. STT and LLM workloads are run on a dedicated server.

## Features

* **System Audio Capture:** Uses loopback recording through `soundcard` to record system output directly from default audio devices on your device.
* **Remote GPU workload:** Offloads Whisper processing to a containerized `faster-whisper-server` over HTTP POST.
* **LAN AI Summarization:** Routes transcribed text to a remote Ollama instance running lightweight instruction models.

## System Flow

1. **[Host PC]** -> Records system output locally through `soundcard` and creates an in memory byte stream.
2. **[Host PC]** -> Sends an HTTP POST request with in in memory `.wav` over LAN to server (Port 9000).
3. **[Server (Whisper Container)]** -> Receives `.wav` file and runs Whisper on the GPU. Returns the transcript back as an HTTP response to the host.
4. **[Host PC]** -> Receives the transcript and sends an HTTP POST request with the text over LAN to Ollama (Port 114343).
5. **[Server (Ollama Container)]** -> Receives the text, runs `qwen2.5:3b` on the GPU, and returns the summary in the HTTP response to the host PC.
6. **[Host PC]** -> Prints the transcript and summary to the console.

## Prerequisites

### 1. Host PC Requirements
* **Python 3.11 or 3.12** *(Python 3.13+ is unsupported by soundcard dependencies)*
* Network access to your Docker server over LAN.

### 2. Server Stack (TrueNAS / Dockge)
* `faster-whisper-server` running on port `8000` (`fedirz/faster-whisper-server:latest-cuda` or `latest-cpu`).
* Ollama running on port `11434` with `qwen2.5:3b` pulled:
  ```bash
  ollama pull qwen2.5:3b
## Docker Compose Configuration (Dockge / TrueNAS)

Below is the stack configuration used for running the Whisper server container via Dockge:
```YAML
services:
  whisper-server:
    image: fedirz/faster-whisper-server:latest-cuda
    container_name: whisper-server
    ports:
      - "8000:8000"
    environment:
      - WHISPER__MODEL=Systran/faster-whisper-medium
      - WHISPER__INFERENCE_DEVICE=cuda
      - WHISPER__COMPUTE_TYPE=int8
      - PRELOAD_MODELS=["Systran/faster-whisper-medium"]
    volumes:
      - whisper-cache:/root/.cache/huggingface
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    restart: unless-stopped

volumes:
  whisper-cache:
```

## Installation

1.  **Clone the repository:**
    
    ```Bash
    git clone git@github.com:magnusmorisbakk-lgtm/MoriScribe.git
    cd MoriScribe
    ```
    
2.  **Create and activate a virtual environment:**
    
    _Windows (PowerShell):_    
    ```PowerShell
    py -3.12 -m venv .venv
    .\.venv\Scripts\Activate.ps1
    ```
    
3.  **Install dependencies:**
    ```Bash
    python -m pip install soundcard numpy requests ollama
    ```
    

## Configuration

Before running the script, update your server settings in `main.py`:
```Python
# IP of your remote TrueNAS/Docker server
SERVER_IP = "192.168.0.180"

# Service endpoints
WHISPER_URL = f"http://{SERVER_IP}:8000/v1/audio/transcriptions"
OLLAMA_HOST = f"http://{SERVER_IP}:11434"
LLM_MODEL = "qwen2.5:3b"
```

## Usage

1.  Start playing any system audio.
    
2.  Run the main script:
   
    ```Bash
    python main.py
    ```
    
3.  The program will automatically:
    
    -   Continuously record local system audio.
        
    -   Send the audio chunks to your server for Whisper GPU transcription.
        
    -   Send the transcript to Ollama for bullet point summarization.
        
    -   Print the results directly in your terminal
        

## Hardware Specs used during development

### Client Device (Host PC)

-   **CPU:** i9-12900K
    
-   **RAM:** 32GB DDR4
    
-   **Audio Device:** AirPods, PC speakers, headphones
    
-   **OS:** Windows 11
    

### Remote Server (TrueNAS / Dockge Host)

-   **Compute:** TrueNAS SCALE, Debian Linux
    
-   **CPU:** R5 3600
    
-   **GPU:** RTX 2060 6GB & GTX 1060 6GB _(GPU with CUDA cores is recommended)_
    
-   **RAM:** 16GB DDR4
    
-   **Storage:** SSD is recommended, but works fine on HDD