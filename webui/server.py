import sys, os, threading
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)
app.jinja_env.auto_reload = True

brain = None
skill_manager = None
voice_output = None
thinking = False
_state_lock = threading.Lock()

WAKE_WORDS = ["jarvis","jarviz","jarbis","jarbi","charvis","yabis","yavis","yarviz","jarvin","jabis","javis","oye","hey","harvis","harpis","jarwis","yar","jarv"]

FALLBACK_MODELS = [
    {"id": "anthropic/claude-fable-5", "name": "Claude Fable 5"},
    {"id": "anthropic/claude-sonnet-4.6", "name": "Claude Sonnet 4.6"},
    {"id": "anthropic/claude-haiku-4.5", "name": "Claude Haiku 4.5"},
    {"id": "openai/gpt-5", "name": "GPT-5"},
    {"id": "google/gemini-3-flash", "name": "Gemini 3 Flash"},
    {"id": "nvidia/nemotron-3-super-120b-a12b:free", "name": "Nemotron 3 Super (free)"},
    {"id": "meta-llama/llama-4-maverick:free", "name": "Llama 4 Maverick (free)"},
    {"id": "deepseek/deepseek-chat-v3.1:free", "name": "DeepSeek V3.1 (free)"},
]


def is_wake_word(text):
    lower = text.lower()
    return any(w in lower for w in WAKE_WORDS)


def ensure_components():
    global brain, skill_manager, voice_output
    if brain is None:
        from core.brain import Brain
        from skills.skill_manager import SkillManager
        from output.voice_output import VoiceOutput
        brain = Brain()
        skill_manager = SkillManager()
        voice_output = VoiceOutput()
        voice_output.enabled = True


def process_message(text: str) -> str:
    """Detecta skill, ejecuta y pasa por el brain. Usado por voz y chat de texto."""
    global thinking
    with _state_lock:
        thinking = True
    try:
        skill_context = ""
        skill_name = skill_manager.detect_skill(text)
        if skill_name:
            try:
                skill_context = skill_manager.execute_skill(skill_name, text)
            except Exception as e:
                skill_context = f"(la habilidad falló: {e})"
        return brain.think(text, skill_context=skill_context)
    finally:
        with _state_lock:
            thinking = False


@app.after_request
def no_cache(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/status")
def status():
    ensure_components()
    stats = {}
    try:
        import psutil
        stats = {
            "cpu": psutil.cpu_percent(interval=None),
            "ram": psutil.virtual_memory().percent,
            "disk": psutil.disk_usage("/").percent,
        }
    except Exception:
        pass
    return jsonify({
        "speaking": voice_output.speaking if voice_output else False,
        "voice_enabled": voice_output.enabled if voice_output else False,
        "thinking": thinking,
        "has_key": brain.has_api_key(),
        "model": brain.model,
        "stats": stats,
    })


@app.route("/voice/toggle", methods=["POST"])
def toggle_voice():
    ensure_components()
    state = voice_output.toggle()
    return jsonify({"enabled": state})


# ---------- Ajustes: API key + modelo ----------

@app.route("/api/settings", methods=["GET"])
def get_settings():
    ensure_components()
    from core.config import SETTINGS
    key = brain._api_key
    masked = (key[:8] + "…" + key[-4:]) if len(key) > 14 else ("configurada" if key else "")
    return jsonify({
        "model": brain.model,
        "has_key": bool(key),
        "api_key_masked": masked,
        "voice": SETTINGS.get("voice", "es-MX-DaliaNeural"),
    })


@app.route("/api/settings", methods=["POST"])
def set_settings():
    ensure_components()
    data = request.get_json(silent=True) or {}
    api_key = data.get("api_key")
    model = data.get("model")
    voice = data.get("voice")

    if api_key is not None and api_key.strip():
        brain.set_api_key(api_key.strip())
    if model is not None and model.strip():
        brain.set_model(model.strip())
    if voice is not None and voice.strip():
        from core.config import update_settings
        update_settings(voice=voice.strip())
        voice_output.set_voice(voice.strip())

    return jsonify({"ok": True, "model": brain.model, "has_key": brain.has_api_key()})


@app.route("/api/settings/test", methods=["POST"])
def test_settings():
    """Prueba la API key y el modelo actual con una petición mínima."""
    ensure_components()
    if not brain.has_api_key():
        return jsonify({"ok": False, "error": "No hay API key configurada"})
    try:
        r = brain.client.chat.completions.create(
            model=brain.model,
            messages=[{"role": "user", "content": "responde solo: ok"}],
            max_tokens=5,
        )
        content = (r.choices[0].message.content or "").strip()
        return jsonify({"ok": True, "reply": content})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


@app.route("/api/models")
def list_models():
    """Lista de modelos de OpenRouter (con fallback estático si no hay red)."""
    try:
        import requests
        r = requests.get("https://openrouter.ai/api/v1/models", timeout=8)
        r.raise_for_status()
        data = r.json().get("data", [])
        models = sorted(
            ({"id": m["id"], "name": m.get("name", m["id"])} for m in data if m.get("id")),
            key=lambda m: m["name"].lower(),
        )
        if models:
            return jsonify({"models": models, "source": "openrouter"})
    except Exception:
        pass
    return jsonify({"models": FALLBACK_MODELS, "source": "fallback"})


# ---------- Chat de texto ----------

@app.route("/api/chat", methods=["POST"])
def api_chat():
    ensure_components()
    data = request.get_json(silent=True) or {}
    text = (data.get("message") or "").strip()
    if not text:
        return jsonify({"response": ""})
    response = process_message(text)
    speak = bool(data.get("speak", False))
    if speak and voice_output and voice_output.enabled:
        voice_output.speak(response)
    try:
        from obsidian_logger import log_chat
        log_chat(text, response)
    except Exception:
        pass
    return jsonify({"response": response})


# ---------- Transcripción de voz ----------

@app.route("/api/transcribe", methods=["POST"])
def api_transcribe():
    ensure_components()

    from core.whisper_singleton import transcribe_pcm
    import base64

    raw = request.get_data()
    sample_rate = int(request.headers.get("X-Sample-Rate", "48000"))
    is_base64 = request.headers.get("X-Base64", "false") == "true"

    if is_base64:
        try:
            pcm_bytes = base64.b64decode(raw)
        except Exception:
            return jsonify({"text": "", "wake": False, "response": ""})
    else:
        pcm_bytes = raw

    if len(pcm_bytes) < 3200:
        return jsonify({"text": "", "wake": False, "response": ""})

    awake = request.headers.get("X-Awake", "false") == "true"
    text = transcribe_pcm(pcm_bytes, sample_rate=sample_rate, language=("es" if awake else None))
    if not text:
        return jsonify({"text": "", "wake": False, "response": ""})

    is_wake = is_wake_word(text.lower().strip())

    if awake:
        response = process_message(text)
        if voice_output and voice_output.enabled:
            voice_output.speak(response)
        return jsonify({"text": text, "wake": False, "response": response})

    return jsonify({"text": text, "wake": is_wake, "response": ""})


if __name__ == "__main__":
    print("JARVIS WebUI http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
