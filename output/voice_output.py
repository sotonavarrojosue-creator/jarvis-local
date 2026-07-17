import asyncio
import re
import tempfile
import subprocess
import os
import threading


def _shorten_for_speech(text: str, max_chars: int = 220) -> str:
    # Quitar razonamiento y markdown antes de hablar
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    text = re.sub(r"[*#_`>]|\[|\]\(.*?\)", "", text)
    text = text.strip()
    if len(text) <= max_chars:
        return text
    cutoff = text[:max_chars]
    best_cut = -1
    for sep in (". ", "\n", "; "):
        idx = cutoff.rfind(sep)
        if idx > best_cut:
            best_cut = idx
    if best_cut > 40:
        return cutoff[:best_cut + 1].strip()
    return cutoff.rstrip() + "..."


class VoiceOutput:
    def __init__(self, voice="es-MX-DaliaNeural"):
        self.enabled = False
        self.speaking = False
        self.voice = voice
        self._temp_dir = tempfile.gettempdir()
        self._player = self._detect_player()

    def _detect_player(self):
        for player in ("pw-play", "paplay", "aplay", "mpg123", "ffplay"):
            if subprocess.run(["which", player], capture_output=True).returncode == 0:
                return player
        return None

    def toggle(self):
        self.enabled = not self.enabled
        return self.enabled

    def set_voice(self, voice: str):
        self.voice = voice

    def speak(self, text: str):
        if not self.enabled or not text.strip():
            return
        short_text = _shorten_for_speech(text)
        t = threading.Thread(target=self._speak_sync, args=(short_text,), daemon=True)
        t.start()

    def _speak_sync(self, text: str):
        self.speaking = True
        try:
            self._speak_edge_tts(text)
        except Exception:
            try:
                self._speak_pyttsx3(text)
            except Exception:
                pass
        finally:
            self.speaking = False

    def _speak_edge_tts(self, text: str):
        try:
            import edge_tts
        except ImportError:
            raise RuntimeError("edge-tts not available")
        if not self._player:
            raise RuntimeError("no audio player")

        tmp = os.path.join(self._temp_dir, f"jarvis_tts_{os.getpid()}.mp3")
        try:
            loop = asyncio.new_event_loop()
            try:
                communicate = edge_tts.Communicate(text, self.voice)
                loop.run_until_complete(communicate.save(tmp))
            finally:
                loop.close()
            subprocess.run([self._player, tmp], capture_output=True)
        finally:
            if os.path.exists(tmp):
                try: os.unlink(tmp)
                except: pass

    def _speak_pyttsx3(self, text: str):
        try:
            import pyttsx3
        except ImportError:
            raise RuntimeError("pyttsx3 not available")
        engine = pyttsx3.init()
        engine.setProperty('rate', 170)
        voices = engine.getProperty('voices')
        for v in voices:
            if 'spanish' in v.name.lower() or 'mexic' in v.name.lower():
                engine.setProperty('voice', v.id)
                break
        engine.say(text)
        engine.runAndWait()
