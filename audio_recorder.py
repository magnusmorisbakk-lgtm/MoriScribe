# audio_recorder.py
import io
import wave
import numpy as np
import soundcard as sc
from config import CHUNK_DURATION, OVERLAP_DURATION, TARGET_SAMPLE_RATE, BLOCK_SIZE

def create_wav_buffer(audio_mono: np.ndarray, sample_rate: int) -> io.BytesIO:
    # Create in memory byte buffer, instead of creating a temp .wav file
    pcm16_data = (audio_mono * 32767).astype(np.int16)
    wav_buffer = io.BytesIO()

    with wave.open(wav_buffer, "wb") as wav_file:
        wav_file.setnchannels(1)           # Mono
        wav_file.setsampwidth(2)           # 16 bit
        wav_file.setframerate(sample_rate) # 16 kHz
        wav_file.writeframes(pcm16_data.tobytes())

    wav_buffer.seek(0)
    return wav_buffer

def capture_audio_loop(audio_queue, running_flag):
    default_speaker = sc.default_speaker()
    
    # Pass default_speaker.id 
    loopback_mic = sc.get_microphone(id=default_speaker.id, include_loopback=True)

    print(f"Listening continuously on: {default_speaker.name}")

    total_frames = int(TARGET_SAMPLE_RATE * CHUNK_DURATION)
    overlap_frames = int(TARGET_SAMPLE_RATE * OVERLAP_DURATION)
    previous_overlap = np.array([], dtype=np.float32)

    with loopback_mic.recorder(samplerate=TARGET_SAMPLE_RATE, 
                                                blocksize=BLOCK_SIZE) as mic:
        while running_flag():
            raw_data = mic.record(numframes=total_frames)

            if raw_data.ndim > 1 and raw_data.shape[1] > 1:
                audio_mono = np.mean(raw_data, axis=1)
            else:
                audio_mono = raw_data.flatten()

             # Add trailing audio from previous chunk to avoind word clipping
            if len(previous_overlap) > 0:
                combined_audio = np.concatenate((previous_overlap, audio_mono))
            else:
                combined_audio = audio_mono

            # Store end of audio chunk to overlap into next audio chunk
            previous_overlap = audio_mono[-overlap_frames:]

            # Push audio chunk into queue
            audio_queue.put(combined_audio)

            

