# main.py
import queue
import signal
import threading
import time
from audio_recorder import capture_audio_loop
from whisper_client import transcribe_audio_chunk
from summarizer import summarize_transcript

audio_queue = queue.Queue()
running = True
transcript_history = []

def transcription():
    # Pulls audio arrays from queue and POSTS to whipser API
    while running or not audio_queue.empty():
        try:
            audio_data = audio_queue.get(timeout=1)
        except queue.Empty:
            continue

        trancript = transcribe_audio_chunk(audio_data)
        if trancript:
            timestamp = time.strftime("%H:%M:%S")
            print(f"{timestamp}: {trancript}")
            transcript_history.append(trancript)

        audio_queue.task_done()

def exit(sig, frame):
    # Soft exit when stopping program (Ctrl + C)
    global running
    print("\nStopping transcription")
    running = False

if __name__ == "__main__":
    signal.signal(signal.SIGINT, exit)

    capture_thread = threading.Thread(
        target=capture_audio_loop,
        args=(audio_queue, lambda: running),
        daemon=True,
    )
    transcribe_thread = threading.Thread(
        target=transcription,
        daemon=False
    )

    capture_thread.start()
    transcribe_thread.start()

    print("Continous transcription. Ctrl+C to stop\n")

    while running:
        time.sleep(0.5)

    capture_thread.join(timeout=2)
    audio_queue.join()
    transcribe_thread.join()
    

    full_transcript = "\n".join(transcript_history)
    if full_transcript:
        print("\n--- Generating summary ---")
        summary  = summarize_transcript(full_transcript)
        if summary:
            print(f"{summary}")

    print("EXIT")