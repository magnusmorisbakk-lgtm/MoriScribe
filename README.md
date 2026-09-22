
# MoriScribe
MoriScribe is a local system audio transcriber and AI-based summarizer built with Python. The program captures system output audio from default speakers and transcribes speech using `faster-whisper`. Structured summaries are generated locally using Ollama.

  

## The Vision
Learn how to build a lightweight client application that turns spoken audio into notes locally, without external cloud APIs, subscriptions, or third-party services.

  

*  **Focus on privacy:** Audio and transcripts do not leave your home network. No cloud tracking or external telemetry.
*  **Client offloading:** The host PC handles zero AI computation. STT and LLM workloads are run on a dedicated server.

  

## Features
*  **System Audio Capture:** Uses loopback recording through `soundcard` to record system output directly from default audio devices on your device.

*  **Remote GPU workload:** Offloads Whisper processing to a containerized `faster-whisper-server` over HTTP POST.

*  **LAN AI Summarization:** Routes transcribed text to a remote Ollama instance running lightweight instruction models.

  

## System Flow
1.  **[Host PC]** -> Records system output locally through `soundcard` and creates an in-memory byte stream.
2.  **[Host PC]** -> Sends an HTTP POST request with an in-memory `.wav` file over LAN to the Whisper server (Port 9000).
3.  **[Server (Whisper Container)]** -> Receives `.wav` file and runs Whisper on the GPU. Returns the transcript back as an HTTP response to the host.
4.  **[Host PC]** -> Receives the transcript and sends an HTTP POST request with the text over LAN to Ollama (Port 11434).
5.  **[Server (Ollama Container)]** -> Receives the text, runs `qwen2.5:3b` on the GPU, and returns the summary in the HTTP response to the host PC.
6.  **[Host PC]** -> Prints the transcript and summary to the console.

  

## Prerequisites
### 1. Host PC Requirements

*  **Python 3.11 or 3.12**  *(Python 3.13+ is unsupported by soundcard dependencies)*
* Network access to your Docker server over LAN.

### 2. Server Stack (Docker / Portainer / Dockge)
*  `faster-whisper-server` running on port `9000` (`fedirz/faster-whisper-server:latest-cuda` or `latest-cpu`).
* Ollama running on port `11434` with `qwen2.5:3b` pulled:

```bash
ollama pull qwen2.5:3b
```

## Docker Compose Configuration
Below is the stack configuration used for running the Whisper server container:

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
1. Clone the repository:
```Bash

git clone [https://github.com/YOUR_GITHUB_USERNAME/MoriScribe.git](https://github.com/YOUR_GITHUB_USERNAME/MoriScribe.git)```
cd MoriScribe
```

2. Create and activate a virtual environment:
Windows (PowerShell):
```PowerShell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```
3. Install dependencies:
```Bash
python -m pip install soundcard numpy requests ollama python-dotenv
```

## Configuration
Copy .env.example to .env and fill in your server's IP address and endpoints


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
        

## Hardware Requirement & Tested Setup

### Client Device (Host PC)

-   **OS:** Windows / Linux
    
-   **Python:** 3.12
    
-   **Audio Device:** Default system output / Loopback device
    

### Remote Server

-   **OS:** Linux (Ubuntu Server / Debian / TrueNAS)
    
-   **GPU:** NVIDIA GPU with CUDA support recommended
    
-   **Containers:** Docker runtime running Ollama and Faster-Whisper-Server