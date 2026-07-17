import wave
import tempfile
import os

_model = None

def get_whisper():
    global _model
    if _model is None:
        try:
            from faster_whisper import WhisperModel
            try:
                from core.config import SETTINGS
                size = SETTINGS.get("whisper_model", "base")
            except Exception:
                size = "base"
            _model = WhisperModel(size, device="cpu", compute_type="int8")
        except Exception as e:
            print(f"whisper load error: {e}")
    return _model

def transcribe_pcm(pcm_bytes, sample_rate=16000, language=None):
    model = get_whisper()
    if model is None:
        return ""
    tmp = None
    try:
        f = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        tmp = f.name
        with wave.open(f, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(pcm_bytes)
        f.close()
        segments, _ = model.transcribe(tmp, language=language, beam_size=5)
        return " ".join(s.text for s in segments).strip()
    except Exception as e:
        print(f"transcribe error: {e}")
        return ""
    finally:
        if tmp and os.path.exists(tmp):
            try: os.unlink(tmp)
            except: pass
