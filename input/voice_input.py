import threading
import queue
import tempfile
import os
import wave
import time
import numpy as np

try:
    import sounddevice as sd
    HAS_SD = True
except ImportError:
    HAS_SD = False

from core.whisper_singleton import transcribe_pcm, get_whisper

MIC_LOCK = threading.Lock()

WAKE_WORDS = ["jarvis","jarviz","jarbis","jarbi","charvis","yabis","yavis","yarviz","jarvin","jabis","javis","oye","hey","harvis","harpis","jarwis","yar","jarv"]

def is_wake_word(text):
    lower = text.lower()
    for w in WAKE_WORDS:
        if w in lower:
            return True
    return False

def calibrate_noise(duration=1.0, sr=16000):
    with MIC_LOCK:
        silence = sd.rec(int(duration * sr), samplerate=sr, channels=1, dtype="int16")
        sd.wait()
    return np.abs(silence).mean()

def has_voice_energy(samples, noise_floor, threshold=3.0):
    energy = np.abs(samples).mean()
    return energy > noise_floor * threshold and energy > 300

def record_to_wav(duration=5, sample_rate=16000, noise_floor=0):
    with MIC_LOCK:
        recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype="int16")
        sd.wait()
    f = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    tmp = f.name
    f.close()
    try:
        with wave.open(tmp, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(recording.tobytes())
        return tmp
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        return ""

def transcribe_wav(wav_path, language=None):
    try:
        with wave.open(wav_path, "rb") as wf:
            frames = wf.readframes(wf.getnframes())
            sr = wf.getframerate()
        text = transcribe_pcm(frames, sample_rate=sr, language=language)
        return text
    except Exception:
        return ""
    finally:
        if os.path.exists(wav_path):
            try: os.unlink(wav_path)
            except: pass

def listen_for_voice(timeout=10, sr=16000, noise_floor=0):
    block_dur = 0.5
    block_size = int(sr * block_dur)
    silence_timeout = 3.0
    silence_start = None
    voice_detected = False
    chunks = []

    with MIC_LOCK:
        start = time.time()
        while time.time() - start < timeout:
            block = sd.rec(block_size, samplerate=sr, channels=1, dtype="int16")
            sd.wait()
            block_np = np.frombuffer(block, dtype=np.int16)

            if has_voice_energy(block_np, noise_floor):
                voice_detected = True
                silence_start = None
                chunks.append(block)
            elif voice_detected:
                if silence_start is None:
                    silence_start = time.time()
                chunks.append(block)
                if time.time() - silence_start > silence_timeout:
                    break
            else:
                silence_start = None

    if not chunks:
        return None
    audio = np.concatenate(chunks)
    f = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    tmp = f.name
    f.close()
    try:
        with wave.open(tmp, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sr)
            wf.writeframes(audio.tobytes())
        return tmp
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        return None


class VoiceInput:
    def __init__(self):
        self.listening = False
        self._wake_thread = None
        self._stop_event = threading.Event()
        self._result_queue: queue.Queue = queue.Queue()
        self.noise_floor = 0

    def start(self):
        self.listening = True
        self._stop_event.clear()
        self._wake_thread = threading.Thread(target=self._wake_loop, daemon=True)
        self._wake_thread.start()

    def stop(self):
        self.listening = False
        self._stop_event.set()
        if self._wake_thread and self._wake_thread.is_alive():
            self._wake_thread.join(timeout=2)

    def _wake_loop(self):
        if not HAS_SD:
            return
        try:
            sd.query_devices()
        except Exception:
            return

        while self.listening and not self._stop_event.is_set():
            try:
                self.noise_floor = calibrate_noise(duration=1.0)
                wav_path = listen_for_voice(timeout=10, noise_floor=self.noise_floor)
                if wav_path is None:
                    continue
                text = transcribe_wav(wav_path)
                print(f"[DEBUG wake] transcribió: '{text}'")
                if not text:
                    continue
                if is_wake_word(text):
                    self._result_queue.put("__wake__")
                    wake_wav = listen_for_voice(timeout=7, noise_floor=self.noise_floor)
                    if wake_wav:
                        cmd_text = transcribe_wav(wake_wav, language="es")
                        if cmd_text:
                            self._result_queue.put(cmd_text)
                else:
                    self._result_queue.put(text)
            except Exception:
                time.sleep(1)
                continue

    def listen(self, timeout=0.5):
        if not self.listening:
            return ""
        try:
            return self._result_queue.get(timeout=timeout)
        except queue.Empty:
            return ""

    def listen_once(self, duration=5):
        if not HAS_SD:
            return ""
        self.noise_floor = calibrate_noise(duration=1.0)
        wav = record_to_wav(duration, noise_floor=self.noise_floor)
        if not wav:
            return ""
        return transcribe_wav(wav)
