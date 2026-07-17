import os
import json
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

_SETTINGS_PATH = BASE_DIR / "data" / "config" / "settings.json"

_DEFAULTS = {
    "model": "nvidia/nemotron-3-super-120b-a12b:free",
    "api_key": "",
    "voice": "es-MX-DaliaNeural",
    "theme": "neon",
    "language": "es",
}


def load_settings() -> dict[str, str]:
    if _SETTINGS_PATH.exists():
        try:
            with _SETTINGS_PATH.open("r", encoding="utf-8") as f:
                return {**_DEFAULTS, **json.load(f)}
        except Exception:
            return dict(_DEFAULTS)
    return dict(_DEFAULTS)


def save_settings(settings: dict[str, str]) -> None:
    _SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(_SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)


SETTINGS = load_settings()


def update_settings(**kwargs) -> dict[str, str]:
    """Actualiza settings en memoria y en disco. Ignora claves con valor None."""
    for k, v in kwargs.items():
        if v is not None:
            SETTINGS[k] = v
    save_settings(SETTINGS)
    return SETTINGS


def get_api_key() -> str:
    """API key con prioridad: settings de la app > variable de entorno."""
    return SETTINGS.get("api_key", "") or os.getenv("OPENROUTER_API_KEY", "")


def get_model() -> str:
    return os.getenv("JARVIS_MODEL") or SETTINGS.get("model", _DEFAULTS["model"])


# Compatibilidad con módulos que importan las constantes
OPENROUTER_API_KEY = get_api_key()
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

DEFAULT_MODEL = get_model()
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
USER_NAME = os.getenv("USER_NAME", "Aaron")
JARVIS_VOICE = os.getenv("JARVIS_VOICE") or SETTINGS.get("voice", "es-MX-DaliaNeural")

MEMORY_DIR = BASE_DIR / "data" / "memory"
NOTES_DIR = BASE_DIR / "data" / "notes"
OBSIDIAN_DIR = Path(os.getenv("JARVIS_OBSIDIAN_DIR", str(BASE_DIR / "data" / "obsidian")))
OBSIDIAN_LOG_DIR = OBSIDIAN_DIR / "logs"
CONFIG_DIR = BASE_DIR / "data" / "config"

MAX_MEMORY_MESSAGES = 50

MISSING_KEYS: list[str] = []
if not get_api_key():
    MISSING_KEYS.append("OPENROUTER_API_KEY (OpenRouter)")
