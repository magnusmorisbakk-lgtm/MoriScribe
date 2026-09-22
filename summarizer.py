# summarizer.py

import ollama
from config import OLLAMA_HOST, LLM_MODEL

client = ollama.Client(host=OLLAMA_HOST)

def summarize_transcript(transcript: str) -> str:
    if not transcript.strip():
        return ""

    prompt = (
        "Summarize the following transcription into concise bullet points. "
        "Summarize in the same language that the transcription is given in."
        "Focus on key facts and main topics:\n\n"
        f"{transcript}"
    )

    try:
        response = client.generate(
            model=LLM_MODEL,
            prompt=prompt,
            stream=False
        )
        return response['response']
    except Exception as err:
        print(f"Failed to generate summary with Ollama: {err}")
        return ""