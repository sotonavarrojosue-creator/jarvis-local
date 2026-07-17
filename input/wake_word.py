import re
import threading
import queue
try:
    import speech_recognition as sr
    HAS_SR = True
except ImportError:
    HAS_SR = False


class WakeWord:
    def __init__(self, word: str = "jarvis"):
        self.word = word.lower()
        self.active = False

    def start(self) -> None:
        self.active = True
        if not HAS_SR:
            return
        threading.Thread(target=self._listen_loop, daemon=True).start()

    def stop(self) -> None:
        self.active = False

    def _listen_loop(self) -> None:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=0.5)
            while self.active:
                try:
                    audio = r.listen(source, timeout=2, phrase_time_limit=3)
                    text = r.recognize_whisper(audio, model="tiny")
                    if self.word in text.lower():
                        break
                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    continue
                except sr.RequestError:
                    continue
        self.active = False
