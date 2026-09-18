# main.py
import queue
import signal
import threading
import time
import warnings

from audio_recorder import capture_audio_loop
from whisper_client import transcribe_audio_chunk

audio_queue = queue.Queue()
running = True

def transcription():
    # Pulls audio arrays from queue and POSTS to whipser API
    while running or not audio_queue.empty():
        try:
            audio_data = audio_queue.get(timeout=1)
        except queue.Empty:
            continue

        trancript = transcribe_audio_chunk(audio_data)
        if trancript:
            print(f"Live: {trancript}")

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
        daemon=True
    )

    capture_thread.start()
    transcribe_thread.start()

    print("Continous transcription. Ctrl+C to stop\n")

    while running:
        time.sleep(0.5)

    capture_thread.join(timeout=2)
    transcribe_thread.join(timeout=5)
    print("EXIT")