
# MoriScribe 
MoriScribe is a local system audio transcriber and AI based summarizer built with python. The program captures system output audio from system default speakers and transcribes speech using `faster-whisper`. Structured summaries are generated locally using Ollama.

---

##  Features
* System Audio Capture: Uses loopback recording via `soundcard` to capture output audio directly from default speaker.
* Speech to text: Utilizes `faster-whisper` running 8 bit quantized models on CPU. Larger quantized models are possible with more sufficient hardware.
* Focus on privacy: Transcribed text is routed through a local Ollama instance, meaning privacy and no API costs.

---

## Prerequisites

* **Python 3.11 or 3.12** 
* **Ollama** installed and running locally with the `llama3` model pulled:
  ```bash
  ollama pull llama3

## Installation

1.  **Clone the repository:**
    
    Bash
    
    ```
    git clone [https://github.com/your-username/MoriScribe.git](https://github.com/your-username/MoriScribe.git)
    cd MoriScribe
    
    ```
    
2.  **Create and activate a virtual environment:**
    
    Windows (PowerShell):
    
    PowerShell
    
    ```
    py -3.12 -m venv .venv
    .\.venv\Scripts\Activate.ps1
    
    ```
    
    Linux/macOS:
    
    Bash
    
    ```
    python3.12 -m venv .venv
    source .venv/bin/activate
    
    ```
    
3.  **Install dependencies:**
    
    Bash
    
    ```
    python -m pip install faster-whisper soundcard numpy ollama
    
    ```
    

## Usage

1.  Start playing any system audio (e.g., a video, call, or audio clip).
    
2.  Run the main script:
    
    Bash
    
    ```
    python main.py
    
    ```
    
3.  The script will:
    
    -   Record 10 seconds of system audio.
        
    -   Transcribe the Norwegian speech to text.
        
    -   Output a bulleted summary via Ollama.